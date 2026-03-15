//
//  APIService.swift
//  Studious Seal
//
//  Fetches dashboard data from the Flask Study Sensei API Bridge.
//  Endpoints: GET /api/users, GET /api/user/<username>/priority
//

import Foundation

enum APIError: LocalizedError {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case decodingError(Error)
    case noUserSelected
    case notFound(username: String)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid server URL"
        case .networkError(let e): return "Network error: \(e.localizedDescription)"
        case .invalidResponse: return "Server returned an error"
        case .decodingError(let e): return "Invalid data: \(e.localizedDescription)"
        case .noUserSelected: return "Select a user to load your dashboard"
        case .notFound(let username): return "No priority list found for \(username)"
        }
    }
}

@MainActor
final class APIService: ObservableObject {
    /// Base URL of the Flask API (e.g. "http://localhost:5000/" or "https://your-ngrok.ngrok-free.app/")
    static let defaultBaseURLString = "http://localhost:5000/"

    private static let baseURLKey = "studiousseal.apiBaseURL"
    private static let usernameKey = "studiousseal.username"

    @Published var baseURLString: String {
        didSet {
            UserDefaults.standard.set(baseURLString, forKey: Self.baseURLKey)
        }
    }

    @Published var username: String? {
        didSet {
            UserDefaults.standard.set(username, forKey: Self.usernameKey)
        }
    }

    @Published var users: [String] = []
    @Published var dashboard: DashboardResponse?
    @Published var isLoading = false
    @Published var error: Error?

    private let session: URLSession = {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 15
        return URLSession(configuration: config)
    }()

    init() {
        self.baseURLString = UserDefaults.standard.string(forKey: Self.baseURLKey) ?? Self.defaultBaseURLString
        self.username = UserDefaults.standard.string(forKey: Self.usernameKey)
    }

    /// Base URL with no trailing path (e.g. http://localhost:5000)
    private var baseURL: URL? {
        let trimmed = baseURLString.trimmingCharacters(in: .whitespacesAndNewlines)
        let withSlash = trimmed.hasSuffix("/") ? trimmed : trimmed + "/"
        return URL(string: withSlash)
    }

    /// GET /api/users — list usernames that have a workspace
    func fetchUsers() async {
        guard let base = baseURL else {
            error = APIError.invalidURL
            return
        }
        guard let url = URL(string: "api/users", relativeTo: base) else {
            error = APIError.invalidURL
            return
        }

        error = nil
        do {
            let (data, response) = try await session.data(from: url)
            guard let http = response as? HTTPURLResponse else {
                error = APIError.invalidResponse
                return
            }
            guard (200...299).contains(http.statusCode) else {
                error = APIError.invalidResponse
                return
            }
            let decoded = try JSONDecoder().decode([String].self, from: data)
            users = decoded
        } catch {
            self.error = APIError.decodingError(error)
            users = []
        }
    }

    /// GET /api/user/<username>/priority — dashboard data (priority_list.json)
    func fetchDashboard() async {
        guard let user = username, !user.isEmpty else {
            dashboard = nil
            error = APIError.noUserSelected
            return
        }
        guard let base = baseURL else {
            error = APIError.invalidURL
            return
        }
        let path = "api/user/\(user.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? user)/priority"
        guard let url = URL(string: path, relativeTo: base) else {
            error = APIError.invalidURL
            return
        }

        isLoading = true
        error = nil

        do {
            let (data, response) = try await session.data(from: url)
            guard let http = response as? HTTPURLResponse else {
                error = APIError.invalidResponse
                isLoading = false
                return
            }
            if http.statusCode == 404 {
                error = APIError.notFound(username: user)
                isLoading = false
                return
            }
            guard (200...299).contains(http.statusCode) else {
                error = APIError.invalidResponse
                isLoading = false
                return
            }
            let decoder = JSONDecoder()
            let decoded = try decoder.decode(DashboardResponse.self, from: data)
            dashboard = decoded
        } catch {
            self.error = APIError.decodingError(error)
        }
        isLoading = false
    }

