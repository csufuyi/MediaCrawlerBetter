"""
把旧版 jsonl 数据迁移为上游匿名化格式，使其能与新采集的数据按 creator_hash 关联分析。

- user_id(抖音 uid / 小红书 user_id) -> creator_hash，算法与 tools/user_hash.anonymize_user_id 一致
- 抖音 creator_creators 里的 user_id 实为 sec_uid，先借内容/评论数据映射回 uid 再哈希
- nickname 走 mask_nickname 脱敏
- 删除 sec_uid / short_user_id / user_unique_id / avatar / user_signature 等原始身份字段
- 其余字段(含 ip_location)原样保留

用法：
    uv run python tools/migrate_legacy_user_hash.py            # 迁移 data/ 下所有 *.jsonl，原文件先备份
    uv run python tools/migrate_legacy_user_hash.py --dry-run  # 只统计不写入
"""

import argparse
import glob
import json
import os
import shutil
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.user_hash import anonymize_user_id, mask_nickname  # noqa: E402

DROP_FIELDS = {"user_id", "sec_uid", "short_user_id", "user_unique_id", "avatar", "user_signature"}


def iter_records(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def build_dy_sec_uid_map(data_dir):
    mapping = {}
    for path in glob.glob(os.path.join(data_dir, "douyin", "jsonl", "*.jsonl")):
        for rec in iter_records(path):
            if rec.get("sec_uid") and rec.get("user_id"):
                mapping[rec["sec_uid"]] = rec["user_id"]
    return mapping


def convert(rec, sec_uid_map, is_dy_creator):
    if "user_id" not in rec:
        return rec, False
    raw_id = rec["user_id"]
    if is_dy_creator:
        raw_id = sec_uid_map.get(raw_id, raw_id)
    out = {}
    for key, value in rec.items():
        if key == "user_id":
            out["creator_hash"] = anonymize_user_id(raw_id)
        elif key == "nickname":
            out["nickname"] = mask_nickname(value)
        elif key not in DROP_FIELDS:
            out[key] = value
    return out, True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.data_dir, "*", "jsonl", "*.jsonl")))
    sec_uid_map = build_dy_sec_uid_map(args.data_dir)
    backup_dir = f"{args.data_dir.rstrip('/')}_raw_backup_{datetime.now():%Y%m%d%H%M%S}"

    unmapped = set()
    for path in files:
        is_dy_creator = os.sep + "douyin" + os.sep in path and "_creators_" in os.path.basename(path)
        records, changed = [], 0
        for rec in iter_records(path):
            if is_dy_creator and rec.get("user_id") and rec["user_id"] not in sec_uid_map:
                unmapped.add(rec["user_id"])
            new, did = convert(rec, sec_uid_map, is_dy_creator)
            records.append(new)
            changed += did
        print(f"{path}: {len(records)} 条，转换 {changed} 条")
        if args.dry_run or not changed:
            continue
        dst = os.path.join(backup_dir, os.path.relpath(path, args.data_dir))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(path, dst)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        os.replace(tmp, path)

    if unmapped:
        print(f"警告：{len(unmapped)} 个抖音创作者 sec_uid 找不到对应 uid，已直接对 sec_uid 哈希，无法与内容关联")
    if not args.dry_run and os.path.isdir(backup_dir):
        print(f"原始文件已备份到 {backup_dir}")


if __name__ == "__main__":
    main()
