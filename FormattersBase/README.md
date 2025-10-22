# FormattersBase

提供一個簡單的內容管線上下文管理器 `FormattersBase`：

- 若未提供 `file_input`，在 stdin 有資料且非 TTY 時自動讀取。
- 在離開 with 內容時，將 `file_input` 的最新值寫到 stdout。

範例：

```python
from formattersbase import FormattersBase

with FormattersBase() as f:
    f.file_input = f.file_input.upper()
```

本元件在撰寫時有考慮可近用性，但仍建議以工具（例如 Accessibility Insights）與人工測試進一步驗證。
