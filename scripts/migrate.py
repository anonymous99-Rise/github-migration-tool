#!/usr/bin/env python3
"""
GitHub 仓库迁移脚本 v2
- 带批次延迟，避免风控
- 断点续传（.state 文件）
"""
import urllib.request
import json
import subprocess
import time
import os
import sys
from datetime import datetime

# ============ 配置区（用之前先改） ============
SRC_TOKEN = "ghp_旧账号TOKEN"          # 旧账号 token（读权限）
DST_TOKEN = "ghp_新账号TOKEN"          # 新账号 token（需要 repo 权限）
SRC_USER  = "anonymous99-Rise"         # 旧账号 username
DST_USER  = "新账号username"           # 新账号 username

BACKUP_DIR  = "/root/github_backup"
REPO_LIST   = "/root/github-migration/data/repo_list.txt"
STATE_FILE  = os.path.join(BACKUP_DIR, ".state_v2")
SKIP_FILE   = "/tmp/skip_large_repos.txt"
BATCH_SIZE  = 20      # 每批多少个
BATCH_DELAY = 300     # 批次间隔（秒），300=5分钟
SINGLE_DELAY = 3      # 单个仓库操作间隔（秒）
LOG_DIR     = "/root/github-migration/logs"
# ============================================

os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def read_skip_list():
    skip = set()
    if os.path.exists(SKIP_FILE):
        with open(SKIP_FILE) as f:
            for line in f:
                skip.add(line.strip())
    return skip

def load_state():
    state = set()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            for line in f:
                state.add(line.strip())
    return state

def save_state(repo):
    with open(STATE_FILE, "a") as f:
        f.write(repo + "\n")

def api_request(url, token, method="GET", data=None):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code
    except Exception as e:
        return {"error": str(e)}, 0

def create_repo(repo_name):
    url = "https://api.github.com/user/repos"
    data = {
        "name": repo_name,
        "description": f"Restored from {SRC_USER}",
        "private": False
    }
    result, code = api_request(url, DST_TOKEN, method="POST", data=data)
    if code in (200, 201):
        return True
    # 仓库已存在也当成功
    if "name already exists" in str(result) or code == 422:
        return True
    return False

def push_mirror(repo_name):
    git_dir = os.path.join(BACKUP_DIR, f"{repo_name}.git")
    if not os.path.exists(os.path.join(git_dir, "HEAD")):
        # 尝试重新 clone
        log(f"  目录不存在，尝试 clone: {repo_name}")
        remote_url = f"git@github.com:{SRC_USER}/{repo_name}.git"
        result = subprocess.run(
            ["git", "clone", "--mirror", remote_url, git_dir],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            log(f"  clone 失败: {result.stderr[:100]}")
            return False

    # push 前修改 remote 为目标账号
    subprocess.run(["git", "--git-dir", git_dir, "remote", "set-url",
                    "origin", f"git@github.com:{DST_USER}/{repo_name}.git"],
                   capture_output=True)
    result = subprocess.run(
        ["git", "--git-dir", git_dir, "push", "--mirror"],
        capture_output=True, text=True, timeout=300
    )
    return result.returncode == 0

def run():
    # 读取跳过列表
    skip_repos = read_skip_list()
    log(f"大仓库跳过列表: {len(skip_repos)} 个")

    # 读取待迁移列表
    if not os.path.exists(REPO_LIST):
        log(f"ERROR: 仓库列表不存在: {REPO_LIST}")
        sys.exit(1)

    with open(REPO_LIST) as f:
        all_repos = [r.strip() for r in f if r.strip()]

    # 读取已完成 state
    done = load_state()
    log(f"已迁移: {len(done)} 个")

    # 过滤
    repos_to_do = [r for r in all_repos if r not in done and r not in skip_repos]
    total = len(repos_to_do)
    log(f"本次待迁移: {total} 个（去掉已完成和大仓库）")

    if total == 0:
        log("没有需要迁移的仓库")
        return

    success = fail = 0
    batch_num = 0

    for i, repo in enumerate(repos_to_do, 1):
        log(f"[{i}/{total}] {repo} ...")

        # 1. 创建空仓库
        ok = create_repo(repo)
        if not ok:
            log(f"  创建仓库失败")
            fail += 1
            time.sleep(SINGLE_DELAY)
            continue
        time.sleep(SINGLE_DELAY)

        # 2. push mirror
        ok = push_mirror(repo)
        if ok:
            log(f"  OK")
            save_state(repo)
            success += 1
        else:
            log(f"  FAIL")
            fail += 1

        # 3. 批次延迟
        if i % BATCH_SIZE == 0 and i < total:
            batch_num += 1
            log(f"===== 批次 {batch_num} 完成，休息 {BATCH_DELAY//60} 分钟 =====")
            time.sleep(BATCH_DELAY)

        time.sleep(SINGLE_DELAY)

    log("========================================")
    log(f"迁移完成 {datetime.now()}")
    log(f"成功: {success} | 失败: {fail} | 跳过: {len(done)}")
    log("========================================")

if __name__ == "__main__":
    run()