    func setUsername(_ name: String?) {
        username = name?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == true ? nil : name?.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    func setBaseURL(_ url: String) {
        baseURLString = url.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// Load mock data for previews and testing without backend.
    func loadMockData() {
        let mock = DashboardResponse(
            userProfile: UserProfile(userId: "student_101", name: "Alex", linkedPlatforms: ["discord", "telegram", "whatsapp"]),
            liveStatus: LiveStatus(
                overallUrgencyScore: 8.5,
                isGaming: true,
                currentActivity: "League of Legends",
                lastActivePlatform: "discord",
                lastPingTimestamp: "2026-03-14T12:05:00Z"
            ),
            classes: [
                Class(classId: "IFT-1010", name: "Programming I", professor: "Dr. Turing", syllabusParsed: true),
                Class(classId: "BIOL-101", name: "Intro to Biology", professor: "Dr. Watson", syllabusParsed: true),
                Class(classId: "MATH-201", name: "Linear Algebra", professor: "Prof. Gauss", syllabusParsed: true)
            ],
            assignments: [
                Assignment(assignmentId: "task_001", classId: "IFT-1010", title: "Binary Tree Implementation", dueDate: "2026-03-16T23:59:00Z", priorityScore: 9, status: "pending", type: "project"),
                Assignment(assignmentId: "task_002", classId: "IFT-1010", title: "Weekly Quiz 5", dueDate: "2026-03-18T23:59:00Z", priorityScore: 5, status: "pending", type: "quiz"),
                Assignment(assignmentId: "task_003", classId: "IFT-1010", title: "Recursion Exercises", dueDate: "2026-03-20T23:59:00Z", priorityScore: 6, status: "pending", type: "homework"),
                Assignment(assignmentId: "task_004", classId: "BIOL-101", title: "Lab Report 2 – Mitosis", dueDate: "2026-03-19T23:59:00Z", priorityScore: 7, status: "pending", type: "lab"),
                Assignment(assignmentId: "task_005", classId: "BIOL-101", title: "Midterm Exam", dueDate: "2026-03-25T09:00:00Z", priorityScore: 10, status: "pending", type: "exam"),
                Assignment(assignmentId: "task_006", classId: "MATH-201", title: "Problem Set 4", dueDate: "2026-03-22T23:59:00Z", priorityScore: 6, status: "pending", type: "homework"),
                Assignment(assignmentId: "task_007", classId: "MATH-201", title: "Eigenvalues Quiz", dueDate: "2026-03-21T23:59:00Z", priorityScore: 5, status: "pending", type: "quiz")
            ],
            interventionLogs: [
                InterventionLog(logId: "log_089", timestamp: "2026-03-14T12:00:00Z", platform: "discord", trigger: "gaming_detected", messageSent: "Hey Alex! I see you're in the Rift. Your IFT-1010 project is due in 2 days. Urgency is at a 9/10. Log off and study!", userReply: "Logging off now, promise."),
                InterventionLog(logId: "log_088", timestamp: "2026-03-13T20:30:00Z", platform: "telegram", trigger: "reminder", messageSent: "Quick reminder: Quiz 5 for Programming I is in 5 days. Have you reviewed the recursion chapter?", userReply: "I'll do it tonight."),
                InterventionLog(logId: "log_087", timestamp: "2026-03-13T14:00:00Z", platform: "discord", trigger: "study_check", messageSent: "You've been focused for 2 hours — great job! Take a short break and then consider tackling the Binary Tree project.", userReply: nil)
            ],
            knowledgeGaps: [
                KnowledgeGap(gapId: "gap_001", classId: "BIOL-101", topic: "Cellular Respiration", questionAsked: "Where does the Krebs cycle occur?", wrongAnswerGiven: "Nucleus", correctConcept: "The Krebs cycle occurs in the mitochondrial matrix.", studyReference: "Syllabus.pdf - Page 14", youtubeLink: "https://youtube.com/results?search_query=Krebs+cycle+explained", status: "needs_review"),
                KnowledgeGap(gapId: "gap_002", classId: "IFT-1010", topic: "Recursion", questionAsked: "What is the base case in a recursive function?", wrongAnswerGiven: "The first line of the function", correctConcept: "The base case is the condition that stops the recursion and returns without making another recursive call.", studyReference: "Lecture 6 slides - Slide 12", youtubeLink: "https://youtube.com/results?search_query=recursion+base+case", status: "reviewed"),
                KnowledgeGap(gapId: "gap_003", classId: "MATH-201", topic: "Eigenvalues", questionAsked: "What does it mean for λ to be an eigenvalue of matrix A?", wrongAnswerGiven: "A − λ is invertible", correctConcept: "λ is an eigenvalue of A if there exists a nonzero vector v such that Av = λv; equivalently, det(A − λI) = 0.", studyReference: "Textbook Ch. 5 - Section 5.1", youtubeLink: "https://youtube.com/results?search_query=eigenvalues+linear+algebra", status: "needs_review")
            ]
        )
        dashboard = mock
        error = nil
    }
}
