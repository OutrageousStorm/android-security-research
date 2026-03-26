# Root Detection & Bypass

How apps detect root, and how to hide it.

---

## Detection methods (roughly ordered by sophistication)

### 1. File system checks
```java
// Check for su binary
String[] paths = {"/sbin/su", "/system/bin/su", "/system/xbin/su",
                  "/data/local/tmp/su", "/data/local/su"};
for (String path : paths) {
    if (new File(path).exists()) return true;
}

// Check for Magisk files
if (new File("/sbin/.magisk").exists()) return true;
if (new File("/data/adb/magisk").exists()) return true;
```

**Bypass:** Magisk's mount namespace isolation hides these from apps.

### 2. Package manager checks
```java
// Known root-related package names
String[] packages = {
    "com.topjohnwu.magisk",
    "eu.chainfire.supersu",
    "com.koushikdutta.superuser",
    "com.noshufou.android.su",
    "com.zachspong.temprootremovejb",
};
for (String pkg : packages) {
    try {
        pm.getPackageInfo(pkg, 0);
        return true;  // package found
    } catch (PackageManager.NameNotFoundException ignored) {}
}
```

**Bypass:** Magisk DenyList hides packages from scoped apps. LSPosed + Hide My AppList for deeper hiding.

### 3. Build property checks
```java
// Check for test-keys build (rooted/custom ROMs often have this)
String buildTags = Build.TAGS;
if (buildTags != null && buildTags.contains("test-keys")) return true;

// Check for debug builds
if (Build.TYPE.equals("eng") || Build.TYPE.equals("userdebug")) return true;
```

**Bypass:** Magisk patches `ro.build.tags` to `release-keys` via the systemless mount.

### 4. Runtime exec checks
```java
// Try to run su and see if it works
try {
    Process p = Runtime.getRuntime().exec("su");
    // if no exception, su is accessible
    return true;
} catch (IOException e) {
    return false;
}
```

**Bypass:** Magisk's DenyList prevents `su` from being found in the PATH for scoped apps.

### 5. Native library detection
Advanced apps use JNI to call native code that scans `/proc/self/maps` for Magisk or Frida libraries:
```c
// Check /proc/self/maps for suspicious libraries
FILE* maps = fopen("/proc/self/maps", "r");
while (fgets(line, sizeof(line), maps)) {
    if (strstr(line, "magisk") || strstr(line, "frida")) {
        return true;
    }
}
```

**Bypass:** Shamiko + Zygisk intercepts this at the ptrace level.

### 6. Play Integrity API (strongest)
Google's hardware-backed attestation:
- **MEETS_BASIC_INTEGRITY** — passes if device isn't obviously modified
- **MEETS_DEVICE_INTEGRITY** — requires Google certification + locked bootloader
- **MEETS_STRONG_INTEGRITY** — hardware attestation, very hard to fake

**Bypass:** 
- `PlayIntegrityFix` module (Magisk/KernelSU) — spoofs device properties
- `TrickyStore` (LSPosed) — hardware attestation spoofing for banking apps
- KernelSU has inherently better evasion since it has no userspace artifacts

---

## Recommended evasion stack (2025)

```
KernelSU  →  ZygiskNext  →  PlayIntegrityFix  →  TrickyStore
```

Or with Magisk:
```
Magisk  →  Zygisk  →  Shamiko  →  PlayIntegrityFix  →  TrickyStore
         └→ Hide My AppList (via LSPosed)
```

---

## Testing root detection

Check if your setup passes:
- **Banking apps** — try opening your bank app
- **YASNAC** (F-Droid) — Play Integrity checker
- **Play Integrity API Checker** (Play Store)
- **RootBeer Sample** (Play Store) — tests multiple detection vectors
