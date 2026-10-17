//
//  CurrentWeatherHeader.swift
//  WeatherApp
//
//  頁首大字：城市名、天氣圖示、目前溫度、高低溫。
//

import SwiftUI

struct CurrentWeatherHeader: View {
    let report: WeatherReport

    var body: some View {
        VStack(spacing: 8) {
            Text(report.city.name)
                .font(.largeTitle.weight(.semibold))
            Text(report.city.country)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Image(systemName: report.condition.symbolName)
                .symbolRenderingMode(.multicolor)
                .font(.system(size: 72))
                .padding(.vertical, 4)
                .accessibilityHidden(true)

            Text(TemperatureFormatter.string(report.environment.temperature))
                .font(.system(size: 64, weight: .thin, design: .rounded))
                .contentTransition(.numericText())

            Text(report.condition.displayName)
                .font(.title3)

            Text("最高 \(TemperatureFormatter.string(report.highTemperature))  最低 \(TemperatureFormatter.string(report.lowTemperature))")
                .font(.callout)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .combine)
    }
}

/// 溫度統一格式：四捨五入到整數 + 「°」
enum TemperatureFormatter {
    static func string(_ celsius: Double) -> String {
        "\(Int(celsius.rounded()))°"
    }
}

#Preview {
    CurrentWeatherHeader(report: PreviewData.report)
        .padding()
}
