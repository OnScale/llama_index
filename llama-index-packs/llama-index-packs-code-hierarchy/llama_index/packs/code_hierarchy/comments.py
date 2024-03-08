"""
Allows you to create comments for code skeletonization.
"""

from enum import Enum
from typing import Dict, Tuple

from llama_index.core.bridge.pydantic import BaseModel
from llama_index_client import TextNode


class ScopeMethod(Enum):
    """
    Enum for the different methods of handling scope by language.
    Some use brackets, some use indentions, and there are others.
    """

    INDENTATION = "INDENTATION"
    BRACKETS = "BRACKETS"


class CommentOptions(BaseModel):
    """
    Using a template with replaceable brackets, and the scope method, we can create a comment.
    """

    comment_template: str
    scope_method: ScopeMethod


"""
Very important that you have one of these for every "language" that you want to
support.
"""
COMMENT_OPTIONS: Dict[str, CommentOptions] = {
    "c_sharp": CommentOptions(
        comment_template="// {}", scope_method=ScopeMethod.BRACKETS
    ),
    "c": CommentOptions(comment_template="// {}", scope_method=ScopeMethod.BRACKETS),
    "cpp": CommentOptions(comment_template="// {}", scope_method=ScopeMethod.BRACKETS),
    "elisp": CommentOptions(
        comment_template=";; {}", scope_method=ScopeMethod.INDENTATION
    ),
    "elixir": CommentOptions(
        comment_template="# {}", scope_method=ScopeMethod.INDENTATION
    ),
    "elm": CommentOptions(
        comment_template="-- {}", scope_method=ScopeMethod.INDENTATION
    ),
    "go": CommentOptions(comment_template="// {}", scope_method=ScopeMethod.BRACKETS),
    "java": CommentOptions(comment_template="// {}", scope_method=ScopeMethod.BRACKETS),
    "javascript": CommentOptions(
        comment_template="// {}", scope_method=ScopeMethod.BRACKETS
    ),
    "ocaml": CommentOptions(
        comment_template="(* {} *)", scope_method=ScopeMethod.INDENTATION
    ),
    "php": CommentOptions(comment_template="// {}", scope_method=ScopeMethod.BRACKETS),
    "python": CommentOptions(
        comment_template="# {}", scope_method=ScopeMethod.INDENTATION
    ),
    "ql": CommentOptions(comment_template="// {}", scope_method=ScopeMethod.BRACKETS),
    "ruby": CommentOptions(
        comment_template="# {}", scope_method=ScopeMethod.INDENTATION
    ),
    "rust": CommentOptions(comment_template="// {}", scope_method=ScopeMethod.BRACKETS),
    "typescript": CommentOptions(
        comment_template="// {}", scope_method=ScopeMethod.BRACKETS
    ),
}


def get_indentation(text: str) -> Tuple[str, int, int]:
    indent_char = None
    minimum_chain = None

    # Check that text is at least 1 line long
    text_split = text.splitlines()
    if len(text_split) == 0:
        raise ValueError("Text should be at least one line long.")

    for line in text_split:
        stripped_line = line.lstrip()

        if stripped_line:
            # Get whether it's tabs or spaces
            spaces_count = line.count(" ", 0, len(line) - len(stripped_line))
            tabs_count = line.count("\t", 0, len(line) - len(stripped_line))

            if not indent_char:
                if spaces_count:
                    indent_char = " "
                if tabs_count:
                    indent_char = "\t"

            # Detect mixed indentation.
            if spaces_count > 0 and tabs_count > 0:
                raise ValueError("Mixed indentation found.")
            if indent_char == " " and tabs_count > 0:
                raise ValueError("Mixed indentation found.")
            if indent_char == "\t" and spaces_count > 0:
                raise ValueError("Mixed indentation found.")

            # Get the minimum chain of indent_char
            if indent_char:
                char_count = line.count(indent_char, 0, len(line) - len(stripped_line))
                if minimum_chain is not None:
                    if char_count > 0:
                        minimum_chain = min(char_count, minimum_chain)
                else:
                    if char_count > 0:
                        minimum_chain = char_count

    # Handle edge case
    if indent_char is None:
        indent_char = " "
    if minimum_chain is None:
        minimum_chain = 4

    # Get the first indent count
    first_line = text_split[0]
    first_indent_count = 0
    for char in first_line:
        if char == indent_char:
            first_indent_count += 1
        else:
            break

    # Return the default indent level if only one indentation level was found.
    return indent_char, minimum_chain, first_indent_count // minimum_chain


