#!/usr/bin/env python3
"""Detect if Play Integrity bypasses are active on the device"""
import subprocess
def adb(cmd):
    return subprocess.run(['adb', 'shell'] + cmd.split(), capture_output=True, text=True).stdout.strip()
indicators = [
    ('Frida process', 'ps | grep frida'),
    ('Xposed framework', 'pm list packages | grep xposed'),
    ('MagiskHide', 'magiskhide --status'),
    ('Zygisk module', 'ls /data/adb/modules'),
]
print("🔍 Play Integrity Bypass Detection\n")
for name, cmd in indicators:
    result = adb(cmd)
    detected = bool(result and 'not found' not in result.lower())
    print(f"{'⚠️' if detected else '✅'} {name}: {result[:60] if detected else 'Not detected'}")
