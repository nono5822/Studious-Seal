//
//  UserPickerView.swift
//  Studious Seal
//
//  Select server URL and username for the Flask API (/api/users, /api/user/<username>/priority).
//

import SwiftUI

struct UserPickerView: View {
    @ObservedObject var api: APIService
    @Binding var isPresented: Bool
    @State private var baseURLInput: String = ""
    @State private var usernameInput: String = ""
    @State private var isLoadingUsers = false

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("Server URL", text: $baseURLInput)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .keyboardType(.URL)
                    Button("Save URL") {
                        api.setBaseURL(baseURLInput)
                    }
                } header: {
                    Text("Server")
                } footer: {
                    Text("e.g. http://localhost:5000/ or your ngrok URL. Must match the Flask API.")
                }

                Section {
                    TextField("Username", text: $usernameInput)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    Button("Load user list") {
                        Task {
                            isLoadingUsers = true
                            await api.fetchUsers()
                            isLoadingUsers = false
                        }
                    }
                    .disabled(isLoadingUsers)
                    if isLoadingUsers {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    }
                    if !api.users.isEmpty {
                        ForEach(api.users, id: \.self) { user in
                            Button {
                                api.setUsername(user)
                                usernameInput = user
                                Task {
                                    await api.fetchDashboard()
                                }
                                isPresented = false
                            } label: {
                                HStack {
                                    Text(user)
                                    if api.username == user {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundStyle(Theme.gold)
                                    }
                                }
                            }
                        }
                    }
                } header: {
                    Text("User")
                } footer: {
                    Text("Type a username or tap one from the list (from /api/users).")
                }

                Section {
                    Button("Use this username") {
                        api.setUsername(usernameInput)
                        Task {
                            await api.fetchDashboard()
                        }
                        isPresented = false
                    }
                    .disabled(usernameInput.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }

                Section {
                    Button("Use mock data") {
                        api.loadMockData()
                        isPresented = false
                    }
                }
            }
            .navigationTitle("Server & User")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                baseURLInput = api.baseURLString
                usernameInput = api.username ?? ""
            }
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") {
                        isPresented = false
                    }
                }
            }
        }
    }
}

#Preview {
    UserPickerView(api: APIService(), isPresented: .constant(true))
}