def get_comment_text(node: TextNode) -> str:
    """Gets just the natural language text for a skeletonize comment."""
    return f"Code replaced for brevity. See node_id {node.node_id}"


def create_comment_line(cls, node: TextNode, indention_lvl: int = -1) -> str:
    """
    Creates a comment line for a node.

    Sometimes we don't use this in a loop because it requires recalculating
    a lot of the same information. But it is handy.
    """
    # Create the text to replace the child_node.text with
    language = node.metadata["language"]
    if language not in COMMENT_OPTIONS:
        # TODO: Create a contribution message
        raise KeyError("Language not yet supported. Please contribute!")
    comment_options = COMMENT_OPTIONS[language]
    (
        indentation_char,
        indentation_count_per_lvl,
        first_indentation_lvl,
    ) = get_indentation(node.text)
    if indention_lvl != -1:
        first_indentation_lvl = indention_lvl
    else:
        first_indentation_lvl += 1
    return (
        indentation_char * indentation_count_per_lvl * first_indentation_lvl
        + comment_options.comment_template.format(cls._get_comment_text(node))
        + "\n"
    )


def get_replacement_text(cls, child_node: TextNode) -> str:
    """
    Manufactures a the replacement text to use to skeletonize a given child node.
    """
    signature = child_node.metadata["inclusive_scopes"][-1]["signature"]
    language = child_node.metadata["language"]
    if language not in COMMENT_OPTIONS:
        # TODO: Create a contribution message
        raise KeyError("Language not yet supported. Please contribute!")
    comment_options = COMMENT_OPTIONS[language]

    # Create the text to replace the child_node.text with
    (
        indentation_char,
        indentation_count_per_lvl,
        first_indentation_lvl,
    ) = get_indentation(child_node.text)

    # Start with a properly indented signature
    replacement_txt = (
        indentation_char * indentation_count_per_lvl * first_indentation_lvl + signature
    )

    # Add brackets if necessary. Expandable in the
    # future to other methods of scoping.
    if comment_options.scope_method == ScopeMethod.BRACKETS:
        replacement_txt += " {\n"
        replacement_txt += (
            indentation_char * indentation_count_per_lvl * (first_indentation_lvl + 1)
            + comment_options.comment_template.format(cls._get_comment_text(child_node))
            + "\n"
        )
        replacement_txt += (
            indentation_char * indentation_count_per_lvl * first_indentation_lvl + "}"
        )

    elif comment_options.scope_method == ScopeMethod.INDENTATION:
        replacement_txt += "\n"
        replacement_txt += indentation_char * indentation_count_per_lvl * (
            first_indentation_lvl + 1
        ) + comment_options.comment_template.format(cls._get_comment_text(child_node))

    # TODO: Add back in when we have an HTML scm file
    # elif comment_options.scope_method == ScopeMethod.HTML_END_TAGS:
    #     tag_name = child_node.metadata["inclusive_scopes"][-1]["name"]
    #     end_tag = f"</{tag_name}>"
    #     replacement_txt += "\n"
    #     replacement_txt += (
    #         indentation_char
    #         * indentation_count_per_lvl
    #         * (first_indentation_lvl + 1)
    #         + comment_options.comment_template.format(
    #             cls._get_comment_text(child_node)
    #         )
    #         + "\n"
    #     )
    #     replacement_txt += (
    #         indentation_char * indentation_count_per_lvl * first_indentation_lvl
    #         + end_tag
    #     )

    else:
        raise KeyError(f"Unrecognized enum value {comment_options.scope_method}")

    return replacement_txt
