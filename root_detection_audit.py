#!/usr/bin/env python3
"""
root_detection_audit.py — Audit what root/jailbreak detection signals your device emits
Shows exactly what detection libraries (SafetyNet, Play Integrity, RootBeer, etc.) can see

Useful for:
  - Privacy researchers understanding device fingerprint
  - Developers testing detection robustness
  - Users wanting to know their device's "detectability score"

Usage: python3 root_detection_audit.py [--json] [--verbose]
"""
import subprocess, json, argparse, os

def adb(cmd):
    r = subprocess.run(['adb', 'shell'] + cmd.split(), capture_output=True, text=True)
    return r.stdout.strip()

def check(label, cmd, detect_strings=None, invert=False):
    """Run a check. Returns (label, passed, detail)"""
    try:
        out = adb(cmd)
        if detect_strings:
            detected = any(s.lower() in out.lower() for s in detect_strings)
            passed = not detected if invert else detected
            return (label, passed, out[:120] if out else 'empty')
        else:
            passed = bool(out.strip()) if not invert else not bool(out.strip())
            return (label, passed, out[:120])
    except Exception as e:
        return (label, False, str(e))

CHECKS = [
    # Binary presence checks
    ("su binary in /sbin",         "ls /sbin/su",                      None, False),
    ("su binary in /system/bin",   "ls /system/bin/su",                None, False),
    ("su binary in /system/xbin",  "ls /system/xbin/su",               None, False),
    ("Magisk binary",              "ls /sbin/.magisk",                  None, False),
    ("Magisk Manager pkg",         "pm list packages com.topjohnwu.magisk", ['com.topjohnwu'], False),
    ("SuperSU pkg",                "pm list packages eu.chainfire.supersu", ['eu.chainfire'], False),
    ("KernelSU pkg",               "pm list packages me.weishu.kernelsu", ['me.weishu'], False),
    # Build prop signals
    ("Build tags (test-keys)",     "getprop ro.build.tags",            ['test-keys'], False),
    ("Build type (eng/userdebug)", "getprop ro.build.type",            ['eng', 'userdebug'], False),
    ("Debuggable flag",            "getprop ro.debuggable",             ['1'], False),
    # System integrity
    ("SELinux status",             "getenforce",                        ['enforcing'], True),  # invert: permissive = detected
    ("dm-verity disabled",         "getprop ro.boot.veritymode",        ['disabled'], False),
    # Frida / Xposed presence
    ("Xposed installed",           "pm list packages de.robv.android.xposed.installer", ['de.robv'], False),
    ("LSPosed installed",          "pm list packages org.lsposed.manager", ['org.lsposed'], False),
    ("Frida server process",       "ps | grep frida",                   ['frida'], False),
    # TWRP / custom recovery
    ("TWRP recovery",              "ls /cache/recovery/last_log",       None, False),
    ("Unlocked bootloader",        "getprop ro.boot.verifiedbootstate", ['orange', 'yellow'], False),
]

def run_audit(verbose=False):
    results = []
    detected_count = 0

    for label, cmd, detect_strings, invert in CHECKS:
        lbl, detected, detail = check(label, cmd, detect_strings, invert)
        results.append({'check': lbl, 'detected': detected, 'detail': detail})
        if detected:
            detected_count += 1
        if verbose:
            icon = '🔴' if detected else '✅'
            print(f"  {icon} {lbl}")
            if detected and detail:
                print(f"     → {detail}")

    score = round((detected_count / len(CHECKS)) * 100)
    return results, detected_count, score

def main():
    parser = argparse.ArgumentParser(description='Root/jailbreak detection signal audit')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--verbose', action='store_true', help='Show detail for each check')
    args = parser.parse_args()

    if not args.json:
        print("🔬 Root Detection Signal Audit")
        print("=" * 40)
        print("Scanning what detection libraries can see on this device...\n")

    results, count, score = run_audit(verbose=not args.json)

    if args.json:
        print(json.dumps({'checks': results, 'detected': count,
                          'total': len(CHECKS), 'detectability_score': score}))
    else:
        print(f"\n{'='*40}")
        print(f"Signals detected: {count}/{len(CHECKS)}")
        grade = 'HIGH' if score >= 60 else 'MEDIUM' if score >= 30 else 'LOW'
        print(f"Detectability:    {score}% ({grade})")
        print()
        if score >= 60:
            print("⚠️  This device would likely fail Play Integrity / SafetyNet checks")
            print("   Apps using RootBeer or similar will detect root")
        elif score >= 30:
            print("🟡 Partially detectable — some apps may flag this device")
        else:
            print("✅ Low detectability — most root detection checks would pass")

if __name__ == '__main__':
    main()
