//
//  ClassGradeView.swift
//  Studious Seal
//
//  Grade components for one class; weights and grades; overall; add/edit components.
//

import SwiftUI

struct ClassGradeView: View {
    @ObservedObject var store: GradeStore
    let gradeClass: GradeClass
    @State private var showingNewComponent = false
    @State private var editingComponent: GradeComponent?
    @State private var newName = ""
    @State private var newWeight = ""
    @State private var newEarned = ""
    @State private var newMax = ""

    private var comps: [GradeComponent] { store.components(for: gradeClass.id) }
    private var overall: Double? { store.overallPercentage(for: gradeClass.id) }

    var body: some View {
        List {
            if let overall = overall {
                Section {
                    HStack {
                        Text("Overall")
                        Spacer()
                        Text(store.displayMode == .percentage
                             ? String(format: "%.1f%%", overall)
                             : String(format: "%.1f / 100", overall))
                            .fontWeight(.semibold)
                            .foregroundStyle(colorForGrade(overall))
                    }
                }
            }

            Section("Graded items") {
                ForEach(comps) { comp in
                    GradeComponentRow(store: store, component: comp, displayMode: store.displayMode)
                        .contentShape(Rectangle())
                        .onTapGesture {
                            editingComponent = comp
                            newName = comp.name
                            newWeight = String(format: "%.0f", comp.weightPercent)
                            newEarned = String(format: "%.1f", comp.earnedPoints)
                            newMax = String(format: "%.1f", comp.maxPoints)
                        }
                        .contextMenu {
                            Button(role: .destructive) {
                                store.deleteComponent(comp)
                            } label: {
                                Label("Delete", systemImage: "trash")
                            }
                        }
                }
                .onDelete(perform: deleteComponents)
                Button {
                    editingComponent = nil
                    newName = ""
                    newWeight = ""
                    newEarned = ""
                    newMax = ""
                    showingNewComponent = true
                } label: {
                    Label("Add graded item", systemImage: "plus.circle")
                }
            }
        }
        .navigationTitle(gradeClass.name)
        .navigationBarTitleDisplayMode(.inline)
        .safeAreaInset(edge: .bottom) {
            GradeDisplayModeBar(store: store)
        }
        .alert(editingComponent == nil ? "New graded item" : "Edit item", isPresented: Binding(
            get: { showingNewComponent || editingComponent != nil },
            set: { if !$0 { showingNewComponent = false; editingComponent = nil } }
        )) {
            TextField("Name", text: $newName)
            TextField("Weight %", text: $newWeight)
                .keyboardType(.decimalPad)
            TextField("Earned", text: $newEarned)
                .keyboardType(.decimalPad)
            TextField("Max", text: $newMax)
                .keyboardType(.decimalPad)
            Button("Cancel", role: .cancel) {
                editingComponent = nil
            }
            Button(editingComponent == nil ? "Add" : "Save") {
                saveComponent()
            }
        } message: {
            Text("Weight is the percentage of the final grade (e.g. 30 for 30%). Enter earned and max points.")
        }
    }

    private func saveComponent() {
        let name = newName.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !name.isEmpty,
              let w = Double(newWeight), w >= 0, w <= 100,
              let earned = Double(newEarned), earned >= 0,
              let max = Double(newMax), max > 0 else { return }
        if let existing = editingComponent {
            var updated = existing
            updated.name = name
            updated.weightPercent = w
            updated.earnedPoints = earned
            updated.maxPoints = max
            store.updateComponent(updated)
        } else {
            store.addComponent(classId: gradeClass.id, name: name, weightPercent: w, earnedPoints: earned, maxPoints: max)
        }
        editingComponent = nil
    }

    private func deleteComponents(at offsets: IndexSet) {
        for i in offsets where i < comps.count {
            store.deleteComponent(comps[i])
        }
    }

    private func colorForGrade(_ pct: Double) -> Color {
        if pct >= 90 { return .green }
        if pct >= 80 { return .blue }
        if pct >= 70 { return .orange }
        return .red
    }
}

struct GradeComponentRow: View {
    @ObservedObject var store: GradeStore
    let component: GradeComponent
    let displayMode: GradeDisplayMode

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text(component.name)
                    .font(.subheadline.weight(.medium))
                Text("\(Int(component.weightPercent))% weight")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            Text(displayMode == .percentage
                 ? String(format: "%.1f%%", component.percentage)
                 : String(format: "%.1f / %.1f", component.earnedPoints, component.maxPoints))
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .padding(.vertical, 2)
    }
}

#Preview {
    NavigationStack {
        ClassGradeView(store: GradeStore(), gradeClass: GradeClass(name: "Programming I", folderId: UUID()))
    }
}
