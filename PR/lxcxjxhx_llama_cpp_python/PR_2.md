# fix: add parameter validation to core methods for type safety

**PR 链接**: [lxcxjxhx/llama-cpp-python#2](https://github.com/lxcxjxhx/llama-cpp-python/pull/2)
**状态**: Merged
**合并时间**: 2026-07-11T01:50:57Z
**创建时间**: 2026-07-09T10:42:41Z
**作者**: [lxcxjxhx](https://github.com/lxcxjxhx)

## 统计信息

- **新增行数**: 344
- **删除行数**: 9
- **变更文件数**: 2
- **提交数**: 5

## 变更文件

| 文件 | 状态 | 新增 | 删除 |
|------|------|------|------|
| `llama_cpp/llama.py` | MOD | +52 | -9 |
| `tests/test_type_safety_validation.py` | NEW | +292 | -0 |

## PR 描述

## Problem

The llama-cpp-python library lacks parameter validation in several critical methods, which can lead to confusing errors or undefined behavior when users pass invalid arguments. Specifically:

1. **`Llama.__init__`** (llama_cpp/llama.py lines 60-234): No validation for `model_path` (can be empty/None/non-string) or `n_ctx` (can be <= 0)
2. **`Llama.create_completion`** (llama_cpp/llama.py lines 1818-1920): No validation for sampling parameters like `temperature`, `top_p`, and `top_k`
3. **`Llama.tokenize`** (llama_cpp/llama.py lines 605-621): No type validation for the `text` parameter
4. **`Llama.detokenize`** (llama_cpp/llama.py lines 623-639): No type validation for the `tokens` parameter or its elements

These missing validations can cause:
- Cryptic errors deep in the C++ layer
- Segmentation faults or undefined behavior
- Difficult debugging for users
- Inconsistent error messages

## Solution

Add explicit parameter validation at the Python layer with clear, descriptive error messages. This provides:
- Early failure with actionable error messages
- Type safety guarantees
- Better developer experience
- Prevention of undefined behavior in the underlying C++ code

## Changes

### 1. `Llama.__init__` validation (llama_cpp/llama.py:202-209)
```python
# Parameter validation
if not model_path:
    raise ValueError("model_path cannot be empty or None")

if not isinstance(model_path, str):
    raise TypeError("model_path must be a string")

if n_ctx <= 0:
    raise ValueError(f"n_ctx must be > 0, got {n_ctx}")
```

### 2. `Llama.create_completion` validation (llama_cpp/llama.py:1904-1911)
```python
# Parameter validation
if temperature < 0.0:
    raise ValueError(f"temperature must be >= 0.0, got {temperature}")

if not 0.0 <= top_p <= 1.0:
    raise ValueError(f"top_p must be in [0.0, 1.0], got {top_p}")

if top_k < 0:
    raise ValueError(f"top_k must be >= 0, got {top_k}")
```

### 3. `Llama.tokenize` validation (llama_cpp/llama.py:632-634)
```python
# Type validation
if not isinstance(text, (str, bytes)):
    raise TypeError(f"text must be str or bytes, got {type(text).__name__}")
```

### 4. `Llama.detokenize` validation (llama_cpp/llama.py:656-661)
```python
# Type validation
if not isinstance(tokens, list):
    raise TypeError(f"tokens must be a list, got {type(tokens).__name__}")

if not all(isinstance(t, int) for t in tokens):
    raise TypeError("all elements in tokens must be integers")
```

### 5. Updated docstrings
Updated the `Raises` sections in docstrings to document the new exceptions.

## Related Issues

Related to #2210 - While that issue focuses on the `embedding` parameter naming, it highlights a broader pattern of insufficient parameter validation leading to confusing errors. This PR addresses the validation aspect by adding early checks with clear error messages.

## Testing

Created comprehensive test suite in `tests/test_type_safety_validation.py` with 41 test cases covering:

**TestInitValidation** (10 tests):
- Empty/None model_path raises ValueError
- Non-string model_path (int, list, dict) raises TypeError
- n_ctx <= 0 raises ValueError
- Valid parameters pass validation

**TestTokenizeValidation** (8 tests):
- Invalid types (int, list, None, dict, float) raise TypeError
- Valid types (str, bytes, empty str) are accepted

**TestDetokenizeValidation** (10 tests):
- Invalid container types (str, int, None, tuple, dict) raise TypeError
- Lists with non-int elements (str, float, None) raise TypeError
- Valid lists (including empty) are accepted

**TestCreateCompletionValidation** (13 tests):
- Negative temperature raises ValueError
- top_p outside [0.0, 1.0] raises ValueError
- Negative top_k raises ValueError
- Valid parameters and boundary values (0.0, 1.0) pass validation
- Multiple invalid parameters fail on first check

### Test Evidence

```
$ pytest tests/test_type_safety_validation.py -v

============================= test session starts =============================
platform win32 -- Python 3.12.7, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\1AAA_PROJECT\BOS\BOS-GIT\fork-projects\llama-cpp-python
configfile: pyproject.toml
plugins: anyio-4.13.0, langsmith-0.8.3, cov-7.1.0
collecting ... collected 41 items

tests/test_type_safety_validation.py::TestInitValidation::test_empty_model_path_raises_value_error PASSED [  2%]
tests/test_type_safety_validation.py::TestInitValidation::test_none_model_path_raises_value_error PASSED [  4%]
tests/test_type_safety_validation.py::TestInitValidation::test_non_string_model_path_int_raises_type_error PASSED [  7%]
tests/test_type_safety_validation.py::TestInitValidation::test_non_string_model_path_list_raises_type_error PASSED [  9%]
tests/test_type_safety_validation.py::TestInitValidation::test_non_string_model_path_dict_raises_type_error PASSED [ 12%]
tests/test_type_safety_validation.py::TestInitValidation::test_n_ctx_zero_raises_value_error PASSED [ 14%]
tests/test_type_safety_validation.py::TestInitValidation::test_n_ctx_negative_raises_value_error PASSED [ 17%]
tests/test_type_safety_validation.py::TestInitValidation::test_n_ctx_negative_large_raises_value_error PASSED [ 19%]
tests/test_type_safety_validation.py::TestInitValidation::test_n_ctx_positive_does_not_raise_validation_error PASSED [ 21%]
tests/test_type_safety_validation.py::TestInitValidation::test_n_ctx_one_passes_validation PASSED [ 24%]
tests/test_type_safety_validation.py::TestTokenizeValidation::test_int_text_raises_type_error PASSED [ 26%]
tests/test_type_safety_validation.py::TestTokenizeValidation::test_list_text_raises_type_error PASSED [ 29%]
tests/test_type_safety_validation.py::TestTokenizeValidation::test_none_text_raises_type_error PASSED [ 31%]
tests/test_type_safety_validation.py::TestTokenizeValidation::test_dict_text_raises_type_error PASSED [ 34%]
tests/test_type_safety_validation.py::TestTokenizeValidation::test_float_text_raises_type_error PASSED [ 36%]
tests/test_type_safety_validation.py::TestTokenizeValidation::test_str_text_is_accepted PASSED [ 39%]
tests/test_type_safety_validation.py::TestTokenizeValidation::test_bytes_text_is_accepted PASSED [ 41%]
tests/test_type_safety_validation.py::TestTokenizeValidation::test_empty_str_is_accepted PASSED [ 43%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_str_tokens_raises_type_error PASSED [ 46%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_int_tokens_raises_type_error PASSED [ 48%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_none_tokens_raises_type_error PASSED [ 51%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_tuple_tokens_raises_type_error PASSED [ 53%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_dict_tokens_raises_type_error PASSED [ 56%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_list_with_string_element_raises_type_error PASSED [ 58%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_list_with_float_element_raises_type_error PASSED [ 60%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_list_with_none_element_raises_type_error PASSED [ 63%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_valid_list_is_accepted PASSED [ 65%]
tests/test_type_safety_validation.py::TestDetokenizeValidation::test_empty_list_is_accepted PASSED [ 68%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_negative_temperature_raises_value_error PASSED [ 70%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_negative_temperature_minus_one_raises_value_error PASSED [ 73%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_top_p_above_one_raises_value_error PASSED [ 75%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_top_p_above_two_raises_value_error PASSED [ 78%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_top_p_negative_raises_value_error PASSED [ 80%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_negative_top_k_raises_value_error PASSED [ 82%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_negative_top_k_large_raises_value_error PASSED [ 85%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_valid_params_do_not_raise PASSED [ 87%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_boundary_temperature_zero PASSED [ 90%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_boundary_top_p_zero PASSED [ 92%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_boundary_top_p_one PASSED [ 95%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_boundary_top_k_zero PASSED [ 97%]
tests/test_type_safety_validation.py::TestCreateCompletionValidation::test_multiple_invalid_params_first_fails PASSED [100%]

======================= 41 passed in 1.51s =======================
```

## Backward Compatibility

These changes maintain backward compatibility:

1. **No breaking changes to valid code**: All existing code that passes valid parameters will continue to work exactly as before
2. **Early failure for invalid code**: Code that previously caused cryptic errors or undefined behavior now fails fast with clear messages
3. **No API changes**: Method signatures remain unchanged
4. **No behavioral changes**: Valid inputs produce identical outputs

The validation is purely additive - it catches errors earlier and provides better error messages, but does not change the behavior for any valid use case.

## Files Modified

- `llama_cpp/llama.py`: Added validation logic and updated docstrings (lines 202-209, 632-634, 656-661, 1904-1911)
- `tests/test_type_safety_validation.py`: New comprehensive test suite (41 tests)

## Code Statistics

- Lines changed: < 50 lines of validation code
- Test coverage: 41 test cases
- All tests passing: 100%


## 相关链接

- **源仓库**: [lxcxjxhx/llama-cpp-python](https://github.com/lxcxjxhx/llama-cpp-python)
- **PR 链接**: https://github.com/lxcxjxhx/llama-cpp-python/pull/2
- **Diff**: https://github.com/lxcxjxhx/llama-cpp-python/pull/2.diff

---
*Auto-generated at 2026-07-12 02:26:51 UTC*
