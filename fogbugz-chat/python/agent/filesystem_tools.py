from pathlib import Path
from typing import Annotated
import time
import os
from langchain.tools import tool  # adjust if your framework uses a different decorator


# ======================================================
# Workspace configuration
# ======================================================

# IMPORTANT:
WORKSPACE_ROOT = Path("D:/IVP AI Boost/fogbugz-chat/python").resolve()
LOCK_TIMEOUT = 5.0          # seconds to wait for a file lock
LOCK_POLL_INTERVAL = 0.05  # seconds between lock checks


# ======================================================
# Internal helpers (NOT tools)
# ======================================================



def _resolve_path(filepath: str) -> Path:
    """
    Resolve a relative filepath safely within WORKSPACE_ROOT.

    - Blocks absolute paths
    - Blocks path traversal
    - Works correctly on Windows
    """
    # Normalize user input
    cleaned = filepath.lstrip("/\\")  # <-- CRITICAL FIX
    target = None
    if "QUERY_HISTORY" in cleaned.upper().replace(" ",""):
        target = (WORKSPACE_ROOT / "agent_memory/QUERY_HISTORY.md").resolve()
    elif "USER_PREFERENCES" in cleaned.upper().replace(" ",""):
        target = (WORKSPACE_ROOT / "agent_memory/USER_PREFERENCES.md").resolve()
    else:
        target = (WORKSPACE_ROOT / "agent_memory/AGENT_MEMORY.md").resolve()

    try:
        target.relative_to(WORKSPACE_ROOT)
    except ValueError:
        raise ValueError(f"Access denied: {filepath}")

    return target



def _acquire_lock(path: Path) -> Path:
    """
    Acquire a simple file-based lock to prevent concurrent writes.
    """
    lock = path.with_suffix(path.suffix + ".lock")
    start = time.time()

    while lock.exists():
        if time.time() - start > LOCK_TIMEOUT:
            raise TimeoutError(f"Timeout acquiring lock for {path.name}")
        time.sleep(LOCK_POLL_INTERVAL)

    lock.touch()
    return lock


def _release_lock(lock: Path):
    """
    Release a previously acquired file lock.
    """
    if lock.exists():
        lock.unlink()


# ======================================================
# Public agent tools
# ======================================================

@tool
def read_from_file(
    filepath: Annotated[str, "Relative path to the file inside the agent memory workspace"]
) -> str:
    """
    Read the full contents of a text file from the workspace.

    Use this tool when:
    - You need to inspect existing file contents
    - You want to understand a file's structure before appending
    - You are continuing or modifying an existing artifact

    INPUTS:
    - filepath (str): Relative path inside the agent memory workspace. Should be agent_memory/AGENT_MEMORY.md or agent_memory/QUERY_HISTORY.md or agent_memory/USER_PREFERENCES.md only.

    RETURNS:
    - str:
        • The full file contents if the file exists
        • An error message if the file does not exist or is not a file
    """
    path = _resolve_path(filepath)

    if not path.exists():
        return f"ERROR: File does not exist: {filepath}"

    if not path.is_file():
        return f"ERROR: Not a file: {filepath}"

    return path.read_text(encoding="utf-8")


@tool
def write_to_file(
    filepath: Annotated[str, "Relative path to the file inside the workspace"],
    content: Annotated[str, "Raw content to append to the file"]
) -> str:
    """
    Append raw content to a file without modifying it.

    IMPORTANT:
    - This tool DOES NOT add a newline automatically
    - Use this only for raw or pre-formatted content

    Use this tool when:
    - You are appending generated text exactly as-is
    - You are continuing a structured file and manage formatting yourself

    INPUTS:
    - filepath (str): Relative path inside the workspace directory
    - content (str): Raw content to append

    RETURNS:
    - str:
        • Confirmation message with number of characters written
        • Raises an error if the write fails
    """
    path = _resolve_path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    lock = _acquire_lock(path)
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(content)
    finally:
        _release_lock(lock)

    return f"OK: Appended {len(content)} characters to {filepath}"


@tool
def append_line(
    filepath: Annotated[str, "Relative path to the file inside the agent memory workspace"],
    line: Annotated[str, "Single line of text to append"]
) -> str:
    """
    Append exactly one newline-terminated line to a file.

    This tool ALWAYS ensures:
    - Exactly one trailing newline
    - No accidental blank lines

    Use this tool when:
    - Writing logs
    - Appending bullet points
    - Appending JSONL entries
    - Adding single statements

    INPUTS:
    - filepath (str): Relative path inside the agent memory workspace.  Should be agent_memory/AGENT_MEMORY.md or agent_memory/QUERY_HISTORY.md or agent_memory/USER_PREFERENCES.md only.
    - line (str): Single line of text (newline will be added automatically)

    RETURNS:
    - str:
        • Confirmation message indicating one line was appended
    """
    path = _resolve_path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    lock = _acquire_lock(path)
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(line.rstrip() + "\n")
    finally:
        _release_lock(lock)

    return f"OK: Appended 1 line to {filepath}"


@tool
def write_block(
    filepath: Annotated[str, "Relative path to the file inside the agent memory workspace"],
    block_title: Annotated[str, "Title of the block or section"],
    content: Annotated[str, "Content belonging to this block"]
) -> str:
    """
    Append a structured, markdown-style block to a file.

    Format written:
    - Blank line
    - Markdown level-2 header (##)
    - Block content
    - Trailing newline

    Use this tool when:
    - Writing documents
    - Adding sections to markdown files
    - Creating clearly separated content blocks

    INPUTS:
    - filepath (str): Relative path inside the agent memory workspace. Should be agent_memory/AGENT_MEMORY.md or agent_memory/QUERY_HISTORY.md or agent_memory/USER_PREFERENCES.md only.
    - block_title (str): Title of the section (used as markdown header)
    - content (str): Body content for the block

    RETURNS:
    - str:
        • Confirmation message indicating the block was appended
    """
    path = _resolve_path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    lock = _acquire_lock(path)
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(f"\n## {block_title}\n")
            f.write(content.rstrip() + "\n")
    finally:
        _release_lock(lock)

    return f"OK: Appended block '{block_title}' to {filepath}"
