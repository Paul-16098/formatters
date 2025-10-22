import contextlib
import sys
from types import TracebackType
from typing import Self


__all__ = ["FormattersBase"]


class FormattersBase(contextlib.AbstractContextManager["FormattersBase"]):
    """Simple context manager that captures (optional) stdin text and
    writes the final value to stdout upon exit.

    Inside the context, mutate the ``file_input`` attribute (e.g. ``cm.file_input = 'x'``)
    so the updated value is what gets written on exit.
    """

    file_input: str

    def __init__(self, file_input: str | None = None):
        """Initialize the context manager.

        If ``file_input`` is None, attempts to read from stdin only when stdin
        is not a TTY (i.e., when data is piped). Otherwise, defaults to empty string.
        """
        # Avoid blocking on import: only read stdin if provided via pipe (not a TTY)
        if file_input is None:
            if not sys.stdin.isatty():  # data is being piped
                file_input = sys.stdin.read()
            else:
                file_input = ""
        self.file_input = str(file_input)

    def __enter__(self) -> Self:
        """Return the manager itself so callers can mutate ``.file_input``."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Write current ``file_input`` to stdout. Do not suppress exceptions."""
        sys.stdout.write(self.file_input)
