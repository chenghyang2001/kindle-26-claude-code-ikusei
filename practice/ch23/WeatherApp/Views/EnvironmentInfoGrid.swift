//
//  EnvironmentInfoGrid.swift
//  WeatherApp
//
//  環境資訊 2x2 卡片：溫度（體感）/ 濕度 / 風速 / 紫外線。
//

import SwiftUI

struct EnvironmentInfoGrid: View {
    let info: EnvironmentInfo

    private let columns = [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)]

    var body: some View {
        LazyVGrid(columns: columns, spacing: 12) {
            InfoCard(title: "溫度", symbol: "thermometer.medium",
                     value: TemperatureFormatter.string(info.temperature),
                     detail: "體感 \(TemperatureFormatter.string(info.feelsLike))")

            InfoCard(title: "濕度", symbol: "humidity.fill",
                     value: "\(info.humidity)%",
                     detail: info.humidity >= 70 ? "偏潮濕" : (info.humidity <= 35 ? "偏乾燥" : "舒適"),
                     progress: Double(info.humidity) / 100)

            InfoCard(title: "風速", symbol: "wind",
                     value: String(format: "%.0f km/h", info.windSpeed),
                     detail: info.windDirectionText)

            InfoCard(title: "紫外線", symbol: "sun.max.trianglebadge.exclamationmark",
                     value: "\(info.uvIndex)",
                     detail: "等級：\(info.uvLevel.rawValue)",
                     progress: min(Double(info.uvIndex) / 11, 1))
        }
    }
}

/// 單張資訊卡；progress 有值時底部顯示進度條
struct InfoCard: View {
    let title: String
    let symbol: String
    let value: String
    let detail: String
    var progress: Double? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(title, systemImage: symbol)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)
            Text(value)
                .font(.title.weight(.medium))
            Text(detail)
                .font(.footnote)
                .foregroundStyle(.secondary)
            if let progress {
                ProgressView(value: progress)
                    .tint(.accentColor)
            }
        }
        .frame(maxWidth: .infinity, minHeight: 110, alignment: .topLeading)
        .padding()
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        .accessibilityElement(children: .combine)
    }
}

#Preview {
    EnvironmentInfoGrid(info: PreviewData.report.environment)
        .padding()
}
