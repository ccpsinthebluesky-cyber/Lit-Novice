# SPDX-License-Identifier: MIT
# Copyright (c) 2026 張明泰@長流 (Ming-Tai Chang)
# Project: Lit-Novice (AI協助工具：文學小白便利貼)
# Repository: https://github.com/ccpsinthebluesky-cyber/Lit-Novice

import re

SEP = "\u200B"  # 分隔符 (Zero Width Space)，示意符號「│」
CON = "\u2060"  # 連接符 (Word Joiner)，示意符號「+」

# 涵蓋 CJK 基本漢字、擴展區 A–I、相容漢字及中文圈零「〇」(U+3007)
CJK_RE = re.compile(
    r"[\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF"
    r"\U00020000-\U0002FA1F\U00030000-\U000323AF]"
)

# 嚴格對應白皮書表一之三大類中文標點白名單（含橫排與直排對應形式，排除 Emoji 與貨幣符號）
CJK_OPENING = frozenset(
    "「『\u201C\u2018（《〈【〖〔［｛"   # 橫排前導開頭符號
    "﹁﹃︵︽︿︻︗︹﹇︷"               # 直排前導開頭符號
)
CJK_CLOSING = frozenset(
    "」』\u201D\u2019）》〉】〗〕］｝"   # 橫排後置結尾符號
    "﹂﹄︶︾﹀︼︘︺﹈︸"               # 直排後置結尾符號
)
CJK_ATTACHED = frozenset(
    "。，、；：？！—…～·・／"              # 橫排句讀與依附符號
    "︒︐︑︔︓︖︕︱︙"                   # 直排句讀與依附符號
)
CJK_SYMBOLS = CJK_OPENING | CJK_CLOSING | CJK_ATTACHED


def is_cjk_char(ch: str) -> bool:
    """判定是否為中文漢字（含圈零「〇」）"""
    return bool(CJK_RE.match(ch))


def is_cjk_opening(ch: str) -> bool:
    """判定是否為表一所列前導開頭標點（含橫直排）"""
    return ch in CJK_OPENING


def is_cjk_symbol(ch: str) -> bool:
    """判定是否為表一所列中文標點白名單（排除 ASCII、Emoji 與貨幣符號）"""
    return ch in CJK_SYMBOLS


def remove_lit_novice(text: str) -> str:
    """一鍵還原：清除所有分隔符與連接符，恢復純淨原文"""
    return text.replace(SEP, "").replace(CON, "")


def apply_lit_novice(text: str) -> str:
    """依雙層優先級規則，於中文漢字與標點縫隙精準配置分隔符與連接符"""
    # 步驟 1：清空既有隱藏空白字元（保留所有原生全形／半形空白與換行）
    clean = remove_lit_novice(text)
    out = []

    # 步驟 2：依雙層優先級規則處理縫隙
    for i, curr in enumerate(clean):
        out.append(curr)
        if i + 1 >= len(clean):
            break
        nxt = clean[i + 1]

        # 豁免規則 A：全形空白 (\u3000)、半形空白與換行控制字元一律跳過
        if curr.isspace() or nxt.isspace():
            continue

        c_valid = is_cjk_char(curr) or is_cjk_symbol(curr)
        n_valid = is_cjk_char(nxt) or is_cjk_symbol(nxt)

        # 豁免規則 B：前後皆非漢字或表一標點（如連續英數、半形網址、貨幣符號）一律跳過
        if not c_valid and not n_valid:
            continue

        # 【第一層：最高優先例外（處理前導開頭符號）】
        if is_cjk_opening(curr):
            out.append(CON)  # 開頭符號右縫隙（含「『 連續開頭與（AI）首字）➔ 連接符 (+)
        elif is_cjk_opening(nxt):
            out.append(SEP)  # 非開頭符號接開頭符號左縫隙 ➔ 分隔符 (│)
        # 【第二層：基礎四條規則（處理其餘文字與結尾／句讀依附符號）】
        else:
            # 右側為表一標點（如 第1條，、意」、——）用連接符 (+)；右側為文字用分隔符 (│)
            out.append(CON if is_cjk_symbol(nxt) else SEP)

    return "".join(out)


if __name__ == "__main__":
    sample = "神風橫掃天雷現"
    processed = apply_lit_novice(sample)
    print("原文：", sample)
    print("視覺透視：", processed.replace(SEP, "│").replace(CON, "+"))
    print("還原驗證：", remove_lit_novice(processed) == sample)
