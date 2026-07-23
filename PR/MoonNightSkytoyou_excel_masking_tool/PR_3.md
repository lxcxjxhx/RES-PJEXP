# perf: 优化性能、修复 SHA-256 Int32Array 问题与列索引算法

**PR 链接**: [MoonNightSkytoyou/excel-masking-tool#3](https://github.com/MoonNightSkytoyou/excel-masking-tool/pull/3)
**状态**: Merged
**合并时间**: 2026-07-20T14:51:39Z
**创建时间**: 2026-07-20T14:15:07Z
**作者**: [lxcxjxhx](https://github.com/lxcxjxhx)

## 统计信息

- **新增行数**: 80
- **删除行数**: 39
- **变更文件数**: 3
- **提交数**: 1

## 变更文件

| 文件 | 状态 | 新增 | 删除 |
|------|------|------|------|
| `src/components/ExcelMasker.tsx` | MOD | +75 | -35 |
| `src/utils/faker.ts` | MOD | +1 | -1 |
| `src/utils/xlsx-handler.ts` | MOD | +4 | -3 |

## PR 描述

## 性能优化与修复

### 优化/修复内容
1. **性能：useMemo 缓存遮罩预览值** — 将 `getMaskedPreviewValue` 改为预计算的 `maskedPreviewMap`，避免每次渲染时逐单元格重新计算遮罩值
2. **修复：colIndexToLabel 边缘情况** — 修正列索引转字母算法，正确处理 26→AA、52→BA 等边界值
3. **修复：SHA-256 Int32Array → Uint32Array** — 改用无符号整数数组，确保大文件哈希计算的正确性
4. **优化：下载添加 loading 状态** — 导出按钮显示 spinner 和 '导出中...' 反馈，并 disabled 防重复点击

### 变更文件
- `src/components/ExcelMasker.tsx` — useMemo 缓存 + 下载 loading
- `src/utils/faker.ts` — Uint32Array 替代 Int32Array
- `src/utils/xlsx-handler.ts` — 修正 colIndexToLabel

所有通过 TypeScript 严格检查和 Vite 构建验证。

## 相关链接

- **源仓库**: [MoonNightSkytoyou/excel-masking-tool](https://github.com/MoonNightSkytoyou/excel-masking-tool)
- **PR 链接**: https://github.com/MoonNightSkytoyou/excel-masking-tool/pull/3
- **Diff**: https://github.com/MoonNightSkytoyou/excel-masking-tool/pull/3.diff

---
*Auto-generated at 2026-07-23 02:26:43 UTC*
