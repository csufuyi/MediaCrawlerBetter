#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝/天猫 商品评论抓取器（mtop 签名接口版）

背景 / 为什么这样做
-------------------
MediaCrawler 本身不支持淘宝。淘宝商品「评论」不在首屏 HTML 里，而是走一个
单独的、需要签名的 mtop 接口 (mtop.taobao.rate.detaillist.get)。直接滚动抓
渲染出来的评论 DOM 会：
  1) 在海外 IP 上被商品详情页的「此商品不可运送」地域墙直接挡死；
  2) 翻页时高频戳评论接口，触发滑块/风控。

本工具改用 MediaCrawler 同款思路：**用登录态 cookie 自己算 mtop 签名，直接调
JSON 评论接口**。数据结构化、请求量小，并且绕开了详情页的地域拦截
（评论接口 h5api.m.taobao.com 本身不做地域限制）。

签名算法
--------
  sign = md5(token + "&" + t + "&" + appKey + "&" + data)
  token = cookie `_m_h5_tk` 的第一段（'_' 之前）
  appKey = 12574478 (h5 通用)
第一次请求通常返回 FAIL_SYS_TOKEN_*（token 为空/过期）并通过 Set-Cookie 下发
新的 `_m_h5_tk`，用它重算签名再请求一次即可。本工具自动完成这个「两段握手」。

如何拿 cookie
-------------
1. 用你**已登录**淘宝的 Chrome 打开任意淘宝页面；
2. DevTools → Network → 找任意一条发往 h5api.m.taobao.com 或 .taobao.com 的
   请求 → 右键 Copy → Copy request headers，或直接复制该请求的 `Cookie:` 头；
3. 把整段 cookie 值粘贴进 taobao_cookies.txt（与本脚本同目录），或用 --cookie-file 指定。
   （必须包含 httpOnly 的登录 cookie，如 cookie2 / _tb_token_ / sgcookie / unb 等，
    所以要从「请求头」里复制，不能用 document.cookie。）

用法
----
  uv run tools/taobao_rate.py --item-id 627338948826 --max-pages 5
  uv run tools/taobao_rate.py --item-ids 627338948826,621840569465 --sleep 3 --out data/taobao_rates.xlsx

⚠️ 仅供个人学习/研究。请控制频率（默认单线程 + 每页 sleep）、只抓一级评论、
   遇到风控/验证码就停下手动处理，勿大规模抓取冲击平台。
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from typing import Dict, List, Optional

import pandas as pd

try:
    # curl_cffi 能模拟 Chrome 的 TLS 指纹，是从 Python 过淘宝 RGV587 风控的关键。
    from curl_cffi import requests as cffi_requests
    _HAS_CFFI = True
except ImportError:  # 兜底：没装 curl_cffi 时退回 httpx（更容易被风控挡）
    import httpx
    _HAS_CFFI = False

H5_HOST = "https://h5api.m.taobao.com/h5"
APP_KEY = "12574478"
RATE_API = "mtop.taobao.rate.detaillist.get"
RATE_VER = "6.0"

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
)


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _get_token(client) -> str:
    """从 client 的 cookie jar 里取 _m_h5_tk 的第一段。"""
    raw = client.cookies.get("_m_h5_tk", "") or ""
    return raw.split("_")[0] if raw else ""


def _mtop_request(client, api: str, ver: str, data: str) -> Dict:
    """单次带签名的 mtop 请求。"""
    t = str(int(time.time() * 1000))
    token = _get_token(client)
    sign = _md5("&".join([token, t, APP_KEY, data]))
    params = {
        "jsv": "2.6.1",
        "appKey": APP_KEY,
        "t": t,
        "sign": sign,
        "api": api,
        "v": ver,
        "type": "originaljson",
        "dataType": "json",
        "data": data,
    }
    url = f"{H5_HOST}/{api}/{ver}/"
    resp = client.get(url, params=params)
    # httpx 会自动把 Set-Cookie（含新的 _m_h5_tk）并入 client.cookies
    try:
        return resp.json()
    except Exception:
        return {"ret": [f"HTTP-{resp.status_code}"], "raw": resp.text[:300]}


