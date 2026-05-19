#!/usr/bin/env python3
"""
git_commit_analyzer.py -- Detect bot/fake commits in a git history
Looks for: same author name but different emails, suspicious timestamps,
mass commits from single author, copy-paste messages

Usage:
  python3 git_commit_analyzer.py <repo_path>
  python3 git_commit_analyzer.py . --since "2024-01-01" --top 10
"""
import subprocess, re, json, argparse, sys
from collections import defaultdict
from datetime import datetime

def git(cmd, repo='.'):
    r = subprocess.run(f'git -C {repo} {cmd}', shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_commits(repo, since=None):
    cmd = 'log --format=%H%n%an%n%ae%n%ad%n%s'
    if since: cmd += f' --since={since}'
    raw = git(cmd, repo)
    commits = []
    lines = raw.splitlines()
    for i in range(0, len(lines), 5):
        if i + 4 < len(lines):
            commits.append({
                'hash': lines[i][:8],
                'author_name': lines[i+1],
                'author_email': lines[i+2],
                'date': lines[i+3],
                'message': lines[i+4]
            })
    return commits

def analyze(repo, since=None):
    commits = get_commits(repo, since)
    if not commits:
        print("No commits found.")
        return
    
    print(f"\n🔍 Git Commit Analysis — {len(commits)} commits\n")
    
    # 1. Suspicious author patterns
    print("[1] Author anomalies:")
    author_emails = defaultdict(set)
    for c in commits:
        author_emails[c['author_name']].add(c['author_email'])
    
    suspicious = {name: emails for name, emails in author_emails.items() if len(emails) > 1}
    if suspicious:
        for name, emails in suspicious.items():
            print(f"  ⚠️  '{name}' using {len(emails)} different emails:")
            for email in emails:
                print(f"      - {email}")
    else:
        print("  ✅ No suspicious author patterns")
    
    # 2. Commit velocity (mass commits)
    print("\n[2] Commit velocity (top 10):")
    author_counts = defaultdict(int)
    for c in commits:
        author_counts[c['author_name']] += 1
    
    for name, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = (count / len(commits)) * 100
        bar = '█' * int(pct / 2)
        print(f"  {name:<25} {count:3d} ({pct:5.1f}%) {bar}")
    
    # 3. Message patterns (copy-paste detection)
    print("\n[3] Suspicious message patterns:")
    messages = defaultdict(int)
    for c in commits:
        msg = c['message'][:50]  # First 50 chars
        messages[msg] += 1
    
    duplicates = {msg: count for msg, count in messages.items() if count > 5}
    if duplicates:
        for msg, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  ⚠️  '{msg[:40]}...' appears {count}x")
    else:
        print("  ✅ No mass copy-paste messages detected")
    
    # 4. Timestamp clustering
    print("\n[4] Temporal clustering:")
    hour_counts = defaultdict(int)
    for c in commits:
        try:
            dt = datetime.fromisoformat(c['date'].replace('Z', '+00:00'))
            hour = dt.hour
            hour_counts[hour] += 1
        except: pass
    
    if hour_counts:
        peak_hour = max(hour_counts, key=hour_counts.get)
        peak_count = hour_counts[peak_hour]
        if peak_count > len(commits) * 0.3:
            print(f"  ⚠️  {peak_count} commits clustered around {peak_hour:02d}:00 (bot-like)")
        else:
            print(f"  ✅ Commits spread across hours ({len(hour_counts)} hours)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detect bot commits in git history')
    parser.add_argument('repo', nargs='?', default='.', help='Repo path')
    parser.add_argument('--since', help='Only analyze commits since date')
    args = parser.parse_args()
    
    analyze(args.repo, args.since)
