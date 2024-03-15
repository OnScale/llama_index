"""Custom way of extracting names and signatures from nodes.
TODO: Handle this with scm file types instead like https://tree-sitter.github.io/tree-sitter/syntax-highlighting .
"""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from tree_sitter import Node


class SignatureCaptureType(BaseModel):
    """
    Unfortunately some languages need special options for how to make a signature.

    For example, html element signatures should include their closing >, there is no
    easy way to include this using an always-exclusive system.

    However, using an always-inclusive system, python decorators don't work,
    as there isn't an easy to define terminator for decorators that is inclusive
    to their signature.
    """

    type: str = Field(description="The type string to match on.")
    inclusive: bool = Field(
        description=(
            "Whether to include the text of the node matched by this type or not."
        ),
    )


class SignatureCaptureOptions(BaseModel):
    """
    Options for capturing the signature of a node.
    """

    start_signature_types: Optional[List[SignatureCaptureType]] = Field(
        None,
        description=(
            "A list of node types any of which indicate the beginning of the signature."
            "If this is none or empty, use the start_byte of the node."
        ),
    )
    end_signature_types: Optional[List[SignatureCaptureType]] = Field(
        None,
        description=(
            "A list of node types any of which indicate the end of the signature."
            "If this is none or empty, use the end_byte of the node."
        ),
    )
    name_identifier: str = Field(
        description=(
            "The node type to use for the signatures 'name'.If retrieving the name is"
            " more complicated than a simple type match, use a function which takes a"
            " node and returns true or false as to whether its the name or not. The"
            " first match is returned."
        )
    )


"""
Maps language -> Node Type -> SignatureCaptureOptions

The best way for a developer to discover these is to put a breakpoint at the TIP
tag in _chunk_node, and then create a unit test for some code, and then iterate
through the code discovering the node names.
"""
SignatureIdentifiersByNodeType = Dict[str, SignatureCaptureOptions]
SignatureIdentifiersByLanguageByNodeType = Dict[str, SignatureIdentifiersByNodeType]
DEFAULT_SIGNATURE_IDENTIFIERS: SignatureIdentifiersByLanguageByNodeType = {
    "python": {
        "function_definition": SignatureCaptureOptions(
            end_signature_types=[SignatureCaptureType(type="block", inclusive=False)],
            name_identifier="identifier",
        ),
        "class_definition": SignatureCaptureOptions(
            end_signature_types=[SignatureCaptureType(type="block", inclusive=False)],
            name_identifier="identifier",
        ),
    },
    "html": {
        "element": SignatureCaptureOptions(
            start_signature_types=[SignatureCaptureType(type="<", inclusive=True)],
            end_signature_types=[SignatureCaptureType(type=">", inclusive=True)],
            name_identifier="tag_name",
        )
    },
    "cpp": {
        "class_specifier": SignatureCaptureOptions(
            end_signature_types=[SignatureCaptureType(type="{", inclusive=False)],
            name_identifier="type_identifier",
        ),
        "function_definition": SignatureCaptureOptions(
            end_signature_types=[SignatureCaptureType(type="{", inclusive=False)],
            name_identifier="function_declarator",
        ),
    },
    "typescript": {
        "interface_declaration": SignatureCaptureOptions(
            end_signature_types=[SignatureCaptureType(type="{", inclusive=False)],
            name_identifier="type_identifier",
        ),
        "lexical_declaration": SignatureCaptureOptions(
            end_signature_types=[SignatureCaptureType(type="{", inclusive=False)],
            name_identifier="identifier",
        ),
        "function_declaration": SignatureCaptureOptions(
            end_signature_types=[SignatureCaptureType(type="{", inclusive=False)],
            name_identifier="identifier",
        ),
        "class_declaration": SignatureCaptureOptions(
            end_signature_types=[SignatureCaptureType(type="{", inclusive=False)],
            name_identifier="type_identifier",
        ),
        "method_definition": SignatureCaptureOptions(
            end_signature_types=[SignatureCaptureType(type="{", inclusive=False)],
            name_identifier="property_identifier",
        ),
    },
}


def get_node_name(
    node: Node,
    signature_identifiers: SignatureIdentifiersByLanguageByNodeType = DEFAULT_SIGNATURE_IDENTIFIERS,
) -> str:
    """Get the name of a tree sitter node."""
    signature_identifier = signature_identifiers[node.type]

    def recur(node: Node) -> str:
        for child in node.children:
            if child.type == signature_identifier.name_identifier:
                return child.text.decode()
            if child.children:
                out = recur(child)
                if out:
                    return out
        return ""

    return recur(node).strip()


def get_node_signature(
    text: str,
    node: Node,
    signature_identifiers: SignatureIdentifiersByLanguageByNodeType = DEFAULT_SIGNATURE_IDENTIFIERS,
) -> str:
    """Get the signature of a tree sitter node."""
    signature_identifier = signature_identifiers[node.type]

    def find_start(node: Node) -> Optional[int]:
        if not signature_identifier.start_signature_types:
            signature_identifier.start_signature_types = []

        for st in signature_identifier.start_signature_types:
            if node.type == st.type:
                if st.inclusive:
                    return node.start_byte
                return node.end_byte

        for child in node.children:
            out = find_start(child)
            if out is not None:
                return out

        return None

    def find_end(node: Node) -> Optional[int]:
        if not signature_identifier.end_signature_types:
            signature_identifier.end_signature_types = []

        for st in signature_identifier.end_signature_types:
            if node.type == st.type:
                if st.inclusive:
                    return node.end_byte
                return node.start_byte

        for child in node.children:
            out = find_end(child)
            if out is not None:
                return out

        return None

    start_byte, end_byte = find_start(node), find_end(node)
    if start_byte is None:
        start_byte = node.start_byte
    if end_byte is None:
        end_byte = node.end_byte
    return text[start_byte:end_byte].strip()
