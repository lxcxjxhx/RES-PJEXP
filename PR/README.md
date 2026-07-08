# 开源贡献 PR 记录

本仓库记录了我在各大开源项目中的 Pull Request 贡献。

## 📊 统计概览

- **已合并 PR 总数**: 6
- **涉及项目**: 4 个
- **贡献类型**: Bug 修复、文档改进、参数验证

## 📋 PR 列表

| 仓库 | PR 编号 | 标题 | 状态 | 合并时间 |
|------|---------|------|------|----------|
| [vanhauser-thc/thc-hydra](https://github.com/vanhauser-thc/thc-hydra) | [#1089](https://github.com/vanhauser-thc/thc-hydra/pull/1089) | Fix socket leak in SMB service initialization | ✅ Merged | 2026-07-07 |
| [vanhauser-thc/thc-hydra](https://github.com/vanhauser-thc/thc-hydra) | [#1088](https://github.com/vanhauser-thc/thc-hydra/pull/1088) | Fix file handle leaks in hydra.c | ✅ Merged | 2026-07-07 |
| [vanhauser-thc/thc-hydra](https://github.com/vanhauser-thc/thc-hydra) | [#1087](https://github.com/vanhauser-thc/thc-hydra/pull/1087) | Fix file handle leaks in main function | ✅ Merged | 2026-07-07 |
| [GH05TCREW/pentestagent](https://github.com/GH05TCREW/pentestagent) | [#82](https://github.com/GH05TCREW/pentestagent/pull/82) | fix: add parameter validation for timeout and max_retries | ✅ Merged | 2026-07-07 |
| [axolotl-ai-cloud/axolotl](https://github.com/axolotl-ai-cloud/axolotl) | [#3802](https://github.com/axolotl-ai-cloud/axolotl/pull/3802) | fix: improve validation error for jinja chat template | ✅ Merged | 2026-07-07 |
| [huggingface/peft](https://github.com/huggingface/peft) | [#3392](https://github.com/huggingface/peft/pull/3392) | docs: fix missing torch import and variable name in README examples | ✅ Merged | 2026-07-06 |

## 🎯 贡献详情

### 1. thc-hydra (密码破解工具)

**项目简介**: hydra 是一个快速且灵活的密码破解工具，支持多种协议。

#### PR #1089 - Fix socket leak in SMB service initialization
- **问题**: SMB 服务初始化函数在三个错误处理路径中未关闭 socket，导致文件描述符泄漏
- **修复**: 在所有错误返回路径前添加 `close(sock)` 调用
- **影响**: 防止长时间暴力破解会话中的资源泄漏，提升稳定性

#### PR #1088 - Fix file handle leaks in hydra.c
- **问题**: `fill_mem()` 函数中 4 个文件句柄未关闭
- **修复**: 在 `fill_mem()` 返回前添加 `fclose()` 调用
- **文件**: `hydra.c` 第 374, 380, 392, 409 行

#### PR #1087 - Fix file handle leaks in main function
- **问题**: `main()` 函数中打开的 4 个文件句柄在读取内容后未关闭
- **修复**: 在 `fill_mem()` 完成后立即调用 `fclose()`
- **影响**: 防止文件描述符耗尽，避免长时间运行时的崩溃

### 2. pentestagent (渗透测试代理)

**项目简介**: 一个基于 AI 的渗透测试自动化工具。

#### PR #82 - fix: add parameter validation for timeout and max_retries
- **问题**: `ToolExecutor.__init__` 方法接受 `timeout` 和 `max_retries` 参数但未验证，无效值会导致意外行为
- **修复**: 添加参数验证，确保 `timeout > 0` 且 `max_retries >= 0`
- **文件**: `pentestagent/tools/executor.py` L25-30
- **影响**: 防止静默失败，提升调试体验

### 3. axolotl (AI 模型微调)

**项目简介**: 一个用于微调大语言模型的工具。

#### PR #3802 - fix: improve validation error for jinja chat template
- **问题**: 用户设置 `chat_template: jinja` 但未提供 `chat_template_jinja` 时，错误信息不够清晰
- **修复**: 改进 `ValueError` 消息，明确说明需要提供实际的模板字符串
- **影响**: 提升用户体验，减少配置困惑

### 4. PEFT (参数高效微调)

**项目简介**: Hugging Face 的参数高效微调库，支持 LoRA、Prefix Tuning 等方法。

#### PR #3392 - docs: fix missing torch import and variable name in README examples
- **问题**: 
  1. README 示例使用 `torch.accelerator.current_accelerator()` 但未导入 `torch`
  2. "Adding multiple adapters" 部分使用错误的变量名 `lora_config`（应为 `peft_config`）
- **修复**: 添加 `import torch`，修正变量名
- **影响**: 确保示例代码可直接运行，减少新用户的困惑

## 🔄 自动化更新

本记录单将通过 GitHub Actions 自动拉取详细的 PR 信息，包括：
- 代码变更统计
- 审查评论
- 合并详情
- 关联的 Issue

## 📅 更新时间

最后更新: 2026-07-08

---

**GitHub 用户**: [lxcxjxhx](https://github.com/lxcxjxhx)
