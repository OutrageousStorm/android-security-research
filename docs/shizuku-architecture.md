# Shizuku Architecture

How Shizuku works under the hood — for developers and security researchers.

**Official repo:** https://github.com/RikkaApps/Shizuku

---

## Overview

Shizuku is an Android library + companion app that allows third-party apps to call system APIs directly, running with the `shell` UID (uid=2000) — without requiring root.

---

## Architecture

```
┌─────────────────────────────────┐
│         Your App                │
│  ShizukuProvider (ContentProvider)│
│  Shizuku.bindUserService(...)   │
└────────────────┬────────────────┘
                 │  Binder IPC
                 ▼
┌─────────────────────────────────┐
│     Shizuku Server              │
│     (runs as shell UID 2000)    │
│                                 │
│  Started via:                   │
│  • adb shell sh /path/start.sh  │
│  • Wireless Debugging (API 30+) │
└─────────────────────────────────┘
```

---

## How it starts

**Via ADB:**
```bash
adb push shizuku.jar /data/local/tmp/
adb shell sh /data/local/tmp/start.sh
```

**Via Wireless Debugging (Android 11+):**  
Shizuku can start itself by pairing with the local Wireless Debugging service — no computer needed after first setup.

---

## What shell UID can do

The `shell` user (uid=2000) has access to:
- `android.permission.WRITE_SECURE_SETTINGS` (grantable via `pm grant`)
- `android.permission.WRITE_SETTINGS`
- Most `pm` subcommands
- `settings` get/put/delete
- `dumpsys` output
- `am` activity/broadcast commands
- `wm` display commands
- `device_config` namespace reads/writes

---

## UserService pattern

Apps can run their own code in a Shizuku-managed process:

```kotlin
val args = Shizuku.UserServiceArgs(
    ComponentName(packageName, MyService::class.java.name)
).daemon(false).version(1)

Shizuku.bindUserService(args, connection)
```

The service class must implement an AIDL interface. It runs in a separate process with shell UID permissions.

---

## Security considerations

- Shizuku server only accepts connections from apps that have been granted permission by the user
- Permission is per-app and can be revoked in the Shizuku app
- The server binds to a local abstract socket — not exposed over network
- Compared to root: significantly smaller attack surface; no `su` binary, no kernel-level privilege
