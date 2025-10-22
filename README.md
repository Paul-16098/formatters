# formatters

一個極簡、可組合的「文字格式化管線」執行器，外加一個基礎輔助元件（FormattersBase）與少量範例步驟。你可以把多個格式化步驟串成 pipeline，讓前一步的輸出成為下一步的輸入。

---

## 專案描述

- stdin → step1 → step2 → … → stdout 的串接資料流。
- 每個步驟可以是腳本路徑（.py 或含路徑分隔符）或是可匯入的模組名稱（以 `-m` 執行）。
- 執行器會將 `FormattersBase/src` 注入子程序的 PYTHONPATH，讓在本機未安裝套件時也能 `from formattersbase import FormattersBase`。

---

## 技術棧（Technology Stack）

- 語言與版本：Python 3.14+
- 打包/建置：uv（工作區使用 uv；`FormattersBase` 可用 `uv build` 建置）
- 主要模組/技術：
  - `subprocess.run(text=True)` 作為步驟之間的文字 I/O
  - `FormattersBase` 作為步驟的 stdin/stdout 薄封裝
  - 型別標註已啟用，並提供 `py.typed`

---

## 專案架構（Architecture）

高階概觀：

```text
stdin ─▶ [step 1] ─▶ [step 2] ─▶ … ─▶ stdout
             ▲
             │  每個 step 以子程序執行，上一個 stdout 會餵給下一個 stdin
```

要點：

- `main.py` 提供 CLI 與 `run_pipeline(data, steps)` API。
- 步驟偵測：若參數像「腳本」則直接執行；否則以 `python -m <module>` 執行。
- 子程序會帶入經過擴充的 `PYTHONPATH`，自動包含 `FormattersBase/src`。
- 文字 I/O 皆採文字模式，避免跨平台換行差異造成混淆。

---

## 快速開始（Getting Started）

前置需求：

- Python 3.14 以上 -（選用）uv：建置 `FormattersBase` 或封裝時使用

最常見用法：

- 以本機腳本路徑執行：

```pwsh
type some.txt | python main.py Formatters/none.py Formatters/no-2-new-line.py
```

```sh
python main.py Formatters/none.py Formatters/no-2-new-line.py <"some.txt"
```

- 以模組名稱執行（模組需在 `sys.path` 上可匯入）：

```pwsh
type some.txt | python -m formatters none no-2-new-line
```

```sh
python -m formatters none no-2-new-line <"some.txt"
```

- 安裝後的主控台指令（`pyproject.toml` 內的 `project.scripts`）：

```pwsh
uv tool install .
type some.txt | formatters Formatters/none.py Formatters/no-2-new-line.py
```

```sh
uv tool install .
formatters Formatters/none.py Formatters/no-2-new-line.py <"some.txt"
```

建置 `FormattersBase`（選用，若你需要 wheel/sdist）：

```pwsh
uv build FormattersBase
```

---

## 專案結構（Project Structure）

```text
.
├─ main.py                         # pipeline 執行器（CLI + run_pipeline）
├─ pyproject.toml                  # 專案定義與 console script 入口
├─ pyrightconfig.json              # 型別檢查設定
├─ Formatters/                     # 範例格式器步驟
│  ├─ none.py                      # no-op；示範如何使用 FormattersBase
│  └─ no-2-new-line.py             # 將 3+ 個連續換行壓成 1 個
├─ FormattersBase/                 # 基礎輔助元件（可獨立建置）
│  ├─ pyproject.toml
│  └─ src/formattersbase/__init__.py  # FormattersBase 內容
└─ .github/
  └─ copilot-instructions.md      # 開發與使用指南（AI 貢獻者）
```

---

## 主要功能（Key Features）

- Pipeline 執行器：
  - 以子程序依序執行每個格式化步驟，並串接 stdout → stdin。
  - 提供 Python API：`run_pipeline(data, steps)`，便於測試或整合。
- FormattersBase：
  - 進入 `with` 時自動讀取（當 stdin 為非 TTY 的情境），離開時輸出 `file_input`。
  - 步驟內只需純粹改寫 `f.file_input`，避免直接 `print`/自行讀 stdin。
- 範例步驟：
  - `none.py`：不變換，做為最小示例。

---

## 開發流程（Development Workflow）

- 新增步驟時，遵循「步驟慣例」：
  - 以單檔腳本 `Formatters/your-step.py` 實作。
  - 使用 `FormattersBase`，在 `with` 區塊中改寫 `f.file_input`。
  - 若使用正規表達式等昂貴操作，於模組載入時預先建立資源。
- 除了路徑，也可用模組名稱執行（以 `-m`）。
- 對於大型或第三方步驟，可獨立發佈套件後再以模組方式使用。

> 更多細節與背景，見 `.github/copilot-instructions.md`。

---

## 程式碼規範（Coding Standards）

- 以 `FormattersBase` 進行 I/O；步驟內避免直接觸碰 stdin/stdout。
- 步驟應該是可預測、可重現的純轉換：
  - 不做檔案/網路 I/O、不互動、不產生副作用。
- 型別標註：
  - 公開函式維持明確型別；本專案已提供 `py.typed` 與 `pyrightconfig.json`。
- 效能：
  - 熱路徑預先配置（例如 regex 預編譯）；避免在回圈中建立昂貴物件。
