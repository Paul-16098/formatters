"""Pipeline runner for formatter scripts/modules.

- Reads stdin once.
- For each argument, treats it as either a script path (endswith .py or contains a path
  separator) or a module name to run via ``-m``.
 - Feeds previous step's stdout as next step's stdin.

This file preserves the original CLI behavior, and also exposes ``run_pipeline``
for easier testing.
"""

import os
import subprocess
import sys
from typing import Iterable


def _cmd_for(name: str) -> list[str]:
    """Build the command to execute a formatter step.

    - If ``name`` looks like a script path, execute it directly.
    - Otherwise run it as a module with ``-m``.
    """
    is_script = name.endswith(".py") or ("/" in name or "\\" in name)
    return [sys.executable, name] if is_script else [sys.executable, "-m", name]


def _child_env_with_formattersbase() -> dict[str, str]:
    """Return a child-process env that includes FormattersBase/src on PYTHONPATH.

    This allows running formatter scripts/modules without needing to install
    the package locally. If FormattersBase/src is missing, falls back silently.
    """
    env = os.environ.copy()
    # Ensure child processes read/write UTF-8 and allow surrogate code points
    # to round-trip without raising encode/decode errors on Windows pipes.
    # See: https://docs.python.org/3/library/codecs.html#codecs-error-handlers
    env["PYTHONIOENCODING"] = "utf-8:surrogatepass"
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "FormattersBase", "src"),  # when running from repo checkout
        os.path.join(
            os.getcwd(), "FormattersBase", "src"
        ),  # when installed but run in repo cwd
    ]
    for fb_src in candidates:
        if os.path.isdir(fb_src):
            existing = env.get("PYTHONPATH", "")
            sep = os.pathsep if existing else ""
            env["PYTHONPATH"] = f"{existing}{sep}{fb_src}"
            break
    return env


def run_pipeline(data: str, steps: Iterable[str]) -> str:
    """Run the given formatter steps sequentially.

    Args:
        data: Initial stdin content.
        steps: Sequence of script paths or module names.

    Returns:
        Final stdout produced by the last step (or the original data if no steps).
    """
    out = data
    env = _child_env_with_formattersbase()
    for name in steps:
        completed = subprocess.run(
            _cmd_for(name),
            # Encode using UTF-8 with surrogateescape to avoid locale code page
            # errors on Windows and preserve any lone surrogates from upstream.
            input=out,
            text=True,
            encoding="utf-8",
            errors="surrogatepass",
            capture_output=True,
            check=True,
            env=env,
        )
        out = completed.stdout
    return out


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    # Normalize stdin/stdout to UTF-8 for pipeline robustness on Windows PowerShell
    # try:
    #     sys.stdout.reconfigure(encoding="utf-8", errors="surrogatepass")
    # except Exception:
    #     # Older Pythons may not support reconfigure in certain environments
    #     pass

    # Read stdin as bytes first to avoid mis-decoding when the console code page
    # is not UTF-8 (common on Windows). Prefer UTF-8, then fall back.
    if sys.stdin is not None and not sys.stdin.isatty():
        raw = sys.stdin.buffer.read()
        data: str
        try:
            data = raw.decode(sys.stdin.encoding)
            # print(sys.stdin.encoding)
        except UnicodeDecodeError as e:
            try:
                # print(e)
                data = raw.decode("utf-8")
                # print("utf-8")
            except UnicodeDecodeError:
                data = raw.decode("cp65001", errors="backslashreplace")
                # print("cp65001")
    else:
        data = ""
    result = run_pipeline(data, argv[1:])
    sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
