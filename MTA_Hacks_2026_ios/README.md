# Studious Seal — iOS Dashboard

Remote control and dashboard for the **OpenClaw AI** study agent. Displays urgency, live status, assignments, intervention logs, and knowledge gaps. Built with **SwiftUI** for **iOS 17+**.

## Quick start

1. **Open in Xcode**  
   Open `SealSensei.xcodeproj` (Studious Seal project) in Xcode.

2. **Run**  
   Select a simulator or device (iOS 17+) and press **Run** (⌘R).

3. **Mock data**  
   With no backend, tap the **person** icon in the top-right of Focus/Interventions/Study Vault → **Mock data** to load sample data.

4. **Backend (Flask API)**  
   Tap the **person** icon → **Server & user**. Set the server URL (e.g. `http://localhost:5000/` or your ngrok URL) and a username. Use **Load user list** to fetch users from `/api/users`, or type a username and tap **Use this username**. The app then loads that user’s data from `GET /api/user/<username>/priority` (the backend’s `priority_list.json` must match the [data contract](#data-contract)).

## Backend (Flask Study Sensei API Bridge)

The app is built for the Flask API that exposes:

- **GET /api/users** — returns a JSON array of usernames (workspace folders under `~/.openclaw/workspace`).
- **GET /api/user/<username>/priority** — returns the user’s `priority_list.json` (dashboard JSON).

Server URL and selected username are stored on device. Default base URL is `http://localhost:5000/`. Change it in the app via **Server & user** (e.g. to your ngrok URL for a device). The file served at `priority_list.json` must match the [data contract](#data-contract).

## App structure (3 tabs)

| Tab | Content |
|-----|--------|
| **Focus** | Urgency meter (1–10, red when 8+), live status (gaming warning + activity), upcoming assignments by due date. |
| **Interventions** | Timeline of `intervention_logs`: time, platform (Discord/Telegram/etc.), message, optional user reply. |
| **Study Vault** | List of `knowledge_gaps`; tap one for detail: question, your answer, correct concept, study reference (e.g. “Syllabus.pdf - Page 14”), and a **Watch on YouTube** button. |

## Data contract

The backend should serve JSON in this shape (snake_case). The app uses `Codable` models in `SealSensei/Models/DashboardData.swift`:

- `user_profile`: `user_id`, `name`, `linked_platforms`
- `live_status`: `overall_urgency_score`, `is_gaming`, `current_activity`, `last_active_platform`, `last_ping_timestamp`
- `classes`: array of `class_id`, `name`, `professor`, `syllabus_parsed`
- `assignments`: array of `assignment_id`, `class_id`, `title`, `due_date`, `priority_score`, `status`, `type`
- `intervention_logs`: array of `log_id`, `timestamp`, `platform`, `trigger`, `message_sent`, `user_reply`
- `knowledge_gaps`: array of `gap_id`, `class_id`, `topic`, `question_asked`, `wrong_answer_given`, `correct_concept`, `study_reference`, `youtube_link`, `status`

## Project layout

```
SealSensei/
├── SealSenseiApp.swift          # @main
├── Views/
│   ├── MainTabView.swift        # 3-tab TabView
│   ├── Components/
│   │   └── UrgencyMeter.swift   # 1–10 gauge, red pulse when 8+
│   ├── FocusDashboard/
│   │   └── FocusDashboardView.swift
│   ├── InterventionFeed/
│   │   └── InterventionFeedView.swift
│   └── StudyVault/
│       ├── StudyVaultView.swift
│       └── KnowledgeGapDetailView.swift
├── Models/
│   └── DashboardData.swift      # Codable types
├── Services/
│   └── APIService.swift         # URLSession GET + mock
└── Assets.xcassets
```

## TestFlight

- Set **Deployment Target** to **iOS 17.0** (already set in the project).
- Configure signing and build for **TestFlight** as usual (Archive → Distribute App → App Store Connect).