def call_rate(client, item_id: str, page_no: int, page_size: int) -> Dict:
    """调评论接口，自动完成 token 两段握手。"""
    data = json.dumps(
        {"auctionNumId": str(item_id), "pageNo": page_no, "pageSize": page_size},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    res = _mtop_request(client, RATE_API, RATE_VER, data)
    ret = "".join(res.get("ret", []))
    if "FAIL_SYS_TOKEN" in ret or "令牌" in ret:
        # 第一次拿到新 _m_h5_tk，重签再来一次
        res = _mtop_request(client, RATE_API, RATE_VER, data)
    return res


def parse_rates(res: Dict) -> List[Dict]:
    """从接口返回里抽出评论正文等字段，兼容多种字段命名。"""
    d = res.get("data", {}) or {}
    rate_list = d.get("rateList") or d.get("rateDetailList") or []
    rows = []
    for r in rate_list:
        append = r.get("appendList") or r.get("append") or []
        append_txt = ""
        if isinstance(append, list) and append:
            append_txt = " || ".join(
                (a.get("appendFeedback") or a.get("feedback") or "") for a in append
            )
        elif isinstance(append, dict):
            append_txt = append.get("appendFeedback") or append.get("feedback") or ""
        rows.append(
            {
                "rate_id": r.get("id") or r.get("rateId"),
                "content": r.get("feedback") or r.get("rateContent") or "",
                "append": append_txt,
                "sku": r.get("auctionSku") or r.get("skuMap") or "",
                "date": r.get("feedbackDate") or r.get("rateDate") or "",
                "user": r.get("reduceUserNick") or r.get("userNick") or "",
                "useful": r.get("useful") or r.get("usefulVoteCount") or 0,
                "pics": len(r.get("photos") or r.get("pics") or []),
            }
        )
    return rows


def get_paginator_last(res: Dict) -> Optional[int]:
    d = res.get("data", {}) or {}
    pag = d.get("paginator") or {}
    return pag.get("lastPage") or pag.get("totalPage")


def load_cookie(cookie_file: str) -> str:
    if not os.path.exists(cookie_file):
        sys.exit(
            f"[!] 找不到 cookie 文件: {cookie_file}\n"
            f"    请把已登录淘宝的请求 Cookie 头粘贴进该文件（详见脚本顶部说明）。"
        )
    with open(cookie_file, "r", encoding="utf-8") as f:
        cookie = f.read().strip()
    if not cookie:
        sys.exit(f"[!] cookie 文件为空: {cookie_file}")
    return cookie


def build_client(cookie_str: str):
    """构造带登录 cookie 的会话；优先用 curl_cffi 模拟 Chrome 指纹以过风控。"""
    jar = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            jar[k.strip()] = v.strip()
    headers = {
        "user-agent": DEFAULT_UA,
        "referer": "https://detail.tmall.com/",
        "origin": "https://detail.tmall.com",
        "accept": "application/json",
        "accept-language": "zh-CN,zh;q=0.9",
    }
    if _HAS_CFFI:
        client = cffi_requests.Session(impersonate="chrome", timeout=20.0)
        client.headers.update(headers)
        for k, v in jar.items():
            client.cookies.set(k, v)
        return client
    client = httpx.Client(headers=headers, cookies=jar, timeout=20.0)
    return client


def main():
    ap = argparse.ArgumentParser(description="淘宝/天猫商品评论抓取（mtop 签名接口）")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--item-id", help="单个商品 ID")
    g.add_argument("--item-ids", help="多个商品 ID，逗号分隔")
    ap.add_argument("--max-pages", type=int, default=5, help="每个商品最多抓多少页（默认 5）")
    ap.add_argument("--page-size", type=int, default=20, help="每页评论数（默认 20）")
    ap.add_argument("--sleep", type=float, default=3.0, help="翻页间隔秒数，降速防风控（默认 3）")
    ap.add_argument(
        "--cookie-file",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "taobao_cookies.txt"),
        help="cookie 文件路径（默认 tools/taobao_cookies.txt）",
    )
    ap.add_argument("--out", default="data/taobao_rates.xlsx", help="输出 Excel 路径")
    args = ap.parse_args()

    item_ids = [args.item_id] if args.item_id else [x.strip() for x in args.item_ids.split(",") if x.strip()]
    cookie_str = load_cookie(args.cookie_file)
    client = build_client(cookie_str)
    print(f"[引擎] {'curl_cffi(模拟Chrome指纹)' if _HAS_CFFI else 'httpx(易被风控，建议装 curl_cffi)'}")

    all_rows: List[Dict] = []
    for item_id in item_ids:
        print(f"\n=== 商品 {item_id} ===")
        for page in range(1, args.max_pages + 1):
            res = call_rate(client, item_id, page, args.page_size)
            ret = "".join(res.get("ret", []))
            if "SUCCESS" not in ret.upper():
                print(f"  第 {page} 页返回异常: {ret or res.get('ret')} —— 停止该商品")
                if any(k in ret for k in ("FAIL_SYS_ILLEGAL", "RGV587", "令牌", "验证", "TOKEN")):
                    print("  ⚠️ 疑似触发风控/验证码，请稍后再试或人工在浏览器过验证。")
                break
            rows = parse_rates(res)
            for r in rows:
                r["item_id"] = item_id
            all_rows.extend(rows)
            last = get_paginator_last(res)
            print(f"  第 {page} 页: +{len(rows)} 条 (累计 {len(all_rows)})" + (f" / 共约 {last} 页" if last else ""))
            if not rows or (last and page >= last):
                break
            time.sleep(args.sleep)  # 降速，单线程翻页

    if not all_rows:
        print("\n未抓到任何评论。检查 cookie 是否有效/已登录，或该商品是否有评论。")
        return
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    df = pd.DataFrame(all_rows)[
        ["item_id", "rate_id", "content", "append", "sku", "date", "user", "useful", "pics"]
    ]
    df.to_excel(args.out, index=False)
    print(f"\n✅ 共 {len(df)} 条评论 → {args.out}")


if __name__ == "__main__":
    main()
