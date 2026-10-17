//
//  HourlyForecastView.swift
//  WeatherApp
//
//  逐時預報：橫向捲動的 24 小時卡片。
//

import SwiftUI

struct HourlyForecastView: View {
    let forecasts: [HourlyForecast]
    let timeZone: TimeZone

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("逐時預報", systemImage: "clock")
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)

            if forecasts.isEmpty {
                Text("目前沒有預報資料")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            } else {
                ScrollView(.horizontal, showsIndicators: false) {
                    LazyHStack(spacing: 16) {
                        ForEach(Array(forecasts.enumerated()), id: \.element.id) { index, item in
                            HourlyItemView(item: item, isNow: index == 0, timeZone: timeZone)
                        }
                    }
                    .padding(.horizontal, 4)
                }
                .scrollTargetBehavior(.viewAligned)
            }
        }
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct HourlyItemView: View {
    let item: HourlyForecast
    let isNow: Bool
    let timeZone: TimeZone

    private var timeText: String {
        if isNow { return "現在" }
        var style = Date.FormatStyle.dateTime.hour(.twoDigits(amPM: .omitted))
        style.timeZone = timeZone
        return item.time.formatted(style) + "時"
    }

    var body: some View {
        VStack(spacing: 8) {
            Text(timeText)
                .font(.caption.weight(isNow ? .bold : .regular))
            Image(systemName: item.condition.symbolName)
                .symbolRenderingMode(.multicolor)
                .font(.title2)
                .frame(height: 30)
            // 降雨機率 >= 30% 才顯示，避免畫面太雜
            Text(item.precipitationChance >= 30 ? "\(item.precipitationChance)%" : " ")
                .font(.caption2)
                .foregroundStyle(.blue)
            Text(TemperatureFormatter.string(item.temperature))
                .font(.headline)
        }
        .frame(width: 56)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(timeText)，\(item.condition.displayName)，\(TemperatureFormatter.string(item.temperature))")
    }
}

#Preview {
    HourlyForecastView(forecasts: PreviewData.report.hourly, timeZone: .current)
        .padding()
}
