//
//  ContentView.swift
//  WeatherApp
//
//  主畫面：組合頁首、環境資訊、逐時預報；工具列有城市選擇與主題切換。
//

import SwiftUI

struct ContentView: View {
    @State private var viewModel: WeatherViewModel
    @State private var isShowingCityPicker = false
    @AppStorage("appTheme") private var themeRawValue = AppTheme.system.rawValue

    init(viewModel: WeatherViewModel = WeatherViewModel()) {
        _viewModel = State(initialValue: viewModel)
    }

    private var theme: AppTheme {
        AppTheme(rawValue: themeRawValue) ?? .system
    }

    var body: some View {
        NavigationStack {
            content
                .background(backgroundGradient.ignoresSafeArea())
                .navigationTitle("天氣")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar { toolbarContent }
                .sheet(isPresented: $isShowingCityPicker) {
                    CityPickerView(cities: viewModel.cities,
                                   selectedCity: viewModel.selectedCity) { city in
                        viewModel.select(city)
                    }
                    .presentationDetents([.medium, .large])
                }
        }
        // 主題切換套在最外層，sheet 也會一起套用
        .preferredColorScheme(theme.colorScheme)
        .task {
            if viewModel.report == nil { viewModel.load() }
        }
    }

    @ViewBuilder
    private var content: some View {
        switch viewModel.state {
        case .idle, .loading:
            ProgressView("載入 \(viewModel.selectedCity.name) 天氣中…")
                .frame(maxWidth: .infinity, maxHeight: .infinity)

        case .failed(let message):
            ContentUnavailableView {
                Label("載入失敗", systemImage: "exclamationmark.triangle")
            } description: {
                Text(message)
            } actions: {
                Button("重試") { viewModel.load() }
                    .buttonStyle(.borderedProminent)
            }

        case .loaded(let report):
            ScrollView {
                VStack(spacing: 20) {
                    CurrentWeatherHeader(report: report)
                    HourlyForecastView(forecasts: report.hourly, timeZone: report.city.timeZone)
                    EnvironmentInfoGrid(info: report.environment)
                    Text("更新時間：\(report.updatedAt.formatted(date: .omitted, time: .shortened))（假資料）")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
                .padding()
            }
            .refreshable { await viewModel.refresh() }
        }
    }

    @ToolbarContentBuilder
    private var toolbarContent: some ToolbarContent {
        ToolbarItem(placement: .topBarLeading) {
            Button {
                isShowingCityPicker = true
            } label: {
                Label(viewModel.selectedCity.name, systemImage: "location")
                    .labelStyle(.titleAndIcon)
            }
            .accessibilityLabel("選擇城市，目前為\(viewModel.selectedCity.name)")
        }
        ToolbarItem(placement: .topBarTrailing) {
            // 點一下循環切換；長按可直接選
            Menu {
                Picker("主題", selection: $themeRawValue) {
                    ForEach(AppTheme.allCases) { option in
                        Label(option.displayName, systemImage: option.symbolName)
                            .tag(option.rawValue)
                    }
                }
            } label: {
                Image(systemName: theme.symbolName)
            } primaryAction: {
                withAnimation { themeRawValue = theme.next.rawValue }
            }
            .accessibilityLabel("切換主題，目前為\(theme.displayName)")
        }
    }

    /// 背景漸層會依深淺模式自動換色
    private var backgroundGradient: some View {
        // systemBackground 本身會隨深淺模式變色，疊一層淡藍就有天空感
        LinearGradient(colors: [Color.blue.opacity(0.25), Color.clear],
                       startPoint: .top, endPoint: .bottom)
            .background(Color(uiColor: .systemBackground))
    }
}

#Preview("淺色") {
    ContentView(viewModel: WeatherViewModel(service: MockWeatherService(simulatedDelay: 0)))
        .preferredColorScheme(.light)
}

#Preview("深色") {
    ContentView(viewModel: WeatherViewModel(service: MockWeatherService(simulatedDelay: 0)))
        .preferredColorScheme(.dark)
}

#Preview("載入失敗") {
    ContentView(viewModel: WeatherViewModel(service: MockWeatherService(simulatedDelay: 0, shouldFail: true)))
}
