#!/usr/bin/env python3
"""
GitHub Actions workflow script to auto-update PR records
"""

import os
import requests
import base64
from datetime import datetime
from collections import defaultdict

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO = 'lxcxjxhx/HOS-Qian-jia-hong-resume'
USERNAME = 'lxcxjxhx'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def get_merged_prs():
    """Fetch all merged PRs for the user"""
    url = f'https://api.github.com/search/issues?q=author:{USERNAME}+is:pr+is:merged&per_page=100'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()['items']

def get_pr_details(repo_full_name, pr_number):
    """Get detailed PR information"""
    url = f'https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_pr_files(repo_full_name, pr_number):
    """Get list of files changed in PR"""
    url = f'https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files'
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def sanitize_repo_name(repo_name):
    """Convert repo name to safe directory name"""
    return repo_name.replace('/', '_').replace('-', '_')

def generate_pr_detail_markdown(pr_data, files_data):
    """Generate detailed markdown for a single PR"""
    repo_name = pr_data['base']['repo']['full_name']
    repo_url = pr_data['base']['repo']['html_url']
    
    md = f"""# {pr_data['title']}

**PR 链接**: [{repo_name}#{pr_data['number']}]({pr_data['html_url']})  
**状态**: ✅ Merged  
**合并时间**: {pr_data['merged_at']}  
**创建时间**: {pr_data['created_at']}  
**作者**: [{pr_data['user']['login']}]({pr_data['user']['html_url']})

## 📊 统计信息

- **新增行数**: {sum(f['additions'] for f in files_data)}
- **删除行数**: {sum(f['deletions'] for f in files_data)}
- **变更文件数**: {len(files_data)}
- **提交数**: {pr_data['commits']}

## 📝 变更文件

| 文件 | 状态 | 新增 | 删除 |
|------|------|------|------|
"""
    
    for file in files_data:
        status_map = {
            'added': '🟢 新增',
            'modified': '🔵 修改',
            'removed': '🔴 删除',
            'renamed': '🟡 重命名'
        }
        status = status_map.get(file['status'], file['status'])
        md += f"| `{file['filename']}` | {status} | +{file['additions']} | -{file['deletions']} |\n"
    
    md += f"""
## 📖 PR 描述

{pr_data['body'] if pr_data['body'] else '_无描述_'}

## 🔗 相关链接

- **源仓库**: [{repo_name}]({repo_url})
- **PR 链接**: {pr_data['html_url']}
- **Diff**: {pr_data['diff_url']}
- **Patch**: {pr_data['patch_url']}

---
*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return md

def generate_pr_readme(prs_by_repo):
    """Generate main PR README"""
    total_prs = sum(len(prs) for prs in prs_by_repo.values())
    
    md = f"""# 开源贡献 PR 记录

本仓库记录了我在各大开源项目中的 Pull Request 贡献。

## 📊 统计概览

- **已合并 PR 总数**: {total_prs}
- **涉及项目**: {len(prs_by_repo)} 个
- **贡献类型**: Bug 修复、文档改进、参数验证

## 📋 PR 列表

| 仓库 | PR 编号 | 标题 | 状态 | 合并时间 |
|------|---------|------|------|----------|
"""
    
    for repo_name, prs in sorted(prs_by_repo.items()):
        for pr in sorted(prs, key=lambda x: x['merged_at'], reverse=True):
            repo_url = pr['base']['repo']['html_url']
            md += f"| [{repo_name}]({repo_url}) | [#{pr['number']}]({pr['html_url']}) | {pr['title']} | ✅ Merged | {pr['merged_at'][:10]} |\n"
    
    md += f"""
## 🎯 贡献详情

每个 PR 的详细信息（包括代码变更、文件列表、统计数据）已自动拉取到对应的子目录中。

目录结构：
```
PR/
├── README.md          # 本文件 - PR 总览
├── {{repo_name}}/     # 按仓库分组的 PR 详情
│   ├── PR_{{number}}.md
│   └── ...
```

## 🔄 自动化更新

本记录单通过 GitHub Actions 自动更新：
- **更新频率**: 每天 UTC 00:00
- **更新内容**: 
  - 拉取最新的已合并 PR 列表
  - 获取每个 PR 的详细变更信息
  - 生成详细的 PR 分析文档
  - 更新统计数据和表格

