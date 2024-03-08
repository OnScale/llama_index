from pathlib import Path
from llama_index.packs.code_hierarchy.comments import COMMENT_OPTIONS, get_indentation
import pytest
import re


def test_space_indentation() -> None:
    text = """\
def function():
    print("First level of indentation")
    if True:
        print("Second level of indentation")
"""
    (
        indent_char,
        count_per_indent,
        first_indent_level,
    ) = get_indentation(text)
    assert indent_char == " "
    assert count_per_indent == 4
    assert first_indent_level == 0


def test_tab_indentation() -> None:
    text = """\
def function():
\tprint("First level of indentation")
\tif True:
\t\tprint("Second level of indentation")
"""
    (
        indent_char,
        count_per_indent,
        first_indent_level,
    ) = get_indentation(text)
    assert indent_char == "\t"
    assert count_per_indent == 1
    assert first_indent_level == 0


def test_tab_indentation_2() -> None:
    text = """\
\tdef function():
\t\tprint("First level of indentation")
\t\tif True:
\t\t\tprint("Second level of indentation")
"""
    (
        indent_char,
        count_per_indent,
        first_indent_level,
    ) = get_indentation(text)
    assert indent_char == "\t"
    assert count_per_indent == 1
    assert first_indent_level == 1


def test_mixed_indentation() -> None:
    text = """\
def function():
\tprint("First level of indentation")
    if True:
        print("Second level of indentation")
"""
    with pytest.raises(ValueError, match="Mixed indentation found."):
        get_indentation(text)


def test_mixed_indentation_2() -> None:
    text = """\
\tdef function():
  print("First level of indentation")
    if True:
        print("Second level of indentation")
"""
    with pytest.raises(ValueError, match="Mixed indentation found."):
        get_indentation(text)


def test_no_indentation() -> None:
    text = """\"
def function():
print("No indentation")
"""
    (
        indent_char,
        count_per_indent,
        first_indent_level,
    ) = get_indentation(text)
    assert indent_char == " "
    assert count_per_indent == 4
    assert first_indent_level == 0


def test_typescript() -> None:
    text = """\
class Example {
    exampleMethod() {
        console.log("line1");
    }
}
"""
    (
        indent_char,
        count_per_indent,
        first_indent_level,
    ) = get_indentation(text)
    assert indent_char == " "
    assert count_per_indent == 4
    assert first_indent_level == 0


def test_typescript_2() -> None:
    text = """\
function foo() {
    console.log("bar");
}

class Example {
    exampleMethod() {
        console.log("line1");
    }
}

function baz() {
    console.log("bbq");
}"""
    (
        indent_char,
        count_per_indent,
        first_indent_level,
    ) = get_indentation(text)
    assert indent_char == " "
    assert count_per_indent == 4
    assert first_indent_level == 0


def test_all_languages_supported():
    """Checks that all languages in the queries folder are represented in the comments.py file."""
    # Load all files from ../queries
    for file in (Path(__file__).parent.parent / "queries").glob("*.scm"):
        # The language name is in the capture group tree-sitter-(.*)-tags.scm
        language = re.match(r"tree-sitter-(.*)-tags.scm", file.name).group(1)
        # Check that the language is in the COMMENT_OPTIONS
        assert language in COMMENT_OPTIONS
