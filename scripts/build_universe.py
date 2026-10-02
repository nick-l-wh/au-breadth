"""建立澳洲股票池（ASX 普通股）。可單獨執行，也會被 download_prices.py 自動呼叫。

輸入：ASX 官網「ASX Listed Companies」CSV
      https://www.asx.com.au/asx/research/ASXListedCompanies.csv
      格式：第 1 行是標題文字，第 2 行起為「Company name, ASX code, GICS industry group」
輸出：data/universe.csv（入選）、data/universe_excluded.csv（被排除者與原因，供你檢查）
用法：python scripts/build_universe.py [data/ASXListedCompanies.csv]
"""
import csv
import re
import sys
from pathlib import Path

import pandas as pd

OUT = Path("data/universe.csv")
OUT_EXCL = Path("data/universe_excluded.csv")

# 名稱中帶有這些字樣的視為基金／結構性商品，不是普通股
FUND_PATTERN = re.compile(
    r"\b(?:ETF|ETFS|ETC|ETP|ISHARES|SPDR|VANECK|BETASHARES|GLOBAL X|VANGUARD|"
    r"EXCHANGE TRADED|INDEX FUND|HEDGED|BITCOIN|ETHEREUM|MSCI|NASDAQ|S&P)\b", re.I)


def read_asx_csv(src):
    with open(src, newline="", encoding="utf-8-sig", errors="replace") as f:
        rows = list(csv.reader(f))
    hdr = next((i for i, r in enumerate(rows) if r and r[0].strip().lower() == "company name"), None)
    if hdr is None:
        raise ValueError(f"找不到標題列（Company name, ASX code, GICS industry group），前 2 行：{rows[:2]}")
    cols = [c.strip() for c in rows[hdr]]
    df = pd.DataFrame([r for r in rows[hdr + 1:] if len(r) >= 3], columns=cols[:3] if len(cols) >= 3 else cols)
    return df.rename(columns={cols[0]: "name", cols[1]: "code", cols[2]: "gics"})


def build(src):
    df = read_asx_csv(src)
    for c in ("name", "code", "gics"):
        df[c] = df[c].astype(str).str.strip()
    df["code"] = df["code"].str.upper()
    df["reason"] = ""
    df.loc[~df["code"].str.fullmatch(r"[A-Z0-9]{3}"), "reason"] = "代碼不是 3 碼（混合證券、權證等）"
    m = df["reason"].eq("") & df["gics"].str.lower().str.startswith("not applic")
    df.loc[m, "reason"] = "GICS 為 Not Applic（基金、信託、結構性商品）"
    m = df["reason"].eq("") & df["name"].str.contains(FUND_PATTERN)
    df.loc[m, "reason"] = "名稱含 ETF／指數基金字樣"
    df.loc[df["reason"].eq("") & df.duplicated("code", keep="first"), "reason"] = "代碼重複"

    ok = df[df["reason"].eq("")].copy()
    ok["ticker"] = ok["code"] + ".AX"
    ok = ok[["ticker", "code", "name", "gics"]].sort_values("code")
    OUT.parent.mkdir(exist_ok=True)
    ok.to_csv(OUT, index=False, encoding="utf-8-sig")
    df[df["reason"].ne("")][["code", "name", "gics", "reason"]].to_csv(OUT_EXCL, index=False, encoding="utf-8-sig")

    print(f"名單共 {len(df)} 筆，入選普通股 {len(ok)} 隻")
    print(df[df["reason"].ne("")]["reason"].value_counts().to_string())
    print(f"被排除的名單已存到 {OUT_EXCL}，建議抽查是否有誤排除")
    return ok


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "data/ASXListedCompanies.csv")
