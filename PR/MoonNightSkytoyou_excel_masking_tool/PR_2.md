# refactor: 提取翻译/配置常量、清理依赖、启用严格模式并添加错误边界

**PR 链接**: [MoonNightSkytoyou/excel-masking-tool#2](https://github.com/MoonNightSkytoyou/excel-masking-tool/pull/2)
**状态**: Merged
**合并时间**: 2026-07-20T15:12:12Z
**创建时间**: 2026-07-20T14:14:54Z
**作者**: [lxcxjxhx](https://github.com/lxcxjxhx)

## 统计信息

- **新增行数**: 425
- **删除行数**: 1879
- **变更文件数**: 8
- **提交数**: 1

## 变更文件

| 文件 | 状态 | 新增 | 删除 |
|------|------|------|------|
| `package-lock.json` | MOD | +28 | -1637 |
| `package.json` | MOD | +3 | -7 |
| `src/App.tsx` | MOD | +8 | -5 |
| `src/components/ErrorBoundary.tsx` | NEW | +65 | -0 |
| `src/components/ExcelMasker.tsx` | MOD | +9 | -229 |
| `src/config/entity-colors.ts` | NEW | +19 | -0 |
| `src/i18n/translations.ts` | NEW | +289 | -0 |
| `tsconfig.json` | MOD | +4 | -1 |

## PR 描述

## 代码架构重构

### 重构内容
1. **提取翻译文件** — 将 200+ 行的 TRANSLATIONS 移至 `src/i18n/translations.ts`，并添加 TypeScript 类型定义
2. **提取常量配置** — 将 ENTITY_COLORS 移至 `src/config/entity-colors.ts`
3. **消除重复** — 导出 `DEFAULT_GLOBAL_OPERATORS` 共用于 ExcelMasker 和 xlsx-handler
4. **清理未使用的依赖** — 移除 `@google/genai`、`dotenv`、`express`、`@types/express`、`autoprefixer`
5. **启用 TypeScript strict 模式** — 开启 `strict`、`noUnusedLocals`、`noUnusedParameters`
6. **添加 ErrorBoundary** — React 错误边界组件捕获渲染异常
7. **安装类型声明** — 添加 `@types/react` / `@types/react-dom`

### 变更文件
- `src/components/ExcelMasker.tsx` — 大幅简化（-230 行）
- `src/i18n/translations.ts` — 新增翻译文件
- `src/config/entity-colors.ts` — 新增配置常量
- `src/components/ErrorBoundary.tsx` — 新增错误边界组件
- `src/App.tsx` — 集成 ErrorBoundary
- `src/utils/xlsx-handler.ts` — 导出 DEFAULT_GLOBAL_OPERATORS
- `package.json` — 清理依赖
- `tsconfig.json` — 启用严格模式

所有通过 TypeScript 严格检查和 Vite 构建验证。

## 相关链接

- **源仓库**: [MoonNightSkytoyou/excel-masking-tool](https://github.com/MoonNightSkytoyou/excel-masking-tool)
- **PR 链接**: https://github.com/MoonNightSkytoyou/excel-masking-tool/pull/2
- **Diff**: https://github.com/MoonNightSkytoyou/excel-masking-tool/pull/2.diff

---
*Auto-generated at 2026-07-27 02:36:36 UTC*
