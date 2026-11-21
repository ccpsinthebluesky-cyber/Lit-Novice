// SPDX-License-Identifier: MIT
// Copyright (c) 2026 張明泰@長流 (Ming-Tai Chang)
// Project: Lit-Novice (AI協助工具：文學小白便利貼)
// Repository: https://github.com/ccpsinthebluesky-cyber/Lit-Novice

const SEP = '\u200B'; // 分隔符 (Zero Width Space)，示意符號「│」
const CON = '\u2060'; // 連接符 (Word Joiner)，示意符號「+」

// 涵蓋 CJK 基本漢字、擴展區 A–I、相容漢字及中文圈零「〇」(U+3007)
const CJK_RE = /[\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u{20000}-\u{2FA1F}\u{30000}-\u{323AF}]/u;
const WS_RE = /\s/u; // 涵蓋半形空白、全形空白 (\u3000)、Tab 與換行

// 嚴格對應白皮書表一之三大類中文標點白名單（含橫排與直排對應形式，排除 Emoji 與貨幣符號）
const CJK_OPENING = new Set([
    ...'「『\u201C\u2018（《〈【〖〔［｛', // 橫排前導開頭符號
    ...'﹁﹃︵︽︿︻︗︹﹇︷'               // 直排前導開頭符號
]);
const CJK_CLOSING = new Set([
    ...'」』\u201D\u2019）》〉】〗〕］｝', // 橫排後置結尾符號
    ...'﹂﹄︶︾﹀︼︘︺﹈︸'               // 直排後置結尾符號
]);
const CJK_ATTACHED = new Set([
    ...'。，、；：？！—…～·・／',           // 橫排句讀與依附符號
    ...'︒︐︑︔︓︖︕︱︙'                  // 直排句讀與依附符號
]);
const CJK_SYMBOLS = new Set([...CJK_OPENING, ...CJK_CLOSING, ...CJK_ATTACHED]);

function isCjkChar(ch) {
    return CJK_RE.test(ch);
}

function isCjkOpening(ch) {
    return CJK_OPENING.has(ch);
}

function isCjkSymbol(ch) {
    return CJK_SYMBOLS.has(ch);
}

function removeLitNovice(text) {
    // 一鍵還原：清除所有分隔符與連接符，恢復純淨原文
    return text.replace(/[\u200B\u2060]/g, '');
}

function applyLitNovice(text) {
    // 步驟 1：清空既有隱藏空白字元（使用 Array.from 確保擴展漢字不破字）
    const chars = Array.from(removeLitNovice(text));
    const out = [];

    // 步驟 2：依雙層優先級規則處理縫隙
    for (let i = 0; i < chars.length; i++) {
        const curr = chars[i];
        out.push(curr);
        if (i + 1 >= chars.length) break;
        const nxt = chars[i + 1];

        // 豁免規則 A：全形空白、半形空白與換行控制字元一律跳過
        if (WS_RE.test(curr) || WS_RE.test(nxt)) continue;

        const cValid = isCjkChar(curr) || isCjkSymbol(curr);
        const nValid = isCjkChar(nxt) || isCjkSymbol(nxt);

        // 豁免規則 B：前後皆非漢字或表一標點（如連續英數、半形網址、貨幣符號）一律跳過
        if (!cValid && !nValid) continue;

        // 【第一層：最高優先例外（處理前導開頭符號）】
        if (isCjkOpening(curr)) {
            out.push(CON); // 開頭符號右縫隙（含「『 連續開頭與（AI）首字）➔ 連接符 (+)
        } else if (isCjkOpening(nxt)) {
            out.push(SEP); // 非開頭符號接開頭符號左縫隙 ➔ 分隔符 (│)
        }
        // 【第二層：基礎四條規則（處理其餘文字與結尾／句讀依附符號）】
        else {
            // 右側為表一標點（如 第1條，、意」、——）用連接符 (+)；右側為文字用分隔符 (│)
            out.push(isCjkSymbol(nxt) ? CON : SEP);
        }
    }

    return out.join('');
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { applyLitNovice, removeLitNovice };
}
