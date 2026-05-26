from pathlib import Path
from typing import Annotated
import time
import os
from langchain.tools import tool  # adjust if your framework uses a different decorator


# ======================================================
# Workspace configuration
# ======================================================

WORKSPACE_ROOT = Path("D:/IVP AI Boost/fogbugz-chat/python").resolve()

LOCK_TIMEOUT = 5.0
LOCK_POLL_INTERVAL = 0.05


# ======================================================
# Path Resolution
# ======================================================

def _resolve_path(filepath: str) -> Path:
    """
    Resolve a safe path within agent_memory.
    """
    cleaned = filepath.lstrip("/\\").upper().replace(" ", "")
    target = None
    if "QUERY_HISTORY" in cleaned:
        target = WORKSPACE_ROOT / "agent_memory/QUERY_HISTORY.md"
    elif "USER_PREFERENCES" in cleaned:
        target = WORKSPACE_ROOT / "agent_memory/USER_PREFERENCES.md"
    else:
        target = WORKSPACE_ROOT / "agent_memory/AGENT_MEMORY.md"

    target = target.resolve()

    try:
        target.relative_to(WORKSPACE_ROOT)
    except ValueError:
        raise ValueError(f"Access denied: {filepath}")

    return target


# ======================================================
# Locking (Atomic + Windows-safe)
# ======================================================

def _acquire_lock(path: Path) -> Path:
    """
    Atomically acquire a lock file.
    """
    lock = path.with_suffix(path.suffix + ".lock")
    start = time.time()

    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lock
        except FileExistsError:
            if time.time() - start > LOCK_TIMEOUT:
                raise TimeoutError(f"Timeout acquiring lock for {path.name}")
            time.sleep(LOCK_POLL_INTERVAL)


def _release_lock(lock: Path):
    """
    Safely release lock without crashing on Windows.
    """
    for _ in range(5):
        try:
            if lock.exists():
                lock.unlink()
            return
        except PermissionError:
            time.sleep(0.05)

    print(f"[WARN] Failed to delete lock: {lock}")


# ======================================================
# Atomic File Write
# ======================================================

def _atomic_append(path: Path, content: str):
    """
    Append safely using full rewrite + atomic replace.
    """
    existing = ""

    if path.exists():
        try:
            existing = path.read_text(encoding="utf-8")
        except Exception:
            # Rare edge: file being replaced mid-read
            time.sleep(0.01)
            existing = path.read_text(encoding="utf-8")

    new_content = existing + content

    temp_path = path.with_suffix(path.suffix + ".tmp")

    with temp_path.open("w", encoding="utf-8") as f:
        f.write(new_content)
        f.flush()
        os.fsync(f.fileno())

    os.replace(temp_path, path)


# ======================================================
# Tools
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

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"ERROR reading file: {str(e)}"


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
        _atomic_append(path, content.rstrip() + "\n")
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
        _atomic_append(path, line.rstrip() + "\n")
    finally:
        _release_lock(lock)

    return f"OK: Appended {len(line)} characters to {filepath}"


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

    block = f"\n## {block_title}\n{content.rstrip()}\n"

    lock = _acquire_lock(path)
    try:
        _atomic_append(path, block)
    finally:
        _release_lock(lock)

    return f"OK: Appended block '{block_title}' to {filepath}"


def write_block_function(
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

    block = f"\n## {block_title}\n{content.rstrip()}\n"

    lock = _acquire_lock(path)
    try:
        _atomic_append(path, block)
    finally:
        _release_lock(lock)

    return f"OK: Appended block '{block_title}' to {filepath}"