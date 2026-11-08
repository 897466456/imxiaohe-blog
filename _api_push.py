#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Push local commits to GitHub via git-data API (fallback when git-over-https stalls).
Usage: python _api_push.py <repo> <branch> <commit1> <commit2> ... (oldest first)"""
import base64, json, subprocess, sys

REPO, BRANCH = sys.argv[1], sys.argv[2]
COMMITS = sys.argv[3:]

def gh(method, path, data=None):
    cmd = ["gh", "api", "--method", method, f"/repos/{REPO}{path}"]
    if data is not None:
        cmd += ["--input", "-"]
    p = subprocess.run(cmd, input=json.dumps(data).encode() if data is not None else None,
                       capture_output=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"gh api {method} {path} failed: {p.stderr.decode()[:300]}")
    return json.loads(p.stdout) if p.stdout.strip() else {}

def blob_sha(path):
    content = open(path, "rb").read()
    data = {"content": base64.b64encode(content).decode(), "encoding": "base64"}
    return gh("POST", "/git/blobs", data)["sha"]

# current head
head = gh("GET", f"/git/ref/heads/{BRANCH}")["object"]["sha"]
print("base:", head[:8])

for sha in COMMITS:
    # local file changes for this commit vs its parent (previous remote head)
    diff = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", "-z", sha],
        capture_output=True).stdout.decode("utf-8", "ignore").split("\0")
    changes = []
    i = 0
    while i < len(diff) - 1:
        st, path = diff[i], diff[i + 1]
        changes.append((st, path))
        i += 2
    msg = subprocess.run(["git", "log", "-1", "--format=%s%n%n%b", sha],
                         capture_output=True).stdout.decode("utf-8")

    tree = gh("GET", f"/git/commits/{head}")["tree"]["sha"]
    full = gh("GET", f"/git/trees/{tree}?recursive=1")
    entries = {e["path"]: e for e in full["tree"] if e["type"] != "tree"}

    new_entries = []
    for st, path in changes:
        if st == "D":
            entries.pop(path, None)
        else:
            b = blob_sha(path)
            entries[path] = {"path": path, "mode": "100644", "type": "blob", "sha": b}
    new_entries = [{"path": k, "mode": v["mode"], "type": v["type"], "sha": v["sha"]}
                   for k, v in entries.items()]
    new_tree = gh("POST", "/git/trees", {"base_tree": tree, "tree": new_entries})["sha"]
    new_commit = gh("POST", "/git/commits",
                    {"message": msg, "tree": new_tree, "parents": [head]})["sha"]
    print(f"pushed {sha} -> {new_commit[:8]} ({len(changes)} files)")
    head = new_commit

gh("PATCH", f"/git/refs/heads/{BRANCH}", {"sha": head, "force": True})
print(f"branch {BRANCH} -> {head[:8]}")