# fix: 修复内存泄漏、无效CSS类名、重复常量及文件验证问题

**PR 链接**: [MoonNightSkytoyou/excel-masking-tool#1](https://github.com/MoonNightSkytoyou/excel-masking-tool/pull/1)
**状态**: Merged
**合并时间**: 2026-07-20T14:57:48Z
**创建时间**: 2026-07-20T14:14:44Z
**作者**: [lxcxjxhx](https://github.com/lxcxjxhx)

## 统计信息

- **新增行数**: 4432
- **删除行数**: 34
- **变更文件数**: 3
- **提交数**: 1

## 变更文件

| 文件 | 状态 | 新增 | 删除 |
|------|------|------|------|
| `package-lock.json` | NEW | +4382 | -0 |
| `src/components/ExcelMasker.tsx` | MOD | +19 | -32 |
| `src/utils/xlsx-handler.ts` | MOD | +31 | -2 |

## PR 描述

## 问题修复

### 🐛 Bug 修复
1. **内存泄漏** — 在 xlsx-handler.ts 中添加 `URL.revokeObjectURL()` 调用，下载后及时释放 Blob URL 以释放内存
2. **无效 CSS 类名** — 将所有 Tailwind v4 中不存在的 `text-xxs` 替换为有效的 `text-xs`
3. **重复常量** — 消除 ExcelMasker.tsx 和 xlsx-handler.ts 中重复的 `DEFAULT_GLOBAL_OPERATORS` 定义，统一从 xlsx-handler 导出共享
4. **文件验证增强** — 在 parseExcelFile 中添加文件魔数（Magic Bytes）校验，拦截不符合规范的文件

### 变更文件
- `src/components/ExcelMasker.tsx`
- `src/utils/xlsx-handler.ts`

所有通过 TypeScript 严格检查和 Vite 构建验证。

## 相关链接

- **源仓库**: [MoonNightSkytoyou/excel-masking-tool](https://github.com/MoonNightSkytoyou/excel-masking-tool)
- **PR 链接**: https://github.com/MoonNightSkytoyou/excel-masking-tool/pull/1
- **Diff**: https://github.com/MoonNightSkytoyou/excel-masking-tool/pull/1.diff

---
*Auto-generated at 2026-07-22 02:21:48 UTC*
