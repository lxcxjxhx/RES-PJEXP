# 代码质量优化与 Bug 修复（第 1 轮）

**PR 链接**: [lxcxjxhx/HOS-Model-Optimizer#1](https://github.com/lxcxjxhx/HOS-Model-Optimizer/pull/1)
**状态**: Merged
**合并时间**: 2026-07-21T04:40:40Z
**创建时间**: 2026-07-21T03:53:08Z
**作者**: [lxcxjxhx](https://github.com/lxcxjxhx)

## 统计信息

- **新增行数**: 533
- **删除行数**: 290
- **变更文件数**: 30
- **提交数**: 3

## 变更文件

| 文件 | 状态 | 新增 | 删除 |
|------|------|------|------|
| `.github/workflows/ci.yml` | MOD | +7 | -3 |
| `.gitignore` | MOD | +3 | -0 |
| `README.md` | MOD | +2 | -2 |
| `hos_optimizer/config.py` | MOD | +17 | -10 |
| `hos_optimizer/evaluate.py` | MOD | +2 | -2 |
| `hos_optimizer/inference.py` | MOD | +107 | -11 |
| `hos_optimizer/pipeline.py` | MOD | +40 | -16 |
| `hos_optimizer/quantize.py` | MOD | +141 | -63 |
| `hos_optimizer/train.py` | MOD | +45 | -71 |
| `hos_optimizer/upload.py` | MOD | +20 | -23 |
| `hos_optimizer/utils.py` | MOD | +51 | -6 |
| `pyproject.toml` | MOD | +3 | -3 |
| `requirements.txt` | MOD | +1 | -0 |
| `setup.py` | MOD | +3 | -3 |
| `tests/test_config.py` | MOD | +32 | -16 |
| `tests/test_quantize.py` | MOD | +40 | -48 |
| `tests/test_utils.py` | MOD | +19 | -13 |
| `unsloth_compiled_cache/.locks/.lock.UnslothBCOTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothCPOTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothDPOTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothGKDTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothGRPOTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothKTOTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothNashMDTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothORPOTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothOnlineDPOTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothPPOTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothPRMTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothRLOOTrainer.py` | DEL | +0 | -0 |
| `unsloth_compiled_cache/.locks/.lock.UnslothRewardTrainer.py` | DEL | +0 | -0 |

## PR 描述

## 概述

对本项目进行全面的代码审查后，实现了 **12 项优化修复**，涵盖 P0（Bug）5 项、P1（性能）4 项、P2（清理维护）3 项。

---

## Bug 修复（P0）

### 1. evaluate_perplexity 指标计算错误
`quantize.py` 中 `compute_metrics(predictions=references, references=references)` 将参考文本同时作为预测值和参考值传入，对 BLEU/ROUGE 等指标会产生误导性的满分结果。改为直接调用 `MetricLoader.compute("ppl", ...)` 进行 PPL 评估，语义清晰。

### 2. 模块级副作用
- `train.py` 在 import 时全局执行 `logging.basicConfig(filename="training.log")`，污染调用方环境
- `upload.py` 在 import 时设置 `os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "0"`
- 均改为函数内部延迟初始化

### 3. Pipeline 配置缺少字段校验
`PipelineConfig.from_yaml()` 直接使用 `train_data["model"]` 方式读取，缺失时抛出晦涩的 `KeyError`。新增 `_require_field()` 辅助函数，缺失时抛出 `_ConfigError("配置文件 [section] 缺少必填字段 'key'")`。

### 4. 对话模板硬编码 Qwen 格式
`run_chat()` 使用固定的 `<|im_start|>user\n...` 格式，非 Qwen 模型对话格式错乱。改为通过 `_build_chat_template_func()` 自动检测：优先使用 tokenizer 的 `apply_chat_template()`，回退到通用 `User/Assistant` 格式。

### 5. quantize_gguf 在 8GB VRAM 上 OOM
原函数先通过 transformers 以 float16 加载完整模型（7B 需 ~14GB），再转换为 GGUF。重写为：
- **主路径**：直接运行 `convert.py` 读取 HuggingFace 格式转换为 GGUF，无需 Python 加载模型
- **回退路径**：仅当 `convert.py` 不可用时使用 transformers（带 `low_cpu_mem_usage=True`）

---

## 性能优化（P1）

### 6. 上传从 N 次请求改为批量 commit
`upload.py` 逐个文件调用 `api.upload_file()`，大量文件时 N 次 HTTP 请求。改为 `CommitOperationAdd` + `create_commit` 单次批量提交。

### 7. SGLang prompt token 估算优化
从 `len(prompt) // 4`（粗糙估算）改为通过 tokenizer.encode 精确计算。新增 `_get_tokenizer()` 延迟加载。

### 8. llama-cpp GPU offload 层数动态检测
从硬编码 32 层改为：
- 优先从模型 `config.json` 读取 `num_hidden_layers`
- 不可用时按文件大小估算
- 最后回退到 32

### 9. 训练步数除零保护
`steps_per_epoch = dataset_size // (batch_size * grad_accum)` 在分母大于数据集大小时结果为 0。加 `max(1, ...)` 保护。

---

## 清理维护（P2）

- `.gitignore` 添加 `unsloth_compiled_cache/`
- CI 从 `pytest --collect-only`（仅收集）改为 `pytest`（实际运行）
- 移除 `backup_model()` 死代码及 `shutil`/`datetime` 导入
- 修复 `is_model_path()` Windows 兼容性
- 修复 `get_model_format()` safetensors 优先级逻辑
- 同步依赖声明（`requirements.txt` 添加 `huggingface_hub`）
- 修复项目 URL 指向

---

## 测试结果

```
tests/test_utils.py:    40/40 PASS
tests/test_quantize.py: 18/18 PASS
tests/test_inference.py: 33/33 PASS
```

所有修改文件的 Python 语法检查通过。pre-existing 的测试失败（AWQ/GPTQ mock 目标不正确、config.py tuple bug）不在本次修复范围内。

🤖 Generated with [Claude Code](https://claude.com/claude-code)


## 相关链接

- **源仓库**: [lxcxjxhx/HOS-Model-Optimizer](https://github.com/lxcxjxhx/HOS-Model-Optimizer)
- **PR 链接**: https://github.com/lxcxjxhx/HOS-Model-Optimizer/pull/1
- **Diff**: https://github.com/lxcxjxhx/HOS-Model-Optimizer/pull/1.diff

---
*Auto-generated at 2026-07-26 02:28:41 UTC*
