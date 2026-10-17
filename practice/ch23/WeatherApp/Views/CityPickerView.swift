//
//  CityPickerView.swift
//  WeatherApp
//
//  城市選擇：以 sheet 呈現的可搜尋清單。
//

import SwiftUI

struct CityPickerView: View {
    let cities: [City]
    let selectedCity: City
    let onSelect: (City) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var searchText = ""

    private var filteredCities: [City] {
        let keyword = searchText.trimmingCharacters(in: .whitespaces)
        guard !keyword.isEmpty else { return cities }
        return cities.filter {
            $0.name.localizedCaseInsensitiveContains(keyword)
                || $0.country.localizedCaseInsensitiveContains(keyword)
                || $0.id.localizedCaseInsensitiveContains(keyword)
        }
    }

    var body: some View {
        NavigationStack {
            List(filteredCities) { city in
                Button {
                    onSelect(city)
                    dismiss()
                } label: {
                    HStack {
                        VStack(alignment: .leading) {
                            Text(city.name).font(.body)
                            Text(city.country).font(.caption).foregroundStyle(.secondary)
                        }
                        Spacer()
                        if city == selectedCity {
                            Image(systemName: "checkmark")
                                .foregroundStyle(Color.accentColor)
                        }
                    }
                    .contentShape(Rectangle())
                }
                .buttonStyle(.plain)
                .accessibilityAddTraits(city == selectedCity ? .isSelected : [])
            }
            .overlay {
                if filteredCities.isEmpty {
                    ContentUnavailableView.search(text: searchText)
                }
            }
            .searchable(text: $searchText, prompt: "搜尋城市或國家")
            .navigationTitle("選擇城市")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("關閉") { dismiss() }
                }
            }
        }
    }
}

#Preview {
    CityPickerView(cities: MockWeatherService.cities,
                   selectedCity: MockWeatherService.cities[0],
                   onSelect: { _ in })
}
