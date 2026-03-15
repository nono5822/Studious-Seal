//
//  DashboardData.swift
//  Studious Seal
//
//  Codable models for the OpenClaw dashboard API.
//

import Foundation

// MARK: - Root Response

struct DashboardResponse: Codable {
    let userProfile: UserProfile
    let liveStatus: LiveStatus
    let classes: [Class]
    let assignments: [Assignment]
    let interventionLogs: [InterventionLog]
    let knowledgeGaps: [KnowledgeGap]

    enum CodingKeys: String, CodingKey {
        case userProfile = "user_profile"
        case liveStatus = "live_status"
        case classes
        case assignments
        case interventionLogs = "intervention_logs"
        case knowledgeGaps = "knowledge_gaps"
    }
}

// MARK: - User Profile

struct UserProfile: Codable {
    let userId: String
    let name: String
    let linkedPlatforms: [String]

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case name
        case linkedPlatforms = "linked_platforms"
    }
}

// MARK: - Live Status

struct LiveStatus: Codable {
    let overallUrgencyScore: Double
    let isGaming: Bool
    let currentActivity: String?
    let lastActivePlatform: String?
    let lastPingTimestamp: String?

    enum CodingKeys: String, CodingKey {
        case overallUrgencyScore = "overall_urgency_score"
        case isGaming = "is_gaming"
        case currentActivity = "current_activity"
        case lastActivePlatform = "last_active_platform"
        case lastPingTimestamp = "last_ping_timestamp"
    }
}

// MARK: - Class

struct Class: Codable, Identifiable {
    var id: String { classId }
    let classId: String
    let name: String
    let professor: String?
    let syllabusParsed: Bool

    enum CodingKeys: String, CodingKey {
        case classId = "class_id"
        case name
        case professor
        case syllabusParsed = "syllabus_parsed"
    }
}

// MARK: - Assignment

struct Assignment: Codable, Identifiable {
    var id: String { assignmentId }
    let assignmentId: String
    let classId: String
    let title: String
    let dueDate: String
    let priorityScore: Int?
    let status: String
    let type: String?

    enum CodingKeys: String, CodingKey {
        case assignmentId = "assignment_id"
        case classId = "class_id"
        case title
        case dueDate = "due_date"
        case priorityScore = "priority_score"
        case status
        case type
    }

    var dueDateParsed: Date? {
        ISO8601DateFormatter().date(from: dueDate)
    }
}

// MARK: - Intervention Log

struct InterventionLog: Codable, Identifiable {
    var id: String { logId }
    let logId: String
    let timestamp: String
    let platform: String
    let trigger: String?
    let messageSent: String
    let userReply: String?

    enum CodingKeys: String, CodingKey {
        case logId = "log_id"
        case timestamp
        case platform
        case trigger
        case messageSent = "message_sent"
        case userReply = "user_reply"
    }

    var timestampParsed: Date? {
        ISO8601DateFormatter().date(from: timestamp)
    }
}

// MARK: - Knowledge Gap

struct KnowledgeGap: Codable, Identifiable, Hashable {
    var id: String { gapId }
    let gapId: String
    let classId: String
    let topic: String
    let questionAsked: String
    let wrongAnswerGiven: String
    let correctConcept: String
    let studyReference: String
    let youtubeLink: String?
    let status: String?

    enum CodingKeys: String, CodingKey {
        case gapId = "gap_id"
        case classId = "class_id"
        case topic
        case questionAsked = "question_asked"
        case wrongAnswerGiven = "wrong_answer_given"
        case correctConcept = "correct_concept"
        case studyReference = "study_reference"
        case youtubeLink = "youtube_link"
        case status
    }
}
