//
//  PreviewData.swift
//  WeatherApp
//
//  #Preview 專用的同步假資料（不經過 async Service，預覽畫面才能立即顯示）。
//

import Foundation

enum PreviewData {
    static let report: WeatherReport = {
        let city = MockWeatherService.cities[0]
        let now = Date()
        let conditions: [WeatherCondition] = [.partlyCloudy, .sunny, .cloudy, .rainy]
        let hourly = (0..<12).map { offset -> HourlyForecast in
            HourlyForecast(
                time: now.addingTimeInterval(Double(offset) * 3600),
                temperature: 26 + Double(offset % 5),
                condition: conditions[offset % conditions.count],
                precipitationChance: (offset * 13) % 90
            )
        }
        return WeatherReport(
            city: city,
            condition: .partlyCloudy,
            highTemperature: 31,
            lowTemperature: 24,
            environment: EnvironmentInfo(temperature: 27, feelsLike: 29, humidity: 78,
                                         windSpeed: 12, windDirection: 135, uvIndex: 7),
            hourly: hourly,
            updatedAt: now
        )
    }()
}
