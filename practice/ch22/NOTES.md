# K26 第 22 章練習：Notebook → .py → Streamlit

> 快速 demo 模式：未經 QA agent／reviewer 審查。

## 做了什麼

1. `uv venv .venv` 建虛擬環境（Python 3.13.12），`uv pip install pandas plotly streamlit nbformat pytest`
   - 實裝版本：pandas 3.0.6、plotly 7.1.0、streamlit 1.66.0、nbformat 5.11.1
2. `make_notebook.py` 用 nbformat 產生 `sales.ipynb`：三段（載入／指標／圖表），模擬 12 個月 × 3 類別（電子產品、服飾、食品），固定亂數種子 42
3. 把 notebook 重構成三個模組：

   | 檔案 | 對應 notebook 段落 | 內容 |
   | --- | --- | --- |
   | `src/load.py` | 1. 載入資料 | `load_sales()` 產生 36 筆資料 |
   | `src/metrics.py` | 2. 指標計算 | `kpis`、`monthly_revenue`、`category_share`、`filter_sales`（純函式） |
   | `src/charts.py` | 3. 圖表 | `trend_chart`（折線）、`share_chart`（甜甜圈） |

4. `app.py`：Streamlit 儀表板
   - 側欄篩選器：產品類別（多選）、月份區間（滑桿）
   - 3 張 KPI 卡：總營收、總銷量、平均單價
   - 月營收趨勢圖、類別營收占比圖、明細表
   - 篩選後沒資料會顯示警告，不會報錯
5. `tests/test_metrics.py`：7 個測試（筆數、KPI、空資料、月彙總、占比加總 100%、篩選、非法參數）

## 結果

- `pytest`：**7 passed**
- `streamlit run app.py --server.headless true --server.port 8599` 背景啟動，3 秒內 `curl http://127.0.0.1:8599/` 回 **200**，`/_stcore/health` 也是 200；驗證後已關閉，8599 埠已釋放
- 另用 `streamlit.testing.v1.AppTest` 跑過腳本：0 個例外；全選 KPI = 3,747,673／15,321／244.6；只選「食品」= 857,357／4,850／176.8；全不選會出現警告
- 第一次跑時 Streamlit 警告 `use_container_width` 已棄用，改成 `width="stretch"` 後消失

## 和書上做法的差異

- **資料來源**：書上通常讀現成 CSV；這裡沒有真實資料，用固定種子的模擬資料，`load_sales()` 直接產生 DataFrame（之後要換成 `pd.read_csv` 只改這一個函式）
- **notebook 是產生的**：書上是先有手寫 notebook 再重構；這裡用 `make_notebook.py` + nbformat 生成「重構前」的版本，方便重現
- **沒有用 Claude 讀 notebook 再自動拆**：重構是一次直接寫好三個模組，不是逐 cell 對話式拆解
- **套件管理用 uv**，不是 pip + requirements.txt；也沒有建 `pyproject.toml`
- **多了 AppTest**：除了 curl 檢查 200，還用 Streamlit 內建測試框架確認頁面內容和篩選器行為（curl 只能證明伺服器起來，證明不了腳本沒錯）
- **沒部署**：書上可能部署到 Streamlit Community Cloud，這裡依指示不部署

## 已知沒處理

- 沒有 `requirements.txt`／`pyproject.toml`，換機器要手動重裝套件
- `sales.ipynb` 沒有實際執行（沒裝 jupyter），只用 nbformat 驗證格式
- 月份滑桿只能選整月，沒有日期級篩選
