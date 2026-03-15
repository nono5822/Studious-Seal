//
//  SealSenseiApp.swift
//  Studious Seal
//
//  Remote control and dashboard for OpenClaw AI study agent. iOS 17+.
//

import SwiftUI
import UIKit

@main
struct SealSenseiApp: App {
    init() {
        let pastelBlue = UIColor(red: 0.682, green: 0.776, blue: 0.812, alpha: 1) // #AEC6CF
        let darkNavy = UIColor(red: 0.149, green: 0.259, blue: 0.412, alpha: 1)   // slightly lighter navy
        let navAppearance = UINavigationBarAppearance()
        navAppearance.configureWithOpaqueBackground()
        navAppearance.backgroundColor = pastelBlue
        navAppearance.titleTextAttributes = [.foregroundColor: darkNavy]
        navAppearance.largeTitleTextAttributes = [.foregroundColor: darkNavy]
        UINavigationBar.appearance().standardAppearance = navAppearance
        UINavigationBar.appearance().scrollEdgeAppearance = navAppearance
        UINavigationBar.appearance().compactAppearance = navAppearance
        UINavigationBar.appearance().tintColor = darkNavy
        UINavigationBar.appearance().prefersLargeTitles = false

        let tabAppearance = UITabBarAppearance()
        tabAppearance.configureWithOpaqueBackground()
        tabAppearance.backgroundColor = pastelBlue
        UITabBar.appearance().standardAppearance = tabAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabAppearance
        UITabBar.appearance().tintColor = darkNavy
    }

    var body: some Scene {
        WindowGroup {
            MainTabView()
        }
    }
}
