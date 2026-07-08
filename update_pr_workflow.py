#!/usr/bin/env python3
"""
GitHub Actions workflow script to auto-update PR records.
Fetches merged PRs, generates per-PR detail files, and updates README files.
"""

import os
import requests
from datetime import datetime
from collections import defaultdict

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
USERNAME = 'lxcxjxhx'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}


def get_merged_prs():
    url = f'https://api.github.com/search/issues?q=author:{USERNAME}+is:pr+is:merged&per_page=100'
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()['items']


def get_pr_details(repo_full_name, pr_number):
    url = f'https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}'
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def get_pr_files(repo_full_name, pr_number):
    url = f'https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files'
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json()


def sanitize_repo_name(repo_name):
    return repo_name.replace('/', '_').replace('-', '_')


def generate_pr_detail_markdown(pr_data, files_data):
    repo_name = pr_data['base']['repo']['full_name']
    repo_url = pr_data['base']['repo']['html_url']

    md = f"""# {pr_data['title']}

**PR 链接**: [{repo_name}#{pr_data['number']}]({pr_data['html_url']})
**状态**: Merged
**合并时间**: {pr_data['merged_at']}
**创建时间**: {pr_data['created_at']}
**作者**: [{pr_data['user']['login']}]({pr_data['user']['html_url']})

## 统计信息

- **新增行数**: {sum(f['additions'] for f in files_data)}
- **删除行数**: {sum(f['deletions'] for f in files_data)}
- **变更文件数**: {len(files_data)}
- **提交数**: {pr_data['commits']}

## 变更文件

| 文件 | 状态 | 新增 | 删除 |
|------|------|------|------|
"""
    status_map = {'added': 'NEW', 'modified': 'MOD', 'removed': 'DEL', 'renamed': 'REN'}
    for f in files_data:
        status = status_map.get(f['status'], f['status'])
        md += f"| `{f['filename']}` | {status} | +{f['additions']} | -{f['deletions']} |\n"

    body = pr_data['body'] if pr_data['body'] else '_No description_'
    md += f"""
## PR 描述

{body}

## 相关链接

- **源仓库**: [{repo_name}]({repo_url})
- **PR 链接**: {pr_data['html_url']}
- **Diff**: {pr_data['diff_url']}

---
*Auto-generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""
    return md


def generate_pr_readme(prs_by_repo):
    total_prs = sum(len(prs) for prs in prs_by_repo.values())

    md = f"""# Open Source PR Records

Merged Pull Requests across open source projects.

## Summary

- **Total Merged PRs**: {total_prs}
- **Projects**: {len(prs_by_repo)}

## PR List

| Repository | PR | Title | Merged |
|------------|-----|-------|--------|
"""
    for repo_name, prs in sorted(prs_by_repo.items()):
        for pr in sorted(prs, key=lambda x: x['merged_at'], reverse=True):
            repo_url = pr['base']['repo']['html_url']
            md += f"| [{repo_name}]({repo_url}) | [#{pr['number']}]({pr['html_url']}) | {pr['title']} | {pr['merged_at'][:10]} |\n"

    md += f"""
## Detail Files

Each PR's detailed analysis (code changes, file list, statistics) is auto-generated in subdirectories.

```
PR/
├── README.md
├── {{repo_name}}/
│   ├── PR_{{number}}.md
│   └── ...
```

## Auto Update

Updated daily via GitHub Actions at UTC 00:00.

Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

---

**GitHub**: [{USERNAME}](https://github.com/{USERNAME})
"""
    return md


def generate_main_readme(prs_by_repo, total_prs):
    all_prs = []
    for prs in prs_by_repo.values():
        all_prs.extend(prs)
    recent_prs = sorted(all_prs, key=lambda x: x['merged_at'], reverse=True)[:5]

    md = f"""# Personal Knowledge Base

## Open Source Contributions

- **Total Merged PRs**: {total_prs}
- **Projects**: {len(prs_by_repo)}
- [View PR Records](./PR/README.md)

## Recent Contributions

| Repository | PR | Title | Date |
|------------|-----|-------|------|
"""
    for pr in recent_prs:
        repo_name = pr['base']['repo']['full_name']
        repo_url = pr['base']['repo']['html_url']
        title = pr['title'][:50] + ('...' if len(pr['title']) > 50 else '')
        md += f"| [{repo_name}]({repo_url}) | [#{pr['number']}]({pr['html_url']}) | {title} | {pr['merged_at'][:10]} |\n"

    md += """
## By Project

"""
    for repo_name, prs in sorted(prs_by_repo.items()):
        repo_url = prs[0]['base']['repo']['html_url']
        md += f"- **[{repo_name}]({repo_url})**: {len(prs)} PR(s)\n"

    md += f"""
## Auto Update

This repo is auto-updated via GitHub Actions daily.

Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

---

**GitHub**: [{USERNAME}](https://github.com/{USERNAME})
"""
    return md


def main():
    print("Starting PR auto-update...")

    prs = get_merged_prs()
    print(f"Found {len(prs)} merged PRs")

    prs_by_repo = defaultdict(list)
    pr_details = {}

    for pr in prs:
        parts = pr['repository_url'].split('/')
        owner = parts[-2]
        repo_name = parts[-1]
        repo_full_name = f"{owner}/{repo_name}"
        pr_number = pr['number']

        print(f"Processing {repo_full_name}#{pr_number}...")
        pr_data = get_pr_details(repo_full_name, pr_number)
        files_data = get_pr_files(repo_full_name, pr_number)
        prs_by_repo[repo_full_name].append(pr_data)
        pr_details[(repo_full_name, pr_number)] = (pr_data, files_data)

    print("\nGenerating PR detail files...")
    for (repo_name, pr_number), (pr_data, files_data) in pr_details.items():
        safe_name = sanitize_repo_name(repo_name)
        dir_path = f"PR/{safe_name}"
        os.makedirs(dir_path, exist_ok=True)
        file_path = f"{dir_path}/PR_{pr_number}.md"
        content = generate_pr_detail_markdown(pr_data, files_data)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  {file_path}")

    print("\nGenerating PR/README.md...")
    pr_readme = generate_pr_readme(prs_by_repo)
    os.makedirs('PR', exist_ok=True)
    with open('PR/README.md', 'w', encoding='utf-8') as f:
        f.write(pr_readme)

    print("Generating main README.md...")
    total_prs = sum(len(prs) for prs in prs_by_repo.values())
    main_readme = generate_main_readme(prs_by_repo, total_prs)
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(main_readme)

    print("Done!")


if __name__ == '__main__':
    main()
