//
//  GradeCalculatorTabView.swift
//  Studious Seal
//
//  Tab: Folders (e.g. semesters), unfiled classes, display mode (points / percentage).
//

import SwiftUI

struct GradeCalculatorTabView: View {
    @ObservedObject var api: APIService
    @StateObject private var store = GradeStore()
    @State private var showingNewFolder = false
    @State private var newFolderName = ""
    @State private var showingNewUnfiledClass = false
    @State private var newUnfiledClassName = ""
    @State private var showUserPicker = false

    var body: some View {
        NavigationStack {
            List {
                Section("Folders") {
                    ForEach(store.folders) { folder in
                        NavigationLink(value: folder) {
                            Label(folder.name, systemImage: "folder.fill")
                        }
                        .dropDestination(for: GradeClass.self) { droppedClasses, _ in
                            guard let c = droppedClasses.first else { return false }
                            store.moveClass(c, toFolderId: folder.id)
                            return true
                        }
                    }
                    .onDelete(perform: deleteFolders)
                    Button {
                        newFolderName = ""
                        showingNewFolder = true
                    } label: {
                        Label("New folder", systemImage: "folder.badge.plus")
                    }
                }

                Section("Unfiled classes") {
                    if !store.unfiledClasses().isEmpty {
                        ForEach(store.unfiledClasses()) { gradeClass in
                            NavigationLink(value: gradeClass) {
                                GradeClassRow(store: store, gradeClass: gradeClass)
                            }
                            .draggable(gradeClass)
                            .contextMenu {
                                if !store.folders.isEmpty {
                                    Menu {
                                        ForEach(store.folders) { folder in
                                            Button(folder.name) {
                                                store.moveClass(gradeClass, toFolderId: folder.id)
                                            }
                                        }
                                    } label: {
                                        Label("Move to folder", systemImage: "folder")
                                    }
                                }
                            }
                        }
                        .onDelete(perform: deleteUnfiledClasses)
                    }
                    Button {
                        showingNewUnfiledClass = true
                    } label: {
                        Label("Add class (no folder)", systemImage: "plus.circle.dashed")
                    }
                }
            }
            .navigationTitle("Grades")
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
            .safeAreaInset(edge: .bottom) {
                GradeDisplayModeBar(store: store)
            }
            .navigationDestination(for: GradeFolder.self) { folder in
                FolderDetailView(store: store, folder: folder)
            }
            .navigationDestination(for: GradeClass.self) { gradeClass in
                ClassGradeView(store: store, gradeClass: gradeClass)
            }
            .alert("New folder", isPresented: $showingNewFolder) {
                TextField("Folder name", text: $newFolderName)
                    .textInputAutocapitalization(.characters)
                Button("Cancel", role: .cancel) {}
                Button("Add") {
                    let name = newFolderName.trimmingCharacters(in: .whitespacesAndNewlines)
                    if !name.isEmpty {
                        store.addFolder(name: name)
                    }
                }
            } message: {
                Text("Name")
            }
            .alert("New class", isPresented: $showingNewUnfiledClass) {
                TextField("Class name", text: $newUnfiledClassName)
                Button("Cancel", role: .cancel) {}
                Button("Add") {
                    let name = newUnfiledClassName.trimmingCharacters(in: .whitespacesAndNewlines)
                    if !name.isEmpty {
                        store.addClass(name: name, folderId: nil)
                    }
                }
            } message: {
                Text("You can move this class into a folder later by opening a folder and adding classes there.")
            }
        }
    }

    private func deleteFolders(at offsets: IndexSet) {
        for i in offsets {
            store.deleteFolder(store.folders[i])
        }
    }

    private func deleteUnfiledClasses(at offsets: IndexSet) {
        let unfiled = store.unfiledClasses()
        for i in offsets where i < unfiled.count {
            store.deleteClass(unfiled[i])
        }
    }
}

// MARK: - Bottom display mode bar (shared across Grades tab screens)

struct GradeDisplayModeBar: View {
    @ObservedObject var store: GradeStore

    var body: some View {
        Picker("Display as", selection: Binding(
            get: { store.displayMode },
            set: { store.setDisplayMode($0) }
        )) {
            Text("Percentage").tag(GradeDisplayMode.percentage)
            Text("Points").tag(GradeDisplayMode.points)
        }
        .pickerStyle(.segmented)
        .padding(.horizontal)
        .padding(.vertical, 10)
        .background(Theme.darkBlue.opacity(0.95))
        .foregroundStyle(.white)
    }
}

struct GradeClassRow: View {
    @ObservedObject var store: GradeStore
    let gradeClass: GradeClass

    var body: some View {
        HStack {
            Text(gradeClass.name)
            Spacer()
            if let overall = store.overallPercentage(for: gradeClass.id) {
                Text(store.displayMode == .percentage ? "\(Int(overall))%" : String(format: "%.1f", overall))
                    .foregroundStyle(.secondary)
            }
        }
    }
}

#Preview {
    GradeCalculatorTabView(api: APIService())
}
