# Testing Studious Seal on Your Phone via TestFlight

## Prerequisites

- **Apple Developer Program** membership ($99/year). Sign up at [developer.apple.com](https://developer.apple.com/programs/).
- Your **Apple ID** added to the team in Xcode (same account as Developer Program).
- **Xcode** on your Mac (full Xcode from the Mac App Store, not only Command Line Tools).

---

## 1. Configure the app in Xcode

1. Open **SealSensei.xcodeproj** in Xcode.
2. Select the **Studious Seal** project in the left sidebar (blue icon).
3. Select the **Studious Seal** target → **Signing & Capabilities**.
4. Under **Team**, choose your Apple Developer team (your account).
5. If you see “Failed to register bundle identifier”, click **Register** or change **Bundle Identifier** to something unique (e.g. `com.yourname.sealsensei`).
6. Connect your iPhone with a cable (or use a wireless connection). Unlock the phone and tap **Trust** if asked.

---

## 2. Create the app in App Store Connect (first time only)

1. Go to [App Store Connect](https://appstoreconnect.apple.com) and sign in with your Apple Developer account.
2. Click **My Apps** → **+** → **New App**.
3. Choose **iOS**, enter a name (e.g. **Studious Seal**), language, bundle ID (must match the one in Xcode, e.g. `com.sealsensei.app` or `com.yourname.studiousseal`), and SKU (e.g. `studiousseal1`). Create the app.

You only do this once per app.

---

## 3. Archive and upload the build

1. In Xcode, set the run destination to **Any iOS Device (arm64)** (not a simulator) in the scheme selector at the top.
2. Menu: **Product** → **Archive**.
3. When the Organizer window opens, select the new archive and click **Distribute App**.
4. Choose **App Store Connect** → **Next**.
5. Choose **Upload** → **Next**.
6. Leave options as default (e.g. upload symbols) → **Next**.
7. Select your distribution certificate / team if asked → **Upload**.
8. Wait until the upload finishes. You’ll see “Upload Successful”.

---

## 4. Add the build in TestFlight (on the web)

1. In **App Store Connect**, open **My Apps** → **Studious Seal**.
2. Go to the **TestFlight** tab.
3. Under **iOS**, wait until the build appears (status “Processing”, then “Ready to Test”). This can take 5–30 minutes.
4. When the build is **Ready to Test**:
   - **Internal testing:** Add yourself (and teammates) as internal testers. They use the same Apple ID as in your team.
   - **External testing:** Create a group, add the build, add testers by email. Each tester must accept the email invite.

---

## 5. Install on your phone

### If you’re an internal tester

1. On your iPhone, install **TestFlight** from the App Store (if you don’t have it).
2. Sign in to TestFlight with the **same Apple ID** you use in App Store Connect / Xcode.
3. Open TestFlight. Your app (**Studious Seal**) should appear.
4. Tap **Install** and accept any prompts. The app will install like a normal app.

### If you’re an external tester

1. Accept the **TestFlight invitation email** on your phone (or open the link on the device where you want to install).
2. Install **TestFlight** from the App Store if needed.
3. In TestFlight, tap **Accept** for Studious Seal, then **Install**.

---

## Quick checklist

| Step | Where | What |
|------|--------|------|
| 1 | Xcode | Set Team + Bundle ID, connect iPhone |
| 2 | App Store Connect | Create app (once), match Bundle ID |
| 3 | Xcode | Product → Archive → Distribute → Upload |
| 4 | App Store Connect | TestFlight tab → wait for “Ready to Test” |
| 5 | iPhone | Open TestFlight → Install Studious Seal |

---

## Troubleshooting

- **“No accounts with App Store Connect access”**  
  Sign in in Xcode: **Xcode** → **Settings** → **Accounts** → **+** → Apple ID (your developer account).

- **“Bundle ID already in use”**  
  Change the bundle ID in Xcode (e.g. to `com.yourname.studiousseal`) and create the app in App Store Connect with that same ID.

- **Build stays “Processing”**  
  Wait up to ~30 minutes. If it stays for hours, check email for messages from Apple (e.g. compliance or signing issues).

- **App doesn’t show in TestFlight**  
  Make sure you’re signed into TestFlight with the Apple ID that was added as a tester (internal or external).

- **“Unable to install” on device**  
  Delete the app, restart the phone, and install again from TestFlight. Ensure the build is “Ready to Test” and not expired.

TestFlight builds expire after 90 days; upload a new build when needed.
