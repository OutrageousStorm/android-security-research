# ADB Attack Surface

What an attacker (or you) can do with ADB access to an Android device.

---

## Threat model

ADB access = **shell user (uid=2000)** on a non-rooted device.

This is less than root but significantly more than a normal app:
- Access to most `pm`, `am`, `settings`, `dumpsys` commands
- Can install/uninstall apps
- Can read app data (if app allows backup)
- Can execute shell commands
- **Cannot** read `/data/data/<package>` for most apps (SELinux blocks it)
- **Cannot** access Secure Enclave, keystore keys

---

## What ADB can do without root

```bash
# Install malicious APK silently (physical access only)
adb install malware.apk

# Grant itself dangerous permissions
adb shell pm grant com.malware.app android.permission.READ_CONTACTS
adb shell pm grant com.malware.app android.permission.ACCESS_FINE_LOCATION
adb shell pm grant com.malware.app android.permission.RECORD_AUDIO

# Enable accessibility service (captures screen, input)
adb shell settings put secure enabled_accessibility_services com.malware/.AccessibilityService

# Dump SMS database (some devices, if backup allowed)
adb backup -noapk com.android.providers.telephony

# Dump contacts
adb shell content query --uri content://contacts/phones/

# Screen capture (visual surveillance)
adb exec-out screencap -p > screen.png

# Screen record
adb shell screenrecord /sdcard/capture.mp4

# Inject key events (bypass PIN via brute force attempt)
adb shell input keyevent ...

# Forward ports (expose local services)
adb forward tcp:8080 tcp:8080

# Read notification log
adb shell dumpsys notification | grep "NotificationRecord"
```

---

## Protecting against rogue ADB

### Physical security
- **Disable USB debugging** when not in use (requires device unlock to re-enable)
- **Lock screen timeout** — short timeout limits physical access window

### Android settings
- Settings → Developer Options → **Revoke USB debugging authorizations** (removes trusted PCs)
- Settings → Developer Options → **USB configuration → No data transfer** (charges only)

### Android 14+ protection
- Developer options now require re-entering PIN/password to enable on some OEMs

### ADB over Wi-Fi risks
If `adb tcpip 5555` is enabled:
- Anyone on the same network can connect (if no auth)
- Android 11+ requires pairing code for wireless ADB — safer

```bash
# Check if TCP ADB is listening (on device)
adb shell netstat -tulnp | grep 5555

# Disable wireless ADB
adb shell setprop service.adb.tcp.port -1
adb shell stop adbd && adb shell start adbd
```

---

## Wireless ADB forensics

```bash
# Scan for open ADB ports on local network
nmap -p 5555 192.168.1.0/24

# Connect without authorization (pre-Android 11)
adb connect 192.168.1.100:5555

# After Android 11 — requires pairing
adb pair 192.168.1.100:<pair-port> <pair-code>
```

---

## ADB via Shizuku (non-physical)

Shizuku lets apps access the ADB shell **without USB** — started once via USB or wireless debugging, then persists. The attack surface:

- Apps with Shizuku permission have full shell-level access
- Only grant Shizuku to apps you trust completely
- Shizuku permission is per-app and must be explicitly granted in the Shizuku UI
