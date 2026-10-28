import pytest

from app.core.exceptions import DiffLimitExceededException
from app.services.diff_parser import DiffParser


def test_parse_simple_diff(clean_code_diff):
    summary = DiffParser.parse_diff(clean_code_diff)
    assert summary.total_files == 1
    assert summary.total_additions == 6
    assert summary.total_deletions == 0

    file = summary.files[0]
    assert file.path == "app/math.py"
    assert file.change_type == "added"
    assert len(file.hunks) == 1

    hunk = file.hunks[0]
    added_lines = DiffParser.get_added_line_numbers(hunk)
    assert len(added_lines) == 6
    assert added_lines[0] == (1, 'def add(a: int, b: int) -> int:')

def test_parse_multi_hunk_diff():
    diff_text = """diff --git a/src/index.ts b/src/index.ts
--- a/src/index.ts
+++ b/src/index.ts
@@ -10,3 +10,4 @@
 context line
-old line
+new line 1
+new line 2
@@ -25,2 +26,3 @@
 line a
+line b
"""
    summary = DiffParser.parse_diff(diff_text)
    assert summary.total_files == 1
    assert summary.total_additions == 3
    assert summary.total_deletions == 1
    assert len(summary.files[0].hunks) == 2

def test_oversized_diff_limit():
    huge_diff = "diff --git a/big.txt b/big.txt\n" + ("+line\n" * 200_000)
    with pytest.raises(DiffLimitExceededException):
        DiffParser.parse_diff(huge_diff)
