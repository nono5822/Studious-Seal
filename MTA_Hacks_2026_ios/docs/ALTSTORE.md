# Install Studious Seal with AltStore

Use **AltStore** to sideload the app on your iPhone with a **free Apple ID**. You need a computer (Mac or Windows) and a USB cable for the first setup; after that you can refresh the app over the same Wi‑Fi so it doesn’t expire (free accounts: 7-day signing).

---

## Part 1: Export the IPA from Xcode

1. Open **SealSensei.xcodeproj** in Xcode.
2. Select the **Studious Seal** target → **Signing & Capabilities** → set **Team** to your Apple ID.
3. Set the run destination to **Any iOS Device (arm64)**.
4. **Product** → **Archive**.
5. In the Organizer: select the archive → **Distribute App** → **Development** → **Next** → **Export**.
6. Save the export folder. Inside it you’ll find **Studious Seal.ipa** (or similar). Keep this file for Part 3.

---

## Part 2: Install AltStore on your iPhone

### 2.1 Install AltServer (on your computer)

- **Mac:** Download from https://altstore.io → open the .dmg, drag **AltServer** to Applications.  
  - On Mac, you also need **Mail** (or the Mail plug-in): see https://altstore.io/faq/ for the Mail plug-in so AltServer can talk to the device.
- **Windows:** Download the Windows version from https://altstore.io → run the installer.

### 2.2 Put AltStore on your iPhone

1. Connect your **iPhone** to the computer with a **USB cable**. Unlock the phone and tap **Trust** if asked.
2. **Mac:** Click the AltServer icon in the menu bar → **Install AltStore** → choose your **iPhone**.  
   **Windows:** Open AltServer from the Start menu → same steps (Install AltStore → choose iPhone).
3. When asked, sign in with your **Apple ID** (free is fine). Enter the **verification code** Apple sends if required.
4. Wait until AltServer says AltStore was installed. You should see the **AltStore** app on your iPhone.

### 2.3 Trust the app on the iPhone

1. On the iPhone: **Settings** → **General** → **VPN & Device Management** (or **Device Management**).
2. Under **Developer App**, tap your Apple ID.
3. Tap **Trust "[Your Apple ID]"** → **Trust**.

Open **AltStore** on the phone once to confirm it works. You may need to be on the same Wi‑Fi as the computer (and have AltServer running) for AltStore to activate.

---

## Part 3: Install Studious Seal via AltServer

To install your own **.ipa** (Studious Seal), you use **AltServer on the computer**, not the AltStore app on the phone.

1. Connect your **iPhone** to the computer with the **USB cable** (and keep it unlocked).
2. **Mac:** In the menu bar, click the **AltServer** icon → **Install .ipa…** (or **Install IPA**).  
   **Windows:** Right‑click the **AltServer** icon in the system tray → **Install .ipa…**.
3. In the file picker, select **Studious Seal.ipa** (the one you exported in Part 1).
4. Choose your **iPhone** if asked.
5. Sign in with your **Apple ID** if AltServer asks (same one you used for AltStore).
6. Wait until you see a message that the app was installed.

### On the iPhone

1. If this is the first time: **Settings** → **General** → **VPN & Device Management** → tap your Apple ID → **Trust** (for Studious Seal / your developer certificate).
2. Open **Studious Seal** from the home screen.

---

## Refreshing the app (so it doesn’t expire)

With a **free** Apple ID, the app’s signature lasts **7 days**. After that it won’t open until you “refresh” it.

### Option A: Same Wi‑Fi (no cable after first time)

1. On the **computer**, make sure **AltServer** is running and you’re signed in.
2. **iPhone** and computer must be on the **same Wi‑Fi**.
3. Open **AltStore** on the iPhone. It will try to refresh your apps. If Studious Seal was installed via AltServer, you may need to refresh it from the computer (Option B) unless it appears in AltStore.

If Studious Seal shows in AltStore’s “My Apps”, tap the **refresh** (circular arrow) button there. Otherwise use Option B.

### Option B: Cable (always works)

1. Connect the **iPhone** to the computer with the **USB cable**.
2. On the computer: **AltServer** → **Install .ipa…** → select **Studious Seal.ipa** again.
3. AltServer will re‑install / refresh the app. It will work for another 7 days (free account) or up to 1 year (paid developer account).

Do this before the 7 days are up so the app doesn’t stop opening.

---

## Quick reference

| Step | Where | Action |
|------|--------|--------|
| 1 | Xcode | Archive → Distribute App → Development → Export → get **.ipa** |
| 2 | Computer | Install **AltServer** from altstore.io |
| 3 | Computer + iPhone (cable) | AltServer → Install AltStore → choose iPhone, sign in with Apple ID |
| 4 | iPhone | Settings → General → VPN & Device Management → Trust your Apple ID |
| 5 | Computer + iPhone (cable) | AltServer → Install .ipa… → select **Studious Seal.ipa** |
| 6 | iPhone | Trust certificate if needed, open **Studious Seal** |
| 7 | Every ~7 days (free ID) | Connect cable → AltServer → Install .ipa… → same .ipa again |

---

## Troubleshooting

| Problem | What to try |
|--------|-------------|
| “Install AltStore” greyed out | Connect the iPhone with the cable, unlock it, and trust the computer. Restart AltServer. |
| AltStore won’t open on iPhone | Turn on **Developer Mode**: Settings → Privacy & Security → Developer Mode → On (device may restart). |
| “Untrusted developer” for Studious Seal | Settings → General → VPN & Device Management → tap your Apple ID → **Trust**. |
| AltServer doesn’t see my iPhone | Use a good USB cable. On Mac, install the Mail plug-in from altstore.io/faq if required. |
| App expired / won’t open | Refresh: connect via cable, AltServer → Install .ipa… → select Studious Seal.ipa again. |

For more: https://altstore.io/faq/
