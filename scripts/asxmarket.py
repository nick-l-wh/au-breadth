"""雪梨市場時間工具：避免把「盤中未收盤」的當日 K 線當成完整資料存下來或拿去計算。

ASX 交易時間 10:00–16:00（雪梨本地時間，含 16:10 左右的收盤競價），
Yahoo 收盤資料穩定約在 16:45 之後。使用 Australia/Sydney 時區，自動處理夏令時間
（每年 10 月第一個週日開始、4 月第一個週日結束）。
規則：平日雪梨 10:00–16:44 之間下載的資料，當天那根 K 線視為不完整。
"""
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pandas as pd

TZ = ZoneInfo("Australia/Sydney")
SESSION_START = time(10, 0)
SESSION_SAFE = time(16, 45)    # 此時間之後視為收盤資料已完整


def now_local():
    return datetime.now(TZ)


def _in_session(dt):
    return dt.weekday() < 5 and SESSION_START <= dt.time() < SESSION_SAFE


def drop_partial_today(df):
    """下載當下若在盤中，丟掉「今天」那一列（盤中價格不是收盤價）。"""
    now = now_local()
    if _in_session(now):
        return df[df.index < pd.Timestamp(now.date())]
    return df


def is_tainted(mtime):
    """檔案是否在盤中寫入（可能含當日不完整 K 線）。"""
    return _in_session(datetime.fromtimestamp(mtime, TZ))


def strip_tainted_bar(df, mtime):
    """若檔案在盤中寫入，移除檔案寫入當天那一列。"""
    if is_tainted(mtime):
        day = pd.Timestamp(datetime.fromtimestamp(mtime, TZ).date())
        return df[df.index < day]
    return df
