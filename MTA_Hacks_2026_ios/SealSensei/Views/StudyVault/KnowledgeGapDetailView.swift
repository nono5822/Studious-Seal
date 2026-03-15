//
//  KnowledgeGapDetailView.swift
//  Studious Seal
//
//  Detail view: question_asked, wrong_answer_given, correct_concept, youtube_link, study_reference.
//

import SwiftUI

struct KnowledgeGapDetailView: View {
    let gap: KnowledgeGap

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text(gap.topic)
                    .font(.title2.weight(.bold))

                labeledBlock("Question", gap.questionAsked)
                labeledBlock("Your answer", gap.wrongAnswerGiven)
                    .foregroundStyle(.red)
                labeledBlock("Correct concept", gap.correctConcept)
                    .foregroundStyle(.green)

                VStack(alignment: .leading, spacing: 8) {
                    Text("Study reference")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Text(gap.studyReference)
                        .font(.subheadline)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding()
                .background(Theme.lightBlue.opacity(0.25))
                .clipShape(RoundedRectangle(cornerRadius: 12))

                if let urlString = gap.youtubeLink, !urlString.isEmpty, let url = URL(string: urlString) {
                    Link(destination: url) {
                        HStack {
                            Image(systemName: "play.rectangle.fill")
                            Text("Watch on YouTube")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Theme.gold.opacity(0.3))
                        .foregroundStyle(Theme.darkBlue)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                }
            }
            .padding()
        }
        .navigationTitle("Knowledge Gap")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func labeledBlock(_ label: String, _ text: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(text)
                .font(.subheadline)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Theme.lightBlue.opacity(0.2))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

#Preview {
    NavigationStack {
        KnowledgeGapDetailView(gap: KnowledgeGap(
            gapId: "gap_001",
            classId: "BIOL-101",
            topic: "Cellular Respiration",
            questionAsked: "Where does the Krebs cycle occur?",
            wrongAnswerGiven: "Nucleus",
            correctConcept: "The Krebs cycle occurs in the mitochondrial matrix.",
            studyReference: "Syllabus.pdf - Page 14",
            youtubeLink: "https://youtube.com/results?search_query=Krebs+cycle+explained",
            status: "needs_review"
        ))
    }
}
