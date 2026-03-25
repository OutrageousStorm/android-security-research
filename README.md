# 🔒 Android Security Research

Notes and references on Android security internals — root detection, ADB attack surface, Magisk internals, and Shizuku architecture.

---

## Topics

- [Root Detection & Hiding](docs/root-detection.md)
- [Magisk Internals](docs/magisk-internals.md)
- [Shizuku Architecture](docs/shizuku-architecture.md)
- [ADB Attack Surface](docs/adb-attack-surface.md)

---

## Quick reference: Root detection methods

| Method | What it checks | Bypass |
|--------|---------------|--------|
| `Build.TAGS` | `test-keys` vs `release-keys` | MagiskHide / Shamiko |
| `/system/app/Superuser.apk` | File existence | Magisk mount namespace |
| `which su` | su binary in PATH | Magisk systemless root |
| `PackageManager` | Known root app package names | Magisk DenyList |
| SafetyNet / Play Integrity | Hardware attestation | Universal SafetyNet Fix |
| Frida detection | Port 27042, frida-agent libs | HTTPS tunnel / custom frida |

---

## Shizuku at a glance

Shizuku lets apps run privileged ADB shell commands without root, via a local IPC bridge:

```
App ──IPC──► Shizuku service (runs as shell UID, started via ADB or via Wireless Debugging)
              └──► executes commands as shell (uid=2000)
```

Permissions: `android.permission.WRITE_SECURE_SETTINGS`, `android.permission.WRITE_SETTINGS`, and most `pm` / `settings` commands are available to shell UID.

---

## ADB security surface

```bash
# What ADB shell can do without root:
settings put secure <key> <value>   # change secure settings
pm grant <pkg> <permission>         # grant dangerous permissions
pm disable-user --user 0 <pkg>      # disable system apps
wm density <dpi>                    # change display density
cmd package install-existing <pkg>  # install from system

# What requires root:
mount -o remount,rw /system
dd if=/dev/block/...                # raw partition access
chcon / setenforce 0                # SELinux manipulation
```

---

*Maintained by [OutrageousStorm](https://github.com/OutrageousStorm)*
