//
//  MainTabView.swift
//  Studious Seal
//
//  4-tab app: Focus, Interventions, Study Vault, Grade Calculator.
//

import SwiftUI

struct MainTabView: View {
    @StateObject private var api = APIService()

    var body: some View {
        TabView {
            FocusDashboardView(api: api)
                .tabItem {
                    Label("Focus", systemImage: "gauge.with.dots.needle.67percent")
                }
            InterventionFeedView(api: api)
                .tabItem {
                    Label("Interventions", systemImage: "bubble.left.and.bubble.right")
                }
            StudyVaultView(api: api)
                .tabItem {
                    Label("Study Vault", systemImage: "book.closed")
                }
            GradeCalculatorTabView(api: api)
                .tabItem {
                    Label("Grades", systemImage: "percent")
                }
        }
        .tint(Theme.gold)
        .task {
            api.loadMockData()
            if api.username != nil {
                await api.fetchDashboard()
            }
        }
    }
}

#Preview {
    MainTabView()
}
