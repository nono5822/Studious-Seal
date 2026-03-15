//
//  InterventionFeedView.swift
//  Studious Seal
//
//  Tab 2: Timeline of intervention_logs (timestamp, platform, message).
//

import SwiftUI

struct InterventionFeedView: View {
    @ObservedObject var api: APIService
    @State private var showUserPicker = false

    private var logs: [InterventionLog] {
        (api.dashboard?.interventionLogs ?? []).sorted { a, b in
            (a.timestampParsed ?? .distantPast) > (b.timestampParsed ?? .distantPast)
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if api.isLoading {
                    ProgressView("Loading…")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if api.dashboard == nil, api.error == nil {
                    ContentUnavailableView(
                        "No data",
                        systemImage: "bubble.left.and.bubble.right",
                        description: Text(api.username == nil ? "Select a user in Focus tab to load data." : "Interventions will appear here.")
                    )
                } else {
                    ScrollView {
                        LazyVStack(alignment: .leading, spacing: 0) {
                            ForEach(logs) { log in
                                InterventionLogRow(log: log)
                            }
                        }
                        .padding()
                    }
                    .refreshable { await api.fetchDashboard() }
                }
            }
            .navigationTitle("Interventions")
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
}

struct InterventionLogRow: View {
    let log: InterventionLog

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            platformIcon(log.platform)
                .font(.title2)
                .foregroundStyle(platformColor(log.platform))
                .frame(width: 32, alignment: .center)

            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text(log.timestampParsed?.formatted(date: .abbreviated, time: .shortened) ?? log.timestamp)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text(log.platform.capitalized)
                        .font(.caption)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(platformColor(log.platform).opacity(0.2))
                        .clipShape(Capsule())
                }
                Text(log.messageSent)
                    .font(.subheadline)
                if let reply = log.userReply, !reply.isEmpty {
                    Text("You: \(reply)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .italic()
                }
            }
            Spacer(minLength: 0)
        }
        .padding()
        .background(Theme.lightBlue.opacity(0.25))
        .clipShape(RoundedRectangle(cornerRadius: 12))
        .padding(.vertical, 4)
    }

    private func platformIcon(_ platform: String) -> Image {
        switch platform.lowercased() {
        case "discord": return Image(systemName: "bubble.left.fill")
        case "telegram": return Image(systemName: "paperplane.fill")
        case "whatsapp": return Image(systemName: "message.fill")
        default: return Image(systemName: "message.fill")
        }
    }

    private func platformColor(_ platform: String) -> Color {
        switch platform.lowercased() {
        case "discord": return Color(red: 0.4, green: 0.5, blue: 0.9)
        case "telegram": return Color(red: 0.2, green: 0.6, blue: 0.9)
        case "whatsapp": return Color.green
        default: return .blue
        }
    }
}

#Preview {
    InterventionFeedView(api: {
        let s = APIService()
        s.loadMockData()
        return s
    }())
}
