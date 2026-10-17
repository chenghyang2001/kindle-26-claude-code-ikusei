//
//  WeatherModels.swift
//  WeatherApp
//
//  天氣 App 的資料模型：城市、目前天氣、環境資訊、逐時預報。
//  全部是值型別（struct / enum），方便在 SwiftUI 預覽與假資料中使用。
//

import Foundation

/// 城市（城市選擇清單的項目）
struct City: Identifiable, Hashable, Codable {
    let id: String
    let name: String
    let country: String
    /// 用 IANA 時區名稱，讓逐時預報的時間顯示符合當地時間
    let timeZoneIdentifier: String

    var timeZone: TimeZone {
        TimeZone(identifier: timeZoneIdentifier) ?? .current
    }
}

/// 天氣狀況，對應 SF Symbols 圖示
enum WeatherCondition: String, Codable, CaseIterable {
    case sunny
    case partlyCloudy
    case cloudy
    case rainy
    case thunderstorm
    case snowy
    case clearNight

    var displayName: String {
        switch self {
        case .sunny: return "晴天"
        case .partlyCloudy: return "晴時多雲"
        case .cloudy: return "多雲"
        case .rainy: return "下雨"
        case .thunderstorm: return "雷雨"
        case .snowy: return "下雪"
        case .clearNight: return "晴朗夜空"
        }
    }

    /// SF Symbols 名稱（需搭配 .symbolRenderingMode(.multicolor) 才有彩色效果）
    var symbolName: String {
        switch self {
        case .sunny: return "sun.max.fill"
        case .partlyCloudy: return "cloud.sun.fill"
        case .cloudy: return "cloud.fill"
        case .rainy: return "cloud.rain.fill"
        case .thunderstorm: return "cloud.bolt.rain.fill"
        case .snowy: return "cloud.snow.fill"
        case .clearNight: return "moon.stars.fill"
        }
    }
}

/// 紫外線等級（依 WHO UV Index 分級）
enum UVLevel: String {
    case low = "低"
    case moderate = "中"
    case high = "高"
    case veryHigh = "過量"
    case extreme = "危險"

    init(index: Int) {
        switch index {
        case ..<3: self = .low
        case 3..<6: self = .moderate
        case 6..<8: self = .high
        case 8..<11: self = .veryHigh
        default: self = .extreme
        }
    }
}

/// 環境資訊：溫度 / 濕度 / 風速 / 紫外線
struct EnvironmentInfo: Codable, Hashable {
    /// 攝氏溫度
    let temperature: Double
    /// 體感溫度（攝氏）
    let feelsLike: Double
    /// 相對濕度 0...100（%）
    let humidity: Int
    /// 風速（km/h）
    let windSpeed: Double
    /// 風向（度，0 = 北）
    let windDirection: Double
    /// 紫外線指數 0...11+
    let uvIndex: Int

    var uvLevel: UVLevel { UVLevel(index: uvIndex) }

    /// 把角度轉成八方位中文
    var windDirectionText: String {
        let directions = ["北", "東北", "東", "東南", "南", "西南", "西", "西北"]
        let normalized = (windDirection.truncatingRemainder(dividingBy: 360) + 360)
            .truncatingRemainder(dividingBy: 360)
        let index = Int((normalized + 22.5) / 45) % directions.count
        return directions[index] + "風"
    }
}

/// 單一小時的預報
struct HourlyForecast: Identifiable, Codable, Hashable {
    let id: UUID
    let time: Date
    let temperature: Double
    let condition: WeatherCondition
    /// 降雨機率 0...100（%）
    let precipitationChance: Int

    init(id: UUID = UUID(), time: Date, temperature: Double,
         condition: WeatherCondition, precipitationChance: Int) {
        self.id = id
        self.time = time
        self.temperature = temperature
        self.condition = condition
        self.precipitationChance = precipitationChance
    }
}

/// 某城市的完整天氣資料（Service 回傳的單位）
struct WeatherReport: Codable, Hashable {
    let city: City
    let condition: WeatherCondition
    let highTemperature: Double
    let lowTemperature: Double
    let environment: EnvironmentInfo
    let hourly: [HourlyForecast]
    let updatedAt: Date
}
