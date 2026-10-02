# 澳洲市場廣度監測（Stockbee 風格）

每天雪梨收盤後，從 Yahoo Finance 下載 ASX 普通股價格，計算廣度指標，並用網頁顯示。

## 每日操作

雪梨時間 17:00 之後（約台北時間 14:00；雪梨夏令時間期間為 13:00），雙擊 `update.bat`（或執行 `py scripts/update_daily.py`）。
它會依序：下載增量價格 → 計算指標 → 提交並推送到 GitHub。約 1–2 分鐘後網頁更新。

想先在本機看結果：雙擊 `view_local.bat`，會開啟 http://localhost:8000/index.html。

## 檔案

| 檔案 | 用途 |
|---|---|
| `index.html` | 儀表板網頁（讀取 `data/breadth.csv`） |
| `data/breadth.csv` | 每日廣度指標（會推送到 GitHub） |
| `data/universe.csv` | 股票池，約每月自動提醒更新（`universe_excluded.csv` 列出被排除者，供檢查） |
| `data/prices/` | 個股價格（只留在本機，不推送） |
| `scripts/update_daily.py` | 每日一鍵更新 |
| `scripts/download_prices.py` | 下載價格（增量、除權息偵測、斷點續傳） |
| `scripts/compute_breadth.py` | 計算指標 |
| `scripts/build_universe.py` | 由 ASX 名單建立股票池 |

## 第一次設定 GitHub（只做一次）

1. 把整個專案資料夾搬到 `C:\au-breadth`。**不要放在 OneDrive 裡**：OneDrive 會同步 `.git` 資料夾與幾千個價格檔，容易造成衝突與變慢。
2. 安裝 Git for Windows：https://git-scm.com/download/win （一路下一步即可）。
3. 在 GitHub 網站右上角「+」→ New repository：名稱填 `au-breadth`，選 Public，**不要**勾選 Add a README，按 Create。
4. 在專案資料夾開啟終端機，依序執行（把 `你的帳號` 換成 GitHub 帳號）：

```
git config --global user.name "你的名字"
git config --global user.email "你的 GitHub 信箱"
git init -b main
git add index.html data/breadth.csv data/universe.csv scripts .gitignore update.bat view_local.bat README.md
git commit -m "first commit"
git remote add origin https://github.com/你的帳號/au-breadth.git
git push -u origin main
```

第一次推送會跳出瀏覽器要求登入 GitHub，照畫面授權即可。

5. 在 GitHub 的 repo 頁面：Settings → Pages → Source 選 `Deploy from a branch` → Branch 選 `main`、資料夾 `/ (root)` → Save。
6. 等 1–2 分鐘，網址是 `https://你的帳號.github.io/au-breadth/`。

注意：免費帳號的 GitHub Pages 需要 Public 倉庫，任何知道網址的人都看得到網頁與程式碼（內容只有公開行情的統計，沒有個人資料）。

## 指標定義

- 股票池：ASX 上市普通股，排除 ETF、基金、信託、混合證券、權證；當日收盤價 ≥ A$0.40 且 20 日平均成交金額 ≥ A$10 萬。
- 價格：Yahoo 調整後收盤價（含分割與股息）。
- 4% 漲／跌：當日報酬 ≥ +4% 或 ≤ −4% 的家數（未加成交量條件）。
- 5／10 日比率：近 5／10 日漲 4% 家數合計 ÷ 跌 4% 家數合計。
- 季度：65 個交易日報酬 ±25%。月度：21 個交易日報酬 ±25%、±50%。34 日：34 個交易日報酬 ±13%。
- T2108：收盤高於 40 日均線的股票比例。
- 基準：S&P/ASX 200（`^AXJO`）與追蹤它的 ETF（`STW.AX`）。

要調整門檻，可在 `compute_breadth.py` 以參數指定，例如 `--min-price 1 --min-avg-turnover 500000`。
先執行 `py scripts/compute_breadth.py --diagnose` 可看到各門檻下剩多少股票。

## 時間與夏令時間

ASX 交易時間是雪梨 10:00–16:00。腳本使用 Australia/Sydney 時區，自動處理夏令時間（每年 10 月第一個週日開始、4 月第一個週日結束）。盤中下載時不會存入當天未完成的 K 線。
