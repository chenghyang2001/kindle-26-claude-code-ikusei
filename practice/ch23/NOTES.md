# K26 第 23 章練習筆記：Claude 與 Xcode

日期：2026-10-18｜模式：kindle-drill 快速模式（未經 QA／審查）

## 做了什麼

在 `WeatherApp/` 產生一個 SwiftUI 天氣 App 的原始檔（共 11 個 `.swift` + README）：

| 類別 | 檔案 | 重點 |
| --- | --- | --- |
| 進入點 | `WeatherApp.swift` | `@main`，只放 `ContentView` |
| 主畫面 | `ContentView.swift` | 載入中／成功／失敗三種狀態、下拉重新整理、工具列（城市、主題）、3 個 `#Preview` |
| Models | `WeatherModels.swift`、`AppTheme.swift` | 城市、天氣狀況（對應 SF Symbols）、環境資訊（含風向換算、UV 分級）、逐時預報；主題 enum |
| ViewModels | `WeatherViewModel.swift` | `@Observable` + `@MainActor`，切城市時取消上一個請求 |
| Services | `WeatherService.swift` | `WeatherServiceProtocol` + `MockWeatherService`（6 城市、正弦波模擬日夜溫差、可模擬失敗） |
| Views | 頁首、環境資訊 2x2 卡片、逐時預報橫向捲動、可搜尋城市選單、預覽假資料 | |

功能對照需求：

- [x] 深淺主題切換：跟隨系統／淺色／深色，點按循環、長按選單，`@AppStorage` 記住
- [x] 環境資訊：溫度（體感）／濕度（進度條）／風速（八方位風向）／紫外線（等級＋進度條）
- [x] 逐時預報：24 小時 `ScrollView(.horizontal)` + `LazyHStack`
- [x] 城市選擇：sheet + `.searchable`，可搜中文名、國家或英文 id
- [x] 假資料：全部來自 `MockWeatherService`，不需網路

另附 `WeatherApp/README.md`：Xcode 建專案與匯入檔案步驟、Xcode 26 Intelligence 接 Claude、Claude Code + `xcodebuild` / `xcrun simctl` 的工作流程。

## 結果

- 原始檔已產生，**未建置、未執行**（本機是 Windows，沒有 Xcode）。
- **語法檢查：略過**。
  - Git Bash 找不到 `swiftc` / `swift`。
  - 嘗試 WSL：WSL2 無法啟動（`HCS_E_HYPERV_NOT_INSTALLED`，BIOS 虛擬化未開）。
  - 就算有 Linux 版 swiftc，也沒有 SwiftUI framework，只能檢查 Models / Services，View 檔一定會失敗，所以沒有另外硬裝。
- 改以人工檢查：寫完後重看一次，修了兩處可能編譯不過或執行期有警告的地方：
  1. `compactMap` 的多行 closure 補上回傳型別 `-> HourlyForecast?`，避免型別推論失敗。
  2. 背景漸層原本引用不存在的 Asset 顏色 `SkyTop`，改用系統色。

## 已知風險（快速模式沒處理）

- 沒有在真的 Xcode 編譯過，可能還有小的型別或 API 可用性錯誤；到 Mac 上第一次建置時，可直接請 Xcode 內的 Claude 或 Claude Code 修。
- 最低部署目標 iOS 17；用 Swift 6 嚴格並行檢查（Strict Concurrency = Complete）時，`MockWeatherService` 的靜態字典可能需要補 `Sendable` 標註。
- 沒有單元測試、沒有 App Icon / Assets、沒有在地化字串檔（中文直接寫在程式碼裡）。
- 假資料的風向是用城市 id 長度算的，只是為了每個城市看起來不一樣。

## 和書上做法的差異

| 書上做法（Mac + Xcode，依本章主題整理） | 本次練習（Windows） | 原因 |
| --- | --- | --- |
| 在 Xcode 建專案，用 Xcode 內建 Claude（Intelligence 面板）對話生成程式碼 | 用 Claude Code 在終端機直接產生 `.swift` 檔，README 寫明之後怎麼匯入 Xcode | 本機沒有 Xcode |
| 每次修改後在 Canvas / 模擬器即時看結果 | 只能寫 `#Preview`，留到 Mac 上看 | Windows 無法跑 SwiftUI |
| 用 `xcodebuild` 建置，讓 Claude 讀錯誤自動修 | 無法建置，改人工檢查；README 附 `xcodebuild` 指令與 `CLAUDE.md` 範本 | 沒有 swiftc / Xcode toolchain |
| 一般是一次一個功能、在對話中逐步加 | 一次把四個功能和資料夾結構全部做好 | 快速 demo 模式，全自動執行 |
| 書上需求未特別要求 ViewModel | 多加 `ViewModels/` 資料夾 | 把載入狀態與取消請求的邏輯從 View 抽出，方便之後換真正的 API |