## 📅 更新时间

最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)

---

**GitHub 用户**: [{USERNAME}](https://github.com/{USERNAME})
"""
    return md

def generate_main_readme(prs_by_repo, total_prs):
    """Generate main repository README with PR summary"""
    md = f"""# 📚 个人知识库

欢迎来到我的个人知识库！这里记录了我的学习笔记、项目经验和开源贡献。

## 📂 目录结构

- **PR/** - 开源贡献记录
  - 已合并 PR 总数: **{total_prs}**
  - 涉及项目: **{len(prs_by_repo)}** 个
  - [查看详细 PR 记录](./PR/README.md)

## 🎯 最近开源贡献

| 仓库 | PR | 标题 | 时间 |
|------|-----|------|------|
"""
    
    # Get top 5 recent PRs
    all_prs = []
    for prs in prs_by_repo.values():
        all_prs.extend(prs)
    recent_prs = sorted(all_prs, key=lambda x: x['merged_at'], reverse=True)[:5]
    
    for pr in recent_prs:
        repo_name = pr['base']['repo']['full_name']
        repo_url = pr['base']['repo']['html_url']
        md += f"| [{repo_name}]({repo_url}) | [#{pr['number']}]({pr['html_url']}) | {pr['title'][:40]}{'...' if len(pr['title']) > 40 else ''} | {pr['merged_at'][:10]} |\n"
    
    md += f"""
## 📊 贡献统计

### 按项目分类

"""
    
    for repo_name, prs in sorted(prs_by_repo.items()):
        repo_url = prs[0]['base']['repo']['html_url']
        md += f"- **[{repo_name}]({repo_url})**: {len(prs)} 个 PR\n"
    
    md += f"""
## 🔄 自动更新

本仓库通过 GitHub Actions 自动更新：
- 每日自动拉取最新的 PR 记录
- 自动生成详细的 PR 分析文档
- 自动更新统计数据

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)

---

**GitHub**: [{USERNAME}](https://github.com/{USERNAME})
"""
    return md

def main():
    print("🚀 Starting PR auto-update workflow...")
    
    # Fetch all merged PRs
    print("📥 Fetching merged PRs...")
    prs = get_merged_prs()
    print(f"✅ Found {len(prs)} merged PRs")
    
    # Group PRs by repository
    prs_by_repo = defaultdict(list)
    pr_details = {}
    
    for pr in prs:
        repo_name = pr['repository_url'].split('/')[-1]
        owner = pr['repository_url'].split('/')[-2]
        repo_full_name = f"{owner}/{repo_name}"
        pr_number = pr['number']
        
        print(f"📋 Processing {repo_full_name}#{pr_number}...")
        
        # Get detailed PR info
        pr_data = get_pr_details(repo_full_name, pr_number)
        files_data = get_pr_files(repo_full_name, pr_number)
        
        prs_by_repo[repo_full_name].append(pr_data)
        pr_details[(repo_full_name, pr_number)] = (pr_data, files_data)
    
    # Generate and save PR detail files
    print("\n📝 Generating PR detail files...")
    for (repo_name, pr_number), (pr_data, files_data) in pr_details.items():
        safe_name = sanitize_repo_name(repo_name)
        dir_path = f"PR/{safe_name}"
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = f"{dir_path}/PR_{pr_number}.md"
        content = generate_pr_detail_markdown(pr_data, files_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {file_path}")
    
    # Generate PR README
    print("\n📝 Generating PR/README.md...")
    pr_readme = generate_pr_readme(prs_by_repo)
    with open('PR/README.md', 'w', encoding='utf-8') as f:
        f.write(pr_readme)
    print("  ✅ PR/README.md")
    
    # Generate main README
    print("\n📝 Generating main README.md...")
    total_prs = sum(len(prs) for prs in prs_by_repo.values())
    main_readme = generate_main_readme(prs_by_repo, total_prs)
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(main_readme)
    print("  ✅ README.md")
    
    print("\n✨ All files generated successfully!")

if __name__ == '__main__':
    main()
