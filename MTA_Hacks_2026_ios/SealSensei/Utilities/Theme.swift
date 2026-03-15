//
//  Theme.swift
//  Studious Seal
//
//  Color palette from the app icon (blue gradient + gold accent).
//

import SwiftUI

enum Theme {
    /// Light cyan/sky blue (icon background top)
    static let lightBlue = Color("StudiousSealLightBlue")
    /// Medium-dark azure (icon background bottom)
    static let darkBlue = Color("StudiousSealDarkBlue")
    /// Gold accent (cap tassel)
    static let gold = Color("StudiousSealGold")

    /// Vertical gradient matching the icon background
    static var backgroundGradient: LinearGradient {
        LinearGradient(
            colors: [lightBlue, darkBlue],
            startPoint: .top,
            endPoint: .bottom
        )
    }

    /// Gradient for navigation/toolbar areas
    static var barGradient: LinearGradient {
        LinearGradient(
            colors: [darkBlue.opacity(0.95), darkBlue],
            startPoint: .top,
            endPoint: .bottom
        )
    }
}
