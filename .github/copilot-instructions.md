## AI contributor guide for this repo

This repository provides a simple “text formatting pipeline” runner plus a tiny base helper used by individual formatter steps.

### Big picture

- Data flow is stdin → step1 → step2 → … → stdout. The runner executes each step as a subprocess and pipes the previous step’s stdout into the next step’s stdin.
- Steps can be either script paths (end with .py or contain a path separator) or importable module names (run with -m).
- The runner adds `FormattersBase/src` to child PYTHONPATH so local scripts can `from formattersbase import FormattersBase` without installing.

Key files/directories:

- `main.py`: pipeline runner. Exposes `run_pipeline(data, steps)` and a CLI (`project.scripts.formatters -> main:main`).
- `FormattersBase/src/formattersbase/__init__.py`: defines `FormattersBase`, a context manager that reads piped stdin (non-TTY) on enter and writes its final `file_input` to stdout on exit.
- `Formatters/none.py`: no-op step using `FormattersBase`.
- `Formatters/no-2-new-line.py`: collapses runs of 3+ newlines to a single newline; exposes a pure helper `collapse_excess_newlines()` and wraps via `FormattersBase`.

### Develop & run

- Quick run (local scripts):
  - PowerShell: `type some.txt | python main.py Formatters/none.py Formatters/no-2-new-line.py`
- As modules (requires the modules to be importable on sys.path):
  - `type some.txt | python -m formatters none no-2-new-line`
- Installed console script (after project install):
  - `type some.txt | formatters Formatters/none.py Formatters/no-2-new-line.py`

Build/install notes:

- Python 3.14 is required (see `pyproject.toml`).
- Workspace uses uv; `FormattersBase` builds with `uv build FormattersBase` (produces wheel/sdist). The runner usually doesn’t require installing `FormattersBase` thanks to PYTHONPATH injection.

### Formatter step conventions (important)

- Always use `FormattersBase` in a `with` block. Don’t read stdin manually and don’t print; mutate `f.file_input` and let `__exit__` write stdout.
- Keep steps pure and deterministic. Prefer a small pure function (e.g., `collapse_excess_newlines(text)`) plus a thin CLI wrapper using `FormattersBase`.
- Avoid side effects (files, network, logs) and avoid interactive prompts; the pipeline expects plain text transforms.
- If performance-sensitive, precompile regex at import time (see `no-2-new-line.py`).

### Adding a new formatter

- Add a single-file script under `Formatters/your-step.py` that:
  - imports `FormattersBase`
  - defines optional pure helpers for unit-level testing
  - wraps the transform in `with FormattersBase() as f: f.file_input = transform(f.file_input)`
- Use by path: `python main.py Formatters/your-step.py`. To use by module name, ensure your module is importable (install or adjust PYTHONPATH).

### Debugging & tips

- Run an individual step standalone: `type input.txt | python Formatters/no-2-new-line.py`.
- The runner decides script vs module via simple heuristic: path separators or `.py` → script; otherwise `-m`.
- Text I/O uses Python text mode (`text=True` in `subprocess.run`); be mindful of newline normalization across platforms.

### Reference

- Entry point: `formatters = "main:main"` in `pyproject.toml`.
- Type hints are enabled; `FormattersBase` ships `py.typed`. A `pyrightconfig.json` exists for type checking.

If anything here feels incomplete (e.g., preferred test harness, packaging of third-party steps), call it out and we’ll extend this guide with concrete repo-backed examples.
