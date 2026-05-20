#!/usr/bin/env python3
"""Test if app uses Play Integrity API and detect verdict manipulation"""
import subprocess, json

def adb(cmd):
    r = subprocess.run(['adb', 'shell'] + cmd.split(), capture_output=True, text=True)
    return r.stdout.strip()

# Monitor Frida for IntegrityManager calls
FRIDA_HOOK = """
Java.perform(() => {
    const IntegrityManager = Java.use('com.google.android.play.core.integrity.IntegrityManagerImpl');
    IntegrityManager.requestIntegrityToken.overload('com.google.android.play.core.integrity.IntegrityTokenRequest')
        .implementation = function(request) {
        console.log('[INTEGRITY] requestIntegrityToken() called');
        console.log('[NONCE] ' + request.nonce());
        return this.requestIntegrityToken(request);
    };
});
"""

def test_app(pkg):
    print(f"Testing {pkg} for Play Integrity usage...")
    # frida -U -f pkg -l hook.js --no-pause
    print("[!] Run with Frida: frida -U -f " + pkg + " -l integrity_hook.js")

if __name__ == '__main__':
    import sys
    pkg = sys.argv[1] if len(sys.argv) > 1 else 'com.example.app'
    test_app(pkg)
