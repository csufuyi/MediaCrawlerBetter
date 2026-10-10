# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/config/dy_config.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# Douyin platform configuration
PUBLISH_TIME_TYPE = 0

# Specify DY video URL list (supports multiple formats)
# Supported formats:
# 1. Full video URL: "https://www.douyin.com/video/7525538910311632128"
# 2. URL with modal_id: "https://www.douyin.com/user/xxx?modal_id=7525538910311632128"
# 3. The search page has modal_id: "https://www.douyin.com/root/search/python?modal_id=7525538910311632128"
# 4. Short link: "https://v.douyin.com/drIPtQ_WPWY/"
# 5. Pure video ID: "7280854932641664319"
DY_SPECIFIED_ID_LIST = [
    "https://www.douyin.com/video/7525538910311632128",
    "https://v.douyin.com/drIPtQ_WPWY/",
    "https://www.douyin.com/user/MS4wLjABAAAATJPY7LAlaa5X-c8uNdWkvz0jUGgpw4eeXIwu_8BhvqE?from_tab_name=main&modal_id=7525538910311632128",
    "7202432992642387233",
    # ........................
]

# Specify DY creator URL list (supports full URL or sec_user_id)
# Supported formats:
# 1. Complete creator homepage URL: "https://www.douyin.com/user/MS4wLjABAAAATJPY7LAlaa5X-c8uNdWkvz0jUGgpw4eeXIwu_8BhvqE?from_tab_name=main"
# 2. sec_user_id: "MS4wLjABAAAATJPY7LAlaa5X-c8uNdWkvz0jUGgpw4eeXIwu_8BhvqE"
DY_CREATOR_ID_LIST = [
    "MS4wLjABAAAADrNxjt_P48HLfgQiY0BZ6-Cqk25XIeZGNe2wrGNsk-Zo7czCYpa3x0PE-poUDFQk",
    "MS4wLjABAAAASUIQGPRxb04qNlOcWJzcFLCnkv19l57YNpsN6uex7TDvU3_RdcSdqNJWyWYr8WbZ",
    "MS4wLjABAAAADBH6ustzH06uVF7wlUuFrMtol3M00w2tiExHFiToH59a0XEzHColZhofi7NNgPIk",
    "MS4wLjABAAAAn5abWkm-w9dHTJnFGmWsJsoG1CNeL67knBsvZK82eU_dr3bCS7Id4ExZ3XNNlRFC",
    "MS4wLjABAAAArbOYV2jRdxQJmbqtx-Mj19trbEs4n6-Fi9_WvA0d_bh4UaWjDFy7e84GY5pEPo7T",
    "MS4wLjABAAAADxvYQcAFHmRosLiAqSuEDkgfkBSDdWd3YPRqjvRqsQ8",
    "MS4wLjABAAAAcY53Y4AODdowWHKUAYHI-xt-CjpN-nT3FKwpTiePIaY",
    "MS4wLjABAAAAN--TsDIJuPNWIHEqnb8_d1ar8wa43H6gaw00UHIkzsMRzvDfkCA8-s7QQxWKd4QR",
    "MS4wLjABAAAAoOCnWrBNO-YinZB7_Lo1xRh0hZnVqgWpjOoCWE5qPzY",
    "MS4wLjABAAAAqwzcuLAB6VYrmOsHo5QHPgvNOfxIwU_cUBRuIJsoOLQ",
    "MS4wLjABAAAA694lpeoo0Nrn0tv8caqHhmoebNPiWQwnp1QgCGqdIjM",
    "MS4wLjABAAAAFmcLzmffgtF90xQAUdKpP-tGlVbHktZ0tcHqKgQMT6A",
    "MS4wLjABAAAAwOn05DRoEaKabjcOLl53ddLPg1ZlqxR1l2AA-but7cY",
    "MS4wLjABAAAADDbMEqAAAw1og7vvUIgu4bL1e_YItzvKQsrcv5lHNOk",
    "MS4wLjABAAAA_1_Oi-CzU4kUjnjLl-PjwXbStIZ6aaj7N6Vrg2lyNrY",
    "MS4wLjABAAAAl2Y6wbMnCmqpZwue0DC0wyhFCwrc8QeMD5itlUQUs5FUzU81XIk2dp99NDIKbx4d",
    "MS4wLjABAAAAr53Z3cXgtHEFeS7jZgxz7yrdAa7_P4A95CR_mzsZ3FqRRxqNqBrXpne_h0Fu1vh3",
    "MS4wLjABAAAAVPxB6Aofc3CqwM3bQfXGOiSvmQHot8OaxI3Sk4pxyaYXnzjFvSW3tc-NHxWtTXmw",
    "MS4wLjABAAAAco4v7P0Gvt4IpH2lWgpRb0HehEbGGLMFwszfgvUlqi5yjm-p3MnYfuCPw6e0Eqy6",
    "MS4wLjABAAAAcx1VEn6dfM-40yGtCBLB0fCqWuVfI6oFBAPmrz-MDv8",
    "MS4wLjABAAAAN--TsDIJuPNWIHEqnb8_d1ar8wa43H6gaw00UHIkzsMRzvDfkCA8-s7QQxWKd4QR",
    "MS4wLjABAAAAmlA_v1CUolkx1dAN0WhKyqieUXFB-3BySp8Bl2GjsOa1Gx0Y-EuIvemY3s4ZfVjr",
]


# POC 补丁：creator 模式只取账号画像（fans/desc/ip_location/videos_count），
# 跳过 get_all_user_aweme_posts 的全量作品爬取。
# 原因：该函数是 while has_more 无上限循环，且每条作品 +6s 休眠；
# 实测周黑鸭官方旗舰店 videos_count=1502 → 单账号约 2.8 小时，22 个账号要跑几天。
# CRAWLER_MAX_NOTES_COUNT 只约束 search 路径，对 creator 无效。
DY_CREATOR_INFO_ONLY = True
