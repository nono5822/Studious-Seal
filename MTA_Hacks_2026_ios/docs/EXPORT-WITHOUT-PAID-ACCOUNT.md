# Export the App Without a Paid Developer Account

Xcode’s **Distribute App** flow often pushes you toward a paid account. Here are two ways to get an **.ipa** (or equivalent) using only a **free Apple ID**.

---

## Option 1: Try Development Export with a Free Apple ID

Sometimes **Development** export works with a free (Personal Team) account.

1. **Add your Apple ID in Xcode** (if you haven’t):  
   **Xcode** → **Settings…** (⌘,) → **Accounts** → **+** → **Apple ID** → sign in with a free iCloud/Apple ID.

2. **Use your Personal Team in the project:**  
   In the project navigator, select the **Studious Seal** project → **Studious Seal** target → **Signing & Capabilities**.  
   Under **Team**, choose **Your Name (Personal Team)** (not a paid team).  
   If you see “Failed to register bundle identifier”, change the **Bundle Identifier** to something unique, e.g. `com.yourname.studiousseal`.

3. **Set destination to a device:**  
   In the scheme selector (top left), choose **Any iOS Device (arm64)**.

4. **Archive:**  
   **Product** → **Archive**.  
   - If Archive is greyed out, the scheme destination must be a device (not a simulator).  
   - If Archive fails with a signing error, try fixing the team/bundle ID and try again.

5. **Distribute:**  
   In the Organizer, select the archive → **Distribute App**.  
   - Choose **Development** (or **Custom** if you see it, then **Development** in the next step).  
   - Click **Next** and follow the steps. If it lets you choose your Personal Team and export, you’ll get an **.ipa** in the folder you choose.  
   - If it insists on a paid team or App Store Connect, use Option 2 below.

---

## Option 2: Build for Device and Create an IPA Manually

If **Distribute App** always requires a paid account, you can **build** the app for a device and then turn the built **.app** into an **.ipa** that Sideloadly or AltStore can re-sign and install.

### Step 1: Build for “Any iOS Device”

1. In Xcode, select the **Studious Seal** target.
2. **Signing & Capabilities** → **Team** → **Your Name (Personal Team)** (free Apple ID).
3. Scheme destination: **Any iOS Device (arm64)**.
4. **Product** → **Build** (⌘B). Wait until the build succeeds.

### Step 2: Find the built .app

The built app is in Xcode’s **DerivedData**:

1. **Xcode** → **Settings** → **Locations** → note the **Derived Data** path (e.g. `~/Library/Developer/Xcode/DerivedData`).
2. In Finder, open that folder. Find a folder whose name starts with **SealSensei-** or **Studious_Seal-** (or similar, based on your project name).
3. Inside it, go to:  
   **Build/Products/Release-iphoneos/**  
   (or **Debug-iphoneos** if you didn’t do a Release build).
4. You should see **Studious Seal.app**. That’s your built app.

**Easier way to open that folder:**  
**Product** → **Show Build Folder in Finder** (or **Reveal in Finder** on the **Studious Seal.app** product). Then go up to **Products** and into **Release-iphoneos** (or **Debug-iphoneos**).

### Step 3: Turn the .app into an .ipa

An IPA is a zip that contains a **Payload** folder with the **.app** inside.

**On Mac (Terminal):**

```bash
# Create a temp folder and the Payload structure
mkdir -p ~/Desktop/StudiousSealIPA/Payload
cp -r "/path/to/Studious Seal.app" ~/Desktop/StudiousSealIPA/Payload/

# Replace /path/to/ with the real path to Studious Seal.app
# Example if it's in DerivedData:
# cp -r ~/Library/Developer/Xcode/DerivedData/SealSensei-xxxxx/Build/Products/Release-iphoneos/Studious\ Seal.app ~/Desktop/StudiousSealIPA/Payload/

# Create the IPA (zip then rename)
cd ~/Desktop/StudiousSealIPA
zip -r ../StudiousSeal.ipa Payload
```

Then use **~/Desktop/StudiousSeal.ipa** in Sideloadly or AltStore.

**Or do it in Finder:**

1. Create a folder, e.g. **StudiousSealIPA** on the Desktop.
2. Inside it, create a folder named **Payload** (capital P).
3. Copy **Studious Seal.app** into **Payload** (so you have `StudiousSealIPA/Payload/Studious Seal.app`).
4. Right‑click **StudiousSealIPA** → **Compress** (or use a zip tool). You get **StudiousSealIPA.zip**.
5. Rename **StudiousSealIPA.zip** to **StudiousSeal.ipa**.

### Step 4: Install with Sideloadly or AltStore

- Open **Sideloadly** or **AltServer**.
- Use **Install .ipa** and select **StudiousSeal.ipa**.
- Sign in with your **Apple ID** (free is fine). The tool will **re-sign** the app and install it on your connected iPhone.

On the iPhone, go to **Settings** → **General** → **VPN & Device Management** and **Trust** your Apple ID if prompted.

---

## If “Run” works but you never get an IPA

If you can **Run** (⌘R) the app on your iPhone from Xcode with your free Apple ID but still can’t export an IPA:

- Use **Option 2**: do a **Build** (not Run) with destination **Any iOS Device**, then find **Studious Seal.app** in **Build/Products/Release-iphoneos** (or **Debug-iphoneos**), and create the **.ipa** as in Step 3. Sideloadly/AltStore will re-sign it so it installs on the device.

---

## Summary

| Goal | What to do |
|------|------------|
| Use a free Apple ID | Add it in Xcode → Accounts; set Team to **Personal Team** in Signing. |
| Get an IPA for Sideloadly/AltStore | Either **Distribute App** → **Development** (Option 1) or **Build** → find **.app** → make **Payload** zip and rename to **.ipa** (Option 2). |
| Install on the phone | Sideloadly or AltStore → Install .ipa → select your **.ipa** and sign in with your Apple ID. |

With a free account, the app will need to be re-sideloaded about every **7 days** (Sideloadly or AltStore can do that by installing the same .ipa again).
