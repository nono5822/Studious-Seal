//
//  FocusDashboardView.swift
//  Studious Seal
//
//  Tab 1: Urgency meter, live status card, upcoming assignments.
//

import SwiftUI

struct FocusDashboardView: View {
    @ObservedObject var api: APIService
    @State private var showUserPicker = false

    private var liveStatus: LiveStatus? { api.dashboard?.liveStatus }
    private var assignments: [Assignment] {
        let list = api.dashboard?.assignments ?? []
        return list.sorted { a, b in
            (a.dueDateParsed ?? .distantFuture) < (b.dueDateParsed ?? .distantFuture)
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if api.isLoading {
                    ProgressView("Loading…")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let err = api.error {
                    ContentUnavailableView(
                        "Couldn't load dashboard",
                        systemImage: "wifi.exclamationmark",
                        description: Text((err as? LocalizedError)?.errorDescription ?? String(describing: err))
                    )
                    if api.error is APIError {
                        Button("Server & user settings") { showUserPicker = true }
                            .padding(.top)
                    }
                } else if api.dashboard == nil {
                    ContentUnavailableView(
                        "No data",
                        systemImage: "person.crop.circle.badge.questionmark",
                        description: Text(api.username == nil ? "Select a user to load your priority list, or use mock data." : "Pull to refresh or load mock data.")
                    )
                    Button(api.username == nil ? "Select user" : "Server & user settings") { showUserPicker = true }
                        .padding(.top)
                } else {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 24) {
                            if let status = liveStatus {
                                UrgencyMeter(score: status.overallUrgencyScore)
                                    .frame(maxWidth: .infinity)
                                    .padding(.top, 24)

                                LiveStatusCard(status: status)

                                sectionHeader("Upcoming Assignments")
                                ForEach(assignments) { assignment in
                                    AssignmentRow(assignment: assignment)
                                }
                            }
                        }
                        .padding()
                    }
                    .refreshable { await api.fetchDashboard() }
                }
            }
            .navigationTitle("Focus")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        Button("Server & user") { showUserPicker = true }
                        Button("Mock data") { api.loadMockData() }
                    } label: {
                        Image(systemName: "person.crop.circle")
                    }
                }
            }
            .sheet(isPresented: $showUserPicker) {
                UserPickerView(api: api, isPresented: $showUserPicker)
            }
        }
    }

    private func sectionHeader(_ title: String) -> some View {
        Text(title)
            .font(.headline)
            .foregroundStyle(Theme.darkBlue)
    }
}

// MARK: - Live Status Card

struct LiveStatusCard: View {
    let status: LiveStatus

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: status.isGaming ? "exclamationmark.triangle.fill" : "checkmark.circle.fill")
                .font(.title2)
                .foregroundStyle(status.isGaming ? .orange : .green)

            VStack(alignment: .leading, spacing: 4) {
                Text(status.isGaming ? "Gaming detected" : "Focus mode")
                    .font(.headline)
                if status.isGaming, let activity = status.currentActivity, !activity.isEmpty, activity.lowercased() != "none" {
                    Text(activity)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
            }
            Spacer()
        }
        .padding()
        .background(Theme.lightBlue.opacity(0.25))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

// MARK: - Assignment Row

struct AssignmentRow: View {
    let assignment: Assignment

    var body: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 4) {
                Text(assignment.title)
                    .font(.subheadline.weight(.medium))
                Text(assignment.dueDateParsed?.formatted(date: .abbreviated, time: .shortened) ?? assignment.dueDate)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            if let score = assignment.priorityScore {
                Text("P\(score)")
                    .font(.caption)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(Theme.gold.opacity(0.3))
                    .foregroundStyle(Theme.darkBlue)
                    .clipShape(Capsule())
            }
        }
        .padding()
        .background(Theme.lightBlue.opacity(0.2))
        .clipShape(RoundedRectangle(cornerRadius: 10))
    }
}

#Preview {
    FocusDashboardView(api: {
        let s = APIService()
        s.loadMockData()
        return s
    }())
}
