//
//  AppTheme.swift
//  WeatherApp
//
//  深淺主題設定。以 rawValue 存進 @AppStorage，App 重開後仍保留使用者選擇。
//

import SwiftUI

enum AppTheme: String, CaseIterable, Identifiable {
    case system
    case light
    case dark

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .system: return "跟隨系統"
        case .light: return "淺色"
        case .dark: return "深色"
        }
    }

    var symbolName: String {
        switch self {
        case .system: return "circle.lefthalf.filled"
        case .light: return "sun.max"
        case .dark: return "moon"
        }
    }

    /// 傳給 .preferredColorScheme；nil 代表跟隨系統設定
    var colorScheme: ColorScheme? {
        switch self {
        case .system: return nil
        case .light: return .light
        case .dark: return .dark
        }
    }

    /// 工具列按鈕用：依序循環 系統 → 淺色 → 深色 → 系統
    var next: AppTheme {
        let all = AppTheme.allCases
        let index = all.firstIndex(of: self) ?? 0
        return all[(index + 1) % all.count]
    }
}
