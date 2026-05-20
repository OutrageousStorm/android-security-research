#!/usr/bin/env python3
"""
Scan repositories for leaked secrets (AWS keys, API tokens, etc)
Prevents CISA-style AWS key dumps on GitHub
Usage: python3 secrets_scanner.py [--path .] [--report secrets.json]
"""
import os, re, json, argparse

PATTERNS = {
    'AWS_KEY': re.compile(r'AKIA[0-9A-Z]{16}'),
    'AWS_SECRET': re.compile(r'aws_secret_access_key\s*=\s*(.{40})'),
    'GITHUB_TOKEN': re.compile(r'ghp_[A-Za-z0-9_]{36}'),
    'API_KEY': re.compile(r'api[_-]?key[\'\"\s:=]+([A-Za-z0-9]{32,})', re.IGNORECASE),
    'PRIVATE_KEY': re.compile(r'-----BEGIN (RSA|PRIVATE|EC) PRIVATE KEY-----'),
    'SLACK_TOKEN': re.compile(r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[A-Za-z0-9-]*'),
    'STRIPE_KEY': re.compile(r'sk_live_[A-Za-z0-9]{24}'),
}

SKIP_DIRS = {'.git', 'node_modules', '.venv', '__pycache__', '.github', 'dist', 'build'}
SKIP_EXTS = {'.png', '.jpg', '.pdf', '.zip', '.bin', '.so', '.o', '.class'}

def scan_file(path):
    findings = []
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for pattern_name, regex in PATTERNS.items():
                    if regex.search(line):
                        findings.append({
                            'file': path,
                            'line': line_num,
                            'type': pattern_name,
                            'snippet': line.strip()[:80],
                        })
    except Exception:
        pass
    return findings

def scan_repo(root_path='.', report_file=None):
    all_findings = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        
        for fname in filenames:
            if any(fname.endswith(ext) for ext in SKIP_EXTS):
                continue
            
            fpath = os.path.join(dirpath, fname)
            findings = scan_file(fpath)
            all_findings.extend(findings)
    
    print(f"\n🔍 Secrets Scan — {root_path}")
    print("=" * 50)
    print(f"Found {len(all_findings)} potential secrets\n")
    
    by_type = {}
    for f in all_findings:
        by_type.setdefault(f['type'], []).append(f)
    
    for pattern_type, items in sorted(by_type.items()):
        print(f"  [{pattern_type}] {len(items)} occurrences")
        for item in items[:2]:
            print(f"      {item['file']}:{item['line']}")
    
    if report_file:
        with open(report_file, 'w') as f:
            json.dump(all_findings, f, indent=2)
        print(f"\n📄 Report saved to {report_file}")
    
    return all_findings

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default='.', help='Scan directory')
    parser.add_argument('--report', help='Save JSON report')
    args = parser.parse_args()
    scan_repo(args.path, args.report)
