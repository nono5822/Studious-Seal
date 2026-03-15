//
//  GradeModels.swift
//  Studious Seal
//
//  Models for the Grade Calculator: folders (e.g. semesters), classes, and weighted components.
//

import Foundation
import SwiftUI
import UniformTypeIdentifiers

// MARK: - Display preference

enum GradeDisplayMode: String, Codable, CaseIterable {
    case points     // e.g. 85/100
    case percentage // e.g. 85%
}

// MARK: - Folder (e.g. semester "A-2026")

struct GradeFolder: Identifiable, Codable, Hashable {
    var id: UUID
    var name: String
    var createdAt: Date

    init(id: UUID = UUID(), name: String, createdAt: Date = Date()) {
        self.id = id
        self.name = name
        self.createdAt = createdAt
    }
}

// MARK: - Class (one course in a folder)

struct GradeClass: Identifiable, Codable, Hashable, Transferable {
    var id: UUID
    var name: String
    var folderId: UUID?
    var createdAt: Date

    init(id: UUID = UUID(), name: String, folderId: UUID?, createdAt: Date = Date()) {
        self.id = id
        self.name = name
        self.folderId = folderId
        self.createdAt = createdAt
    }

    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .json)
    }
}

// MARK: - Grade component (one weighted item: e.g. "Midterm" 30%, 85/100)

struct GradeComponent: Identifiable, Codable, Hashable {
    var id: UUID
    var classId: UUID
    var name: String
    /// Weight as percentage (e.g. 20 for 20%)
    var weightPercent: Double
    /// Points earned
    var earnedPoints: Double
    /// Max points (e.g. 100). Used to compute percentage and display as points.
    var maxPoints: Double

    init(id: UUID = UUID(), classId: UUID, name: String, weightPercent: Double, earnedPoints: Double, maxPoints: Double) {
        self.id = id
        self.classId = classId
        self.name = name
        self.weightPercent = weightPercent
        self.earnedPoints = earnedPoints
        self.maxPoints = maxPoints
    }

    var percentage: Double {
        guard maxPoints > 0 else { return 0 }
        return (earnedPoints / maxPoints) * 100
    }

    var weightedContribution: Double {
        (percentage / 100) * weightPercent
    }
}
