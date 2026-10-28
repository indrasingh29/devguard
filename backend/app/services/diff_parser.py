import re
from typing import List, Optional, Tuple

from app.core.config import settings
from app.core.exceptions import DiffLimitExceededException
from app.schemas.pull_request import ChangedFile, ChangedHunk, DiffSummary

HUNK_HEADER_REGEX = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")

class DiffParser:
    """
    Parses unified git diff output into structured changed files, hunks,
    and line-number mappings for precise static analysis.
    """

    @classmethod
    def parse_diff(cls, raw_diff: str) -> DiffSummary:
        if len(raw_diff.encode("utf-8")) > settings.MAX_DIFF_BYTES:
            raise DiffLimitExceededException(
                f"Diff size ({len(raw_diff.encode('utf-8'))} bytes) exceeds configured limit of {settings.MAX_DIFF_BYTES} bytes"
            )

        files: List[ChangedFile] = []
        raw_files = cls._split_into_file_diffs(raw_diff)

        if len(raw_files) > settings.MAX_DIFF_FILES:
            raise DiffLimitExceededException(
                f"Number of changed files ({len(raw_files)}) exceeds configured limit of {settings.MAX_DIFF_FILES}"
            )

        total_additions = 0
        total_deletions = 0

        for file_diff in raw_files:
            parsed_file = cls._parse_single_file_diff(file_diff)
            if parsed_file:
                files.append(parsed_file)
                total_additions += parsed_file.additions
                total_deletions += parsed_file.deletions

        return DiffSummary(
            total_files=len(files),
            total_additions=total_additions,
            total_deletions=total_deletions,
            files=files
        )

    @classmethod
    def _split_into_file_diffs(cls, raw_diff: str) -> List[str]:
        # Split diff by "diff --git " marker
        parts = re.split(r"(?=^diff --git )", raw_diff, flags=re.MULTILINE)
        return [p for p in parts if p.strip()]

    @classmethod
    def _parse_single_file_diff(cls, file_diff: str) -> Optional[ChangedFile]:
        lines = file_diff.splitlines()
        if not lines:
            return None

        # Check git diff header: e.g. "diff --git a/path/to/file b/path/to/file"
        header_match = re.match(r"^diff --git a/(.*) b/(.*)$", lines[0])
        old_path = header_match.group(1) if header_match else None
        new_path = header_match.group(2) if header_match else None

        change_type = "modified"
        is_binary = False

        # Scan header lines
        idx = 1
        while idx < len(lines) and not lines[idx].startswith("@@"):
            line = lines[idx]
            if "new file mode" in line:
                change_type = "added"
            elif "deleted file mode" in line:
                change_type = "deleted"
            elif "similarity index" in line or "rename from" in line:
                change_type = "renamed"
            elif "Binary files" in line:
                is_binary = True
            elif line.startswith("--- a/"):
                old_path = line[6:]
            elif line.startswith("+++ b/"):
                new_path = line[6:]
            idx += 1

        path = new_path or old_path or "unknown"
        if path == "/dev/null" and old_path:
            path = old_path

        hunks: List[ChangedHunk] = []
        additions = 0
        deletions = 0

        if not is_binary:
            current_hunk_lines: List[str] = []
            current_old_start = 0
            current_old_len = 0
            current_new_start = 0
            current_new_len = 0
            current_header = ""

            for i in range(idx, len(lines)):
                line = lines[i]
                hunk_match = HUNK_HEADER_REGEX.match(line)
                if hunk_match:
                    if current_hunk_lines:
                        hunks.append(ChangedHunk(
                            old_start=current_old_start,
                            old_length=current_old_len,
                            new_start=current_new_start,
                            new_length=current_new_len,
                            header=current_header,
                            lines=current_hunk_lines
                        ))
                        current_hunk_lines = []

                    current_old_start = int(hunk_match.group(1))
                    current_old_len = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                    current_new_start = int(hunk_match.group(3))
                    current_new_len = int(hunk_match.group(4)) if hunk_match.group(4) else 1
                    current_header = line
                elif line.startswith("+") and not line.startswith("+++"):
                    additions += 1
                    current_hunk_lines.append(line)
                elif line.startswith("-") and not line.startswith("---"):
                    deletions += 1
                    current_hunk_lines.append(line)
                elif line.startswith(" ") or line == "":
                    current_hunk_lines.append(line)

            if current_hunk_lines:
                hunks.append(ChangedHunk(
                    old_start=current_old_start,
                    old_length=current_old_len,
                    new_start=current_new_start,
                    new_length=current_new_len,
                    header=current_header,
                    lines=current_hunk_lines
                ))

        return ChangedFile(
            path=path,
            old_path=old_path if old_path != path else None,
            change_type=change_type,
            additions=additions,
            deletions=deletions,
            patch=file_diff,
            hunks=hunks,
            is_binary=is_binary
        )

    @classmethod
    def get_added_line_numbers(cls, hunk: ChangedHunk) -> List[Tuple[int, str]]:
        """
        Returns a list of (line_number, line_content) for all added/modified lines in the new file.
        """
        result: List[Tuple[int, str]] = []
        current_new_line = hunk.new_start

        for line in hunk.lines:
            if line.startswith("+"):
                result.append((current_new_line, line[1:]))
                current_new_line += 1
            elif line.startswith("-"):
                # Deleted line does not increment new file line counter
                pass
            else:
                # Context line
                current_new_line += 1

        return result
