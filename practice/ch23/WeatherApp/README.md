# WeatherApp（SwiftUI 天氣 App 練習）

K26 第 23 章「Claude 與 Xcode」練習產物。純 SwiftUI、全部使用假資料，不需要網路或 API Key。

## 功能

| 功能 | 實作位置 |
| --- | --- |
| 深淺主題切換（跟隨系統／淺色／深色，用 `@AppStorage` 記住） | `Models/AppTheme.swift`、`ContentView.swift` 右上角按鈕 |
| 環境資訊：溫度（含體感）、濕度、風速（含風向）、紫外線（含等級） | `Views/EnvironmentInfoGrid.swift` |
| 逐時預報 24 小時橫向捲動 | `Views/HourlyForecastView.swift` |
| 城市選擇（可搜尋的 sheet，6 個城市） | `Views/CityPickerView.swift`、左上角按鈕 |
| 假資料服務（protocol 隔開，之後可換 WeatherKit） | `Services/WeatherService.swift` |
| 載入中／失敗重試／下拉重新整理 | `ViewModels/WeatherViewModel.swift`、`ContentView.swift` |

## 檔案結構

```text
WeatherApp/
├── WeatherApp.swift            # @main 進入點
├── ContentView.swift           # 主畫面 + 工具列 + 3 個 #Preview
├── Models/
│   ├── WeatherModels.swift     # City / WeatherCondition / EnvironmentInfo / HourlyForecast / WeatherReport
│   └── AppTheme.swift          # 深淺主題 enum
├── ViewModels/
│   └── WeatherViewModel.swift  # @Observable 狀態管理
├── Services/
│   └── WeatherService.swift    # WeatherServiceProtocol + MockWeatherService
└── Views/
    ├── CurrentWeatherHeader.swift
    ├── EnvironmentInfoGrid.swift
    ├── HourlyForecastView.swift
    ├── CityPickerView.swift
    └── PreviewData.swift       # 預覽用同步假資料
```

## 需求

- macOS + Xcode 26（Xcode 15 以上也能編，最低部署目標 **iOS 17**，因為用了 `@Observable`、`ContentUnavailableView`、`scrollTargetBehavior`）
- 沒有任何第三方套件

## 在 Xcode 建立專案並放入這些檔案

1. 開 Xcode → **File › New › Project…** → **iOS › App** → Next。
2. 填寫：
   - Product Name：`WeatherApp`
   - Interface：**SwiftUI**；Language：**Swift**
   - Testing System / Storage：都選 None 即可
3. 存到任意位置（例如這個 repo 旁邊）。Xcode 會自動產生 `WeatherAppApp.swift` 與 `ContentView.swift`。
4. **刪掉** Xcode 自動產生的 `WeatherAppApp.swift` 與 `ContentView.swift`（選 Move to Trash），避免出現兩個 `@main`。
5. 在 Finder 把本資料夾的 `WeatherApp.swift`、`ContentView.swift`、`Models/`、`ViewModels/`、`Services/`、`Views/` 拖進 Xcode 左側 Project Navigator 的 `WeatherApp` 群組：
   - 勾選 **Copy items if needed**
   - 選 **Create groups**（或 Xcode 16+ 的 folder reference 也可以）
   - **Add to targets** 勾 `WeatherApp`
6. 專案設定 → Target `WeatherApp` → **General › Minimum Deployments** 設為 iOS 17.0 以上。
7. 選一台模擬器（例如 iPhone 17），按 **⌘R** 執行；或打開 `ContentView.swift` 用右側 Canvas 看「淺色／深色／載入失敗」三個預覽。

> 小提醒：如果出現 `Invalid redeclaration of 'ContentView'`，代表第 4 步沒有刪掉原本的 `ContentView.swift`。

## Xcode 26 內建 Claude（Intelligence）

Xcode 26 在設定中提供「Intelligence」功能，可以直接在 Xcode 裡跟 Claude 對話、讓它讀目前專案並修改程式碼。

1. **Xcode › Settings… › Intelligence**。
2. 在模型提供者中選 **Claude**，用你的 Claude 帳號登入（Pro / Max 等訂閱）或填 Anthropic API Key。
3. 打開左側的 Coding Assistant 面板（對話泡泡圖示），就可以下指令，例如：
   - 「把 `EnvironmentInfoGrid` 再加一張『能見度』卡片，假資料也要補」
   - 「`HourlyForecastView` 的溫度改成用顏色表示冷熱」
4. 在對話中可用 `@` 引用特定檔案或符號，讓 Claude 只看相關程式碼；改動會以 diff 呈現，可逐段接受或還原。
5. 較新的 Xcode 26.x 版本另外支援 agentic coding（Claude Agent），能自己跑建置、看錯誤再修正；確切功能名稱與選單位置以你安裝的 Xcode 版本為準。

## 用 Claude Code（終端機）搭配 xcodebuild

不想在 Xcode 內對話，也可以在專案資料夾開 Claude Code，讓它用 `xcodebuild` 自己建置、讀錯誤、修程式。

### 1. 讓 Claude Code 知道怎麼建置

在 Xcode 專案根目錄放一個 `CLAUDE.md`，寫清楚建置指令：

```markdown
## 建置與測試
- 建置：xcodebuild -project WeatherApp.xcodeproj -scheme WeatherApp \
    -destination 'platform=iOS Simulator,name=iPhone 17' build
- 測試：同上，把 build 換成 test
- 列出可用模擬器：xcrun simctl list devices available
- 改完 Swift 檔一定要跑一次建置，有錯就修到 BUILD SUCCEEDED 為止
```

### 2. 常用指令

```bash
# 看專案有哪些 scheme
xcodebuild -list -project WeatherApp.xcodeproj

# 建置到模擬器（-quiet 只輸出警告與錯誤，省 Claude 的 context）
xcodebuild -project WeatherApp.xcodeproj -scheme WeatherApp \
  -destination 'platform=iOS Simulator,name=iPhone 17' -quiet build

# 開模擬器、安裝並啟動 App
xcrun simctl boot "iPhone 17"
open -a Simulator
xcrun simctl install booted ~/Library/Developer/Xcode/DerivedData/WeatherApp-*/Build/Products/Debug-iphonesimulator/WeatherApp.app
xcrun simctl launch booted <你的 Bundle Identifier>

# 截圖給 Claude 看畫面
xcrun simctl io booted screenshot screen.png
```

### 3. 減少權限詢問

在專案的 `.claude/settings.local.json` 允許建置類指令：

```json
{
  "permissions": {
    "allow": ["Bash(xcodebuild:*)", "Bash(xcrun simctl:*)"]
  }
}
```

### 4. 建議工作流程

1. 在 Xcode 建好專案（上面步驟），關掉 Xcode 或保持開著都可以（Xcode 會自動重新載入檔案）。
2. 在專案資料夾執行 `claude`，下指令例如「新增 7 日預報區塊，完成後用 xcodebuild 建置確認沒有錯誤」。
3. Claude Code 改檔 → 跑 `xcodebuild` → 讀錯誤 → 修正，直到 `BUILD SUCCEEDED`。
4. 回到 Xcode 用 Canvas 或模擬器看實際畫面。新增的 Swift 檔若沒出現在 Target 中，在 Xcode 裡把它加入 Target（Xcode 16 以上用資料夾同步群組的專案會自動加入）。
