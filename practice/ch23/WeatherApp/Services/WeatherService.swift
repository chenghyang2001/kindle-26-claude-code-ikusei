//
//  WeatherService.swift
//  WeatherApp
//
//  天氣資料來源。用 protocol 隔開，現在接假資料（MockWeatherService），
//  之後要換成 WeatherKit 或其他 API 時，只要新增一個實作，View 不用改。
//

import Foundation

enum WeatherServiceError: LocalizedError {
    case cityNotFound(String)
    case networkUnavailable

    var errorDescription: String? {
        switch self {
        case .cityNotFound(let id):
            return "找不到城市資料（\(id)）"
        case .networkUnavailable:
            return "目前無法連線，請稍後再試"
        }
    }
}

protocol WeatherServiceProtocol: Sendable {
    /// 可選城市清單
    func availableCities() -> [City]
    /// 取得指定城市的天氣
    func fetchWeather(for city: City) async throws -> WeatherReport
}

/// 假資料服務：用固定種子產生可重現的數值，模擬網路延遲
struct MockWeatherService: WeatherServiceProtocol {
    /// 模擬延遲（奈秒），預覽時可設 0
    var simulatedDelay: UInt64 = 400_000_000
    /// 測試錯誤畫面用：設為 true 時一律丟錯
    var shouldFail = false

    static let cities: [City] = [
        City(id: "taipei", name: "台北", country: "台灣", timeZoneIdentifier: "Asia/Taipei"),
        City(id: "kaohsiung", name: "高雄", country: "台灣", timeZoneIdentifier: "Asia/Taipei"),
        City(id: "tokyo", name: "東京", country: "日本", timeZoneIdentifier: "Asia/Tokyo"),
        City(id: "newyork", name: "紐約", country: "美國", timeZoneIdentifier: "America/New_York"),
        City(id: "london", name: "倫敦", country: "英國", timeZoneIdentifier: "Europe/London"),
        City(id: "sydney", name: "雪梨", country: "澳洲", timeZoneIdentifier: "Australia/Sydney")
    ]

    /// 每個城市的基準值：(基準溫度, 濕度, 風速, UV, 主要天氣)
    private static let baselines: [String: (Double, Int, Double, Int, WeatherCondition)] = [
        "taipei": (27, 78, 12, 7, .partlyCloudy),
        "kaohsiung": (30, 72, 9, 9, .sunny),
        "tokyo": (19, 60, 15, 4, .cloudy),
        "newyork": (14, 55, 20, 3, .rainy),
        "london": (11, 82, 18, 1, .rainy),
        "sydney": (22, 65, 22, 6, .thunderstorm)
    ]

    func availableCities() -> [City] {
        Self.cities
    }

    func fetchWeather(for city: City) async throws -> WeatherReport {
        if simulatedDelay > 0 {
            try await Task.sleep(nanoseconds: simulatedDelay)
        }
        if shouldFail {
            throw WeatherServiceError.networkUnavailable
        }
        guard let base = Self.baselines[city.id] else {
            throw WeatherServiceError.cityNotFound(city.id)
        }
        let (baseTemp, humidity, wind, uv, condition) = base
        let now = Date()
        let hourly = makeHourly(baseTemp: baseTemp, condition: condition, city: city, from: now)
        let temps = hourly.map(\.temperature)

        return WeatherReport(
            city: city,
            condition: condition,
            highTemperature: temps.max() ?? baseTemp,
            lowTemperature: temps.min() ?? baseTemp,
            environment: EnvironmentInfo(
                temperature: baseTemp,
                feelsLike: baseTemp + (humidity > 70 ? 2 : -1),
                humidity: humidity,
                windSpeed: wind,
                windDirection: Double(city.id.count * 47 % 360),
                uvIndex: uv
            ),
            hourly: hourly,
            updatedAt: now
        )
    }

    /// 產生未來 24 小時預報：用正弦波模擬日夜溫差（約 ±4°C，下午兩點最熱）
    private func makeHourly(baseTemp: Double, condition: WeatherCondition,
                            city: City, from start: Date) -> [HourlyForecast] {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = city.timeZone
        let startHour = calendar.dateInterval(of: .hour, for: start)?.start ?? start

        return (0..<24).compactMap { offset -> HourlyForecast? in
            guard let time = calendar.date(byAdding: .hour, value: offset, to: startHour) else {
                return nil
            }
            let hour = calendar.component(.hour, from: time)
            let phase = Double(hour - 14) / 24 * 2 * .pi
            let temp = (baseTemp + 4 * cos(phase)).rounded()
            let isNight = hour < 6 || hour >= 19
            let hourCondition: WeatherCondition =
                (isNight && (condition == .sunny || condition == .partlyCloudy)) ? .clearNight : condition
            let rainChance: Int
            switch condition {
            case .rainy, .thunderstorm: rainChance = 60 + (offset * 7) % 35
            case .cloudy: rainChance = 20 + (offset * 5) % 20
            default: rainChance = (offset * 3) % 15
            }
            return HourlyForecast(time: time, temperature: temp,
                                  condition: hourCondition, precipitationChance: rainChance)
        }
    }
}
