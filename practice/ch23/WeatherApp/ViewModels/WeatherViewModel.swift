//
//  WeatherViewModel.swift
//  WeatherApp
//
//  畫面狀態集中管理：目前城市、載入中/成功/失敗。
//  使用 iOS 17 起的 @Observable 巨集（Observation framework）。
//

import Foundation
import Observation

@MainActor
@Observable
final class WeatherViewModel {
    enum LoadState {
        case idle
        case loading
        case loaded(WeatherReport)
        case failed(String)
    }

    private(set) var state: LoadState = .idle
    private(set) var cities: [City]
    var selectedCity: City

    private let service: WeatherServiceProtocol
    /// 快速切換城市時，取消上一個尚未完成的請求，避免舊資料蓋掉新資料
    private var loadTask: Task<Void, Never>?

    init(service: WeatherServiceProtocol = MockWeatherService()) {
        self.service = service
        let cities = service.availableCities()
        self.cities = cities
        // 假資料一定有城市；保底用台北避免空陣列 crash
        self.selectedCity = cities.first
            ?? City(id: "taipei", name: "台北", country: "台灣", timeZoneIdentifier: "Asia/Taipei")
    }

    var report: WeatherReport? {
        if case .loaded(let report) = state { return report }
        return nil
    }

    func select(_ city: City) {
        guard city != selectedCity || report == nil else { return }
        selectedCity = city
        load()
    }

    func load() {
        loadTask?.cancel()
        let city = selectedCity
        state = .loading
        loadTask = Task { [service] in
            do {
                let report = try await service.fetchWeather(for: city)
                guard !Task.isCancelled else { return }
                self.state = .loaded(report)
            } catch is CancellationError {
                // 被新的請求取代，不更新畫面
            } catch {
                guard !Task.isCancelled else { return }
                self.state = .failed(error.localizedDescription)
            }
        }
    }

    /// 給 .refreshable 使用（下拉重新整理）
    func refresh() async {
        load()
        await loadTask?.value
    }
}
