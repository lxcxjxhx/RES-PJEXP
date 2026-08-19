# chore: 切换许可证为 AGPLv3 并引入 DCO

**PR 链接**: [lxcxjxhx/HOS-MATCH-PROJECT#1](https://github.com/lxcxjxhx/HOS-MATCH-PROJECT/pull/1)
**状态**: Merged
**合并时间**: 2026-08-02T13:57:18Z
**创建时间**: 2026-08-02T13:54:43Z
**作者**: [lxcxjxhx](https://github.com/lxcxjxhx)

## 统计信息

- **新增行数**: 93
- **删除行数**: 0
- **变更文件数**: 3
- **提交数**: 1

## 变更文件

| 文件 | 状态 | 新增 | 删除 |
|------|------|------|------|
| `.github/workflows/dco.yml` | NEW | +39 | -0 |
| `CONTRIBUTING.md` | NEW | +41 | -0 |
| `README.md` | MOD | +13 | -0 |

## PR 描述

## 变更内容

- 将项目许可证切换为 **AGPLv3**（GNU Affero General Public License v3.0，OSI 认证的强互惠许可证）
- 新增 `CONTRIBUTING.md`：贡献指南 + DCO（Developer Certificate of Origin）签名要求
- 新增 DCO 检查 workflow（`.github/workflows/dco.yml`）：CI 自动校验每个提交是否含 `Signed-off-by`

## 为什么

AGPLv3 是 OSI 认证中限制最强的 copyleft 许可证：将本项目（或基于它的修改版）作为 SaaS 对外提供服务时必须向用户公开完整服务端源码，可有效防止被闭源商用 / 拿去搭建云服务。

## 注意事项

- 从本 PR 合并起，所有提交都必须带 `Signed-off-by`（使用 `git commit -s`），否则 CI 会阻止合并。
- 维护者：本 PR 已由维护者本人签名提交。

## 相关链接

- **源仓库**: [lxcxjxhx/HOS-MATCH-PROJECT](https://github.com/lxcxjxhx/HOS-MATCH-PROJECT)
- **PR 链接**: https://github.com/lxcxjxhx/HOS-MATCH-PROJECT/pull/1
- **Diff**: https://github.com/lxcxjxhx/HOS-MATCH-PROJECT/pull/1.diff

---
*Auto-generated at 2026-08-19 01:02:17 UTC*
