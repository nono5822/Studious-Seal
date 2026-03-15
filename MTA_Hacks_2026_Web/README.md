# Studious Seal — Web Dashboard

Web app for the **OpenClaw AI** study agent: urgency, live status, assignments, intervention logs, knowledge gaps, and grade calculator. Built with **React**, **TypeScript**, and **Vite**.

## Quick start

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Run the app**
   ```bash
   npm run dev
   ```

3. **Open in browser**  
   Visit the URL shown (e.g. `http://localhost:5173`). The app loads **mock data** by default so you can use it without a backend.

4. **Optional: connect to backend**  
   Use the **person** (👤) menu in any tab → **Server & user**. Set the server URL (e.g. `http://localhost:5000/`) and a username. **Load user list** fetches users from `GET /api/users`; **Use this username** loads that user’s dashboard from `GET /api/user/<username>/priority`.

## Tabs

| Tab | Content |
|-----|--------|
| **Focus** | Urgency meter (1–10), live status (gaming warning + activity), upcoming assignments by due date. |
| **Interventions** | Timeline of intervention logs: time, platform (Discord/Telegram/etc.), message, optional user reply. |
| **Study Vault** | Knowledge gaps; click one for detail: question, your answer, correct concept, study reference, **Watch on YouTube** link. |
| **Grades** | Folders (e.g. semesters), classes, weighted grade components. Display as percentage or points. Data is stored in the browser (localStorage). |

## Backend (optional)

The app expects a Flask API that exposes:

- **GET /api/users** — JSON array of usernames.
- **GET /api/user/<username>/priority** — dashboard JSON (see data contract below).

Server URL and username are stored in `localStorage`. The dashboard response must use **snake_case** keys: `user_profile`, `live_status`, `classes`, `assignments`, `intervention_logs`, `knowledge_gaps`.

## Build

```bash
npm run build
```

Output is in `dist/`. Preview the production build:

```bash
npm run preview
```

## Project layout

```
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── types/
    │   ├── dashboard.ts
    │   └── grades.ts
    ├── services/
    │   ├── api.ts
    │   └── gradeStore.ts
    ├── components/
    │   ├── UrgencyMeter.tsx
    │   └── UserPicker.tsx
    └── views/
        ├── FocusDashboard.tsx
        ├── InterventionFeed.tsx
        ├── StudyVault.tsx
        └── GradeCalculator.tsx
```
