//
//  FolderDetailView.swift
//  Studious Seal
//
//  List of classes in a folder; add class.
//

import SwiftUI

struct FolderDetailView: View {
    @ObservedObject var store: GradeStore
    let folder: GradeFolder
    @State private var showingNewClass = false
    @State private var newClassName = ""

    private var folderClasses: [GradeClass] { store.classes(in: folder.id) }

    var body: some View {
        List {
            ForEach(folderClasses) { gradeClass in
                NavigationLink(value: gradeClass) {
                    GradeClassRow(store: store, gradeClass: gradeClass)
                }
                .contextMenu {
                    Button(role: .destructive) {
                        store.deleteClass(gradeClass)
                    } label: {
                        Label("Delete class", systemImage: "trash")
                    }
                }
            }
            .onDelete(perform: deleteClasses)
            Button {
                newClassName = ""
                showingNewClass = true
            } label: {
                Label("Add class", systemImage: "plus.circle")
            }
        }
        .navigationTitle(folder.name)
        .navigationBarTitleDisplayMode(.inline)
        .safeAreaInset(edge: .bottom) {
            GradeDisplayModeBar(store: store)
        }
        .navigationDestination(for: GradeClass.self) { gradeClass in
            ClassGradeView(store: store, gradeClass: gradeClass)
        }
        .alert("New class", isPresented: $showingNewClass) {
            TextField("Class name", text: $newClassName)
            Button("Cancel", role: .cancel) {}
            Button("Add") {
                let name = newClassName.trimmingCharacters(in: .whitespacesAndNewlines)
                if !name.isEmpty {
                    store.addClass(name: name, folderId: folder.id)
                }
            }
        } message: {
            Text("Course name for this folder.")
        }
    }

    private func deleteClasses(at offsets: IndexSet) {
        for i in offsets where i < folderClasses.count {
            store.deleteClass(folderClasses[i])
        }
    }
}

#Preview {
    NavigationStack {
        FolderDetailView(store: GradeStore(), folder: GradeFolder(name: "A-2026"))
    }
}
