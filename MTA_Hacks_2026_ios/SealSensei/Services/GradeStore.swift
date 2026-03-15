//
//  GradeStore.swift
//  Studious Seal
//
//  Persists folders, classes, and grade components to UserDefaults.
//

import Foundation
import SwiftUI

// MARK: - Persisted data

private struct GradeData: Codable {
    var folders: [GradeFolder]
    var classes: [GradeClass]
    var components: [GradeComponent]
    var displayMode: GradeDisplayMode
}

// MARK: - Store

@MainActor
final class GradeStore: ObservableObject {
    static let displayModeKey = "sealsensei.gradeDisplayMode"
    static let gradeDataKey = "sealsensei.gradeData"

    @Published var folders: [GradeFolder] = []
    @Published var classes: [GradeClass] = []
    @Published var components: [GradeComponent] = []
    @Published var displayMode: GradeDisplayMode = .percentage

    private let defaults = UserDefaults.standard

    init() {
        load()
    }

    // MARK: - Load / Save

    private func load() {
        if let raw = defaults.string(forKey: Self.gradeDataKey),
           let data = try? JSONDecoder().decode(GradeData.self, from: Data(raw.utf8)) {
            folders = data.folders
            classes = data.classes
            components = data.components
            displayMode = data.displayMode
        } else if let modeRaw = defaults.string(forKey: Self.displayModeKey),
                  let mode = GradeDisplayMode(rawValue: modeRaw) {
            displayMode = mode
        }
    }

    private func save() {
        let data = GradeData(folders: folders, classes: classes, components: components, displayMode: displayMode)
        if let encoded = try? JSONEncoder().encode(data),
           let string = String(data: encoded, encoding: .utf8) {
            defaults.set(string, forKey: Self.gradeDataKey)
        }
        defaults.set(displayMode.rawValue, forKey: Self.displayModeKey)
    }

    // MARK: - Folders

    func addFolder(name: String) {
        folders.append(GradeFolder(name: name))
        folders.sort { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
        save()
    }

    func updateFolder(_ folder: GradeFolder) {
        if let i = folders.firstIndex(where: { $0.id == folder.id }) {
            folders[i] = folder
            save()
        }
    }

    func deleteFolder(_ folder: GradeFolder) {
        let classIdsInFolder = Set(classes.filter { $0.folderId == folder.id }.map(\.id))
        components.removeAll { classIdsInFolder.contains($0.classId) }
        classes.removeAll { $0.folderId == folder.id }
        folders.removeAll { $0.id == folder.id }
        save()
    }

    // MARK: - Classes

    func classes(in folderId: UUID) -> [GradeClass] {
        classes.filter { $0.folderId == folderId }.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    func unfiledClasses() -> [GradeClass] {
        classes.filter { $0.folderId == nil }.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    func addClass(name: String, folderId: UUID?) {
        classes.append(GradeClass(name: name, folderId: folderId))
        save()
    }

    func updateClass(_ gradeClass: GradeClass) {
        if let i = classes.firstIndex(where: { $0.id == gradeClass.id }) {
            classes[i] = gradeClass
            save()
        }
    }

    func deleteClass(_ gradeClass: GradeClass) {
        components.removeAll { $0.classId == gradeClass.id }
        classes.removeAll { $0.id == gradeClass.id }
        save()
    }

    /// Move a class into a folder (or back to unfiled if folderId is nil).
    func moveClass(_ gradeClass: GradeClass, toFolderId folderId: UUID?) {
        var updated = gradeClass
        updated.folderId = folderId
        updateClass(updated)
    }

    // MARK: - Components

    func components(for classId: UUID) -> [GradeComponent] {
        components.filter { $0.classId == classId }.sorted { $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending }
    }

    func addComponent(classId: UUID, name: String, weightPercent: Double, earnedPoints: Double, maxPoints: Double) {
        components.append(GradeComponent(classId: classId, name: name, weightPercent: weightPercent, earnedPoints: earnedPoints, maxPoints: maxPoints))
        save()
    }

    func updateComponent(_ component: GradeComponent) {
        if let i = components.firstIndex(where: { $0.id == component.id }) {
            components[i] = component
            save()
        }
    }

    func deleteComponent(_ component: GradeComponent) {
        components.removeAll { $0.id == component.id }
        save()
    }

    /// Overall grade for a class (weighted average of components). 0–100.
    func overallPercentage(for classId: UUID) -> Double? {
        let comps = components(for: classId)
        guard !comps.isEmpty else { return nil }
        let totalWeight = comps.reduce(0) { $0 + $1.weightPercent }
        guard totalWeight > 0 else { return nil }
        let weightedSum = comps.reduce(0) { $0 + $1.weightedContribution }
        return weightedSum / totalWeight * 100
    }

    func setDisplayMode(_ mode: GradeDisplayMode) {
        displayMode = mode
        save()
    }
}
