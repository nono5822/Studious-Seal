# Sideload Studious Seal (No Paid Developer Account)

Use **Sideloadly** or **AltStore** to install the app on an iPhone with a **free Apple ID**. The device must connect to a computer **once** to install. With a free account, the app expires after **7 days** and must be reinstalled (or use a paid developer account for 1-year signing).

---

## Part 1: Create an IPA in Xcode

1. Open **SealSensei.xcodeproj** in Xcode.
2. Select the **Studious Seal** target → **Signing & Capabilities** → set **Team** to your Apple ID (Personal Team is fine).
3. In the scheme/destination dropdown (top left), choose **Any iOS Device (arm64)** — not a simulator.
4. Menu: **Product** → **Archive**.
5. When the Organizer opens, select the new archive → **Distribute App**.
6. Choose **Development** (or **Ad Hoc** if you’ve registered the device) → **Next**.
7. Select your team/signing options → **Next** → **Export**.
8. Pick a folder and export. You’ll get a folder containing **Studious Seal.ipa** (or the .ipa inside that folder).

Keep this **.ipa** file — you’ll load it in Sideloadly or AltStore.

---

## Part 2A: Install with Sideloadly

### On your Mac

1. Download **Sideloadly** for Mac: https://sideloadly.io
2. Install and open Sideloadly.
3. Connect the **iPhone** with a USB cable. Unlock the device and tap **Trust** if asked.
4. (Optional) On the iPhone: **Settings** → **Privacy & Security** → **Developer Mode** → **On** (required on some iOS versions for sideloaded apps to run).
5. In Sideloadly:
   - **IPA**: Click and select your **Studious Seal.ipa** (or the .ipa inside the exported folder).
   - **Apple Account**: Sign in with the **Apple ID** that will be used to sign the app (free or paid).
   - **Device**: Your iPhone should appear; select it.
6. Click **Start** (or **Sideload**).
7. If Apple sends a **verification code** to your email/device, enter it when Sideloadly asks.
8. Wait until you see a success message.

### On the iPhone

1. **Settings** → **General** → **VPN & Device Management** (or **Device Management**).
2. Under **Developer App**, tap your Apple ID.
3. Tap **Trust "[Your Apple ID]"** → **Trust**.
4. Open **Studious Seal** from the home screen.

---

## Part 2B: Install with AltStore (alternative)

1. Download **AltServer** (Mac/Windows): https://altstore.io
2. Install **AltServer**, then install **AltStore** on your iPhone (via cable; follow AltStore’s instructions).
3. In AltStore on the iPhone, you can install an IPA if you have it on a server or use AltServer to “sideload” the IPA from your computer (AltServer → Install .ipa and choose your file).
4. Trust the profile: **Settings** → **General** → **VPN & Device Management** → trust the developer.

---

## Reinstalling after 7 days (free Apple ID)

With a **free** Apple ID, the app stops opening after **7 days**. To keep using it:

1. Connect the iPhone to the computer again.
2. Open Sideloadly (or AltStore), load the same **.ipa**, sign in with the same Apple ID.
3. Click **Start** / **Sideload** again. This refreshes the signing; the app will run for another 7 days.

You can do this as often as you need. With a **paid** Apple Developer account, sideloaded apps can last **1 year** before needing a refresh.

---

## Sharing the app with someone else

- They need a **Mac or Windows PC** with Sideloadly (or AltServer for AltStore) and a **USB cable** to connect their iPhone.
- Send them the **.ipa** file (e.g. via cloud link). They load it in Sideloadly, sign in with **their** Apple ID, and sideload to their device.
- They must **trust** the developer certificate on their iPhone (Settings → General → VPN & Device Management).
- With a free Apple ID, they’ll need to reconnect and re-sideload every 7 days if they want to keep using the app.

---

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| “No devices” in Xcode | Register the device: [developer.apple.com](https://developer.apple.com/account) → Certificates, Identifiers & Profiles → Devices → add the iPhone’s UDID. Get UDID from Xcode → Window → Devices and Simulators. |
| Archive / Export disabled | Set **Team** in Signing & Capabilities and choose **Any iOS Device** as the run destination. |
| App won’t open on device | Enable **Developer Mode** (Settings → Privacy & Security). Trust the app in **VPN & Device Management**. |
| “Untrusted developer” | Settings → General → VPN & Device Management → tap your Apple ID → **Trust**. |
