from collections import defaultdict
from llama_index.packs.code_hierarchy.signature import (
    DEFAULT_SIGNATURE_IDENTIFIERS,
    SignatureCaptureOptions,
    SignatureIdentifiersByNodeType,
    get_node_name,
    get_node_signature,
)
from llama_index.packs.code_hierarchy.comments import (
    create_comment_line,
    get_replacement_text,
)
from tree_sitter import Node
from typing import Any, Dict, List, Optional, Sequence, Tuple


from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.extractors.metadata_extractors import BaseExtractor
from llama_index.core.node_parser.interface import NodeParser
from llama_index.core.schema import BaseNode, NodeRelationship, TextNode
from llama_index.core.text_splitter import CodeSplitter
from llama_index.core.utils import get_tqdm_iterable


class _ScopeItem(BaseModel):
    """Like a Node from tree_sitter, but with only the str information we need."""

    name: str
    type: str
    signature: str


class _ChunkNodeOutput(BaseModel):
    """The output of a chunk_node call."""

    this_document: Optional[TextNode]
    upstream_children_documents: List[TextNode]
    all_documents: List[TextNode]


class CodeHierarchyNodeParser(NodeParser):
    """Split code using a AST parser.

    Add metadata about the scope of the code block and relationships between
    code blocks.
    """

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "CodeHierarchyNodeParser"

    language: str = Field(
        description="The programming language of the code being split."
    )
    signature_identifiers: Dict[str, SignatureCaptureOptions] = Field(
        description=(
            "A dictionary mapping the type of a split mapped to the first and last type"
            " of itschildren which identify its signature."
        )
    )
    min_characters: int = Field(
        default=80,
        description=(
            "Minimum number of characters per chunk.Defaults to 80 because that's about"
            " how long a replacement comment is in skeleton mode."
        ),
    )
    code_splitter: Optional[CodeSplitter] = Field(
        description="The text splitter to use when splitting documents."
    )
    metadata_extractor: Optional[BaseExtractor] = Field(
        default=None, description="Metadata extraction pipeline to apply to nodes."
    )
    callback_manager: CallbackManager = Field(
        default_factory=CallbackManager, exclude=True
    )
    skeleton: bool = Field(
        True,
        description=(
            "Parent nodes have the text of their child nodes replaced with a signature"
            " and a comment instructing the language model to visit the child node for"
            " the full text of the scope."
        ),
    )

    def __init__(
        self,
        language: str,
        skeleton: bool = True,
        signature_identifiers: Optional[SignatureIdentifiersByNodeType] = None,
        code_splitter: Optional[CodeSplitter] = None,
        callback_manager: Optional[CallbackManager] = None,
        metadata_extractor: Optional[BaseExtractor] = None,
        chunk_min_characters: int = 80,
    ):
        callback_manager = callback_manager or CallbackManager([])

        if signature_identifiers is None:
            try:
                signature_identifiers = DEFAULT_SIGNATURE_IDENTIFIERS[language]
            except KeyError:
                raise ValueError(
                    f"Must provide signature_identifiers for language {language}."
                )

        super().__init__(
            include_prev_next_rel=False,
            language=language,
            callback_manager=callback_manager,
            metadata_extractor=metadata_extractor,
            code_splitter=code_splitter,
            signature_identifiers=signature_identifiers,
            min_characters=chunk_min_characters,
            skeleton=skeleton,
        )

    def _chunk_node(
        self,
        parent: Node,
        text: str,
        _context_list: Optional[List[_ScopeItem]] = None,
        _root: bool = True,
    ) -> _ChunkNodeOutput:
        """
        This is really the "main" method of this class. It is recursive and recursively
        chunks the text by the options identified in self.signature_identifiers.

        It is ran by get_nodes_from_documents.

        Args:
            parent (Node): The parent node to chunk
            text (str): The text of the entire document
            _context_list (Optional[List[_ScopeItem]]): The scope context of the
                                                        parent node
            _root (bool): Whether or not this is the root node
        """
        if _context_list is None:
            _context_list = []

        upstream_children_documents: List[TextNode] = []
        all_documents: List[TextNode] = []

        # Capture any whitespace before parent.start_byte
        # Very important for space sensitive languages like python
        start_byte = parent.start_byte
        while start_byte > 0 and text[start_byte - 1] in (" ", "\t"):
            start_byte -= 1

        # Create this node
        current_chunk = text[start_byte : parent.end_byte]

        # Return early if the chunk is too small
        if len(current_chunk) < self.min_characters and not _root:
            return _ChunkNodeOutput(
                this_document=None, all_documents=[], upstream_children_documents=[]
            )

        # TIP: This is a wonderful place to put a debug breakpoint when
        #      Trying to integrate a new language. Pay attention to parent.type to learn
        #      all the available node types and their hierarchy.
        if parent.type in self.signature_identifiers or _root:
            # Get the new context
            if not _root:
                new_context = _ScopeItem(
                    name=get_node_name(
                        node=parent, signature_identifiers=self.signature_identifiers
                    ),
                    type=parent.type,
                    signature=get_node_signature(
                        text=text,
                        node=parent,
                        signature_identifiers=self.signature_identifiers,
                    ),
                )
                _context_list.append(new_context)
            this_document = TextNode(
                text=current_chunk,
                metadata={
                    "inclusive_scopes": [cl.dict() for cl in _context_list],
                    "start_byte": start_byte,
                    "end_byte": parent.end_byte,
                },
                relationships={
                    NodeRelationship.CHILD: [],
                },
            )
            all_documents.append(this_document)
        else:
            this_document = None

        # Iterate over children
        for child in parent.children:
            if child.children:
                # Recurse on the child
                next_chunks = self._chunk_node(
                    child, text, _context_list=_context_list.copy(), _root=False
                )

                # If there is a this_document, then we need
                # to add the children to this_document
                # and flush upstream_children_documents
                if this_document is not None:
                    # If we have been given a document, that means it's children
                    # are already set, so it needs to become a child of this node
                    if next_chunks.this_document is not None:
                        assert not next_chunks.upstream_children_documents, (
                            "next_chunks.this_document and"
                            " next_chunks.upstream_children_documents are exclusive."
                        )
                        this_document.relationships[
                            NodeRelationship.CHILD
                        ].append(  # type: ignore
                            next_chunks.this_document.as_related_node_info()
                        )
                        next_chunks.this_document.relationships[
                            NodeRelationship.PARENT
                        ] = this_document.as_related_node_info()
                    # Otherwise, we have been given a list of
                    # upstream_children_documents. We need to make
                    # them a child of this node
                    else:
                        for d in next_chunks.upstream_children_documents:
                            this_document.relationships[
                                NodeRelationship.CHILD
                            ].append(  # type: ignore
                                d.as_related_node_info()
                            )
                            d.relationships[
                                NodeRelationship.PARENT
                            ] = this_document.as_related_node_info()
                # Otherwise we pass the children upstream
                else:
                    # If we have been given a document, that means it's
                    # children are already set, so it needs to become a
                    # child of the next node
                    if next_chunks.this_document is not None:
                        assert not next_chunks.upstream_children_documents, (
                            "next_chunks.this_document and"
                            " next_chunks.upstream_children_documents are exclusive."
                        )
                        upstream_children_documents.append(next_chunks.this_document)
                    # Otherwise, we have leftover children, they need
                    # to become children of the next node
                    else:
                        upstream_children_documents.extend(
                            next_chunks.upstream_children_documents
                        )

                # Lastly we need to maintain all documents
                all_documents.extend(next_chunks.all_documents)

        return _ChunkNodeOutput(
            this_document=this_document,
            upstream_children_documents=upstream_children_documents,
            all_documents=all_documents,
        )

    @staticmethod
    def get_code_hierarchy_from_nodes(
        nodes: Sequence[BaseNode],
        max_depth: int = -1,
    ) -> Tuple[Dict[str, Any], str]:
        """
        Creates a code hierarchy appropriate to put into a tool description or context
        to make it easier to search for code.

        Call after `get_nodes_from_documents` and pass that output to this function.
        """
        out: Dict[str, Any] = defaultdict(dict)

        def get_subdict(keys: List[str]) -> Dict[str, Any]:
            # Get the dictionary we are operating on
            this_dict = out
            for key in keys:
                if key not in this_dict:
                    this_dict[key] = defaultdict(dict)
                this_dict = this_dict[key]
            return this_dict

        def recur_inclusive_scope(node: BaseNode, i: int, keys: List[str]) -> None:
            if "inclusive_scopes" not in node.metadata:
                raise KeyError("inclusive_scopes not in node.metadata")
            if i >= len(node.metadata["inclusive_scopes"]):
                return
            scope = node.metadata["inclusive_scopes"][i]

            this_dict = get_subdict(keys)

            if scope["name"] not in this_dict:
                this_dict[scope["name"]] = defaultdict(dict)

            if i < max_depth or max_depth == -1:
                recur_inclusive_scope(node, i + 1, [*keys, scope["name"]])

        def dict_to_markdown(d: Dict[str, Any], depth: int = 0) -> str:
            markdown = ""
            indent = "  " * depth  # Two spaces per depth level

            for key, value in d.items():
                if isinstance(value, dict):  # Check if value is a dict
                    # Add the key with a bullet point and increase depth for nested dicts
                    markdown += f"{indent}- {key}\n{dict_to_markdown(value, depth + 1)}"
                else:
                    # Handle non-dict items if necessary
                    markdown += f"{indent}- {key}: {value}\n"

            return markdown

        for node in nodes:
            filepath = node.metadata["filepath"].split("/")
            filepath[-1] = filepath[-1].split(".")[0]
            recur_inclusive_scope(node, 0, filepath)

        return out, dict_to_markdown(out)

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[BaseNode]:
        """
        The main public method of this class.

        Parse documents into nodes.
        """
        out: List[BaseNode] = []

        try:
            import tree_sitter_languages
        except ImportError:
            raise ImportError(
                "Please install tree_sitter_languages to use CodeSplitter."
            )

        try:
            parser = tree_sitter_languages.get_parser(self.language)
        except Exception as e:
            print(
                f"Could not get parser for language {self.language}. Check "
                "https://github.com/grantjenks/py-tree-sitter-languages#license "
                "for a list of valid languages."
            )
            raise e  # noqa: TRY201

        nodes_with_progress = get_tqdm_iterable(
            nodes, show_progress, "Parsing documents into nodes"
        )
        for node in nodes_with_progress:
            text = node.text
            tree = parser.parse(bytes(text, "utf-8"))

            if (
                not tree.root_node.children
                or tree.root_node.children[0].type != "ERROR"
            ):
                # Chunk the code
                _chunks = self._chunk_node(tree.root_node, node.text)
                assert _chunks.this_document is not None, "Root node must be a chunk"
                chunks = _chunks.all_documents

                # Add your metadata to the chunks here
                for chunk in chunks:
                    chunk.metadata = {
                        "language": self.language,
                        **chunk.metadata,
                        **node.metadata,
                    }
                    chunk.relationships[
                        NodeRelationship.SOURCE
                    ] = node.as_related_node_info()

                if self.skeleton:
                    self._skeletonize_list(chunks)

                # Now further split the code by lines and characters
                # TODO: Test this and the relationships it creates
                if self.code_splitter:
                    new_nodes = []
                    for original_node in chunks:
                        new_split_nodes = self.code_splitter.get_nodes_from_documents(
                            [original_node], show_progress=show_progress, **kwargs
                        )

                        # Force the first new_split_node to have the
                        # same id as the original_node
                        new_split_nodes[0].id_ = original_node.id_

                        # Add the UUID of the next node to the end of all nodes
                        for i, new_split_node in enumerate(new_split_nodes[:-1]):
                            new_split_node.text = (
                                new_split_node.text
                                + "\n"
                                + create_comment_line(new_split_nodes[i + 1], 0)
                            ).strip()

                        # Add the UUID of the previous node to the beginning of all nodes
                        for i, new_split_node in enumerate(new_split_nodes[1:]):
                            new_split_node.text = (
                                create_comment_line(new_split_nodes[i])
                                + new_split_node.text
                            ).strip()

                        # Add the parent child info to all the new_nodes_
                        # derived from node
                        for new_split_node in new_split_nodes:
                            new_split_node.relationships[
                                NodeRelationship.CHILD
                            ] = original_node.child_nodes  # type: ignore
                            new_split_node.relationships[
                                NodeRelationship.PARENT
                            ] = original_node.parent_node  # type: ignore

                        # Go through chunks and replace all
                        # instances of node.node_id in relationships
                        # with new_nodes_[0].node_id
                        for old_node in chunks:
                            # Handle child nodes, which are a list
                            new_children = []
                            for old_nodes_child in old_node.child_nodes or []:
                                if old_nodes_child.node_id == original_node.node_id:
                                    new_children.append(
                                        new_split_nodes[0].as_related_node_info()
                                    )
                                new_children.append(old_nodes_child)
                            old_node.relationships[
                                NodeRelationship.CHILD
                            ] = new_children

                            # Handle parent node
                            if (
                                old_node.parent_node
                                and old_node.parent_node.node_id
                                == original_node.node_id
                            ):
                                old_node.relationships[
                                    NodeRelationship.PARENT
                                ] = new_split_nodes[0].as_related_node_info()

                        # Now save new_nodes_
                        new_nodes += new_split_nodes

                    chunks = new_nodes

                # Or just extract metadata
                if self.metadata_extractor:
                    chunks = self.metadata_extractor.process_nodes(  # type: ignore
                        chunks
                    )

                out += chunks
            else:
                raise ValueError(f"Could not parse code with language {self.language}.")

        return out

    @classmethod
    def _skeletonize(cls, parent_node: TextNode, child_node: TextNode) -> None:
        """WARNING: In Place Operation."""
        # Simple protection clauses
        if child_node.text not in parent_node.text:
            raise ValueError("The child text is not contained inside the parent text.")
        if child_node.node_id not in (c.node_id for c in parent_node.child_nodes or []):
            raise ValueError("The child node is not a child of the parent node.")

        # Now do the replacement
        replacement_text = get_replacement_text(child_node=child_node)
        parent_node.text = parent_node.text.replace(child_node.text, replacement_text)

    @classmethod
    def _skeletonize_list(cls, nodes: List[TextNode]) -> None:
        # Create a convenient map for mapping node id's to nodes
        node_id_map = {n.node_id: n for n in nodes}

        def recur(node: TextNode) -> None:
            # If any children exist, skeletonize ourselves, starting at the root DFS
            for child in node.child_nodes or []:
                child_node = node_id_map[child.node_id]
                cls._skeletonize(parent_node=node, child_node=child_node)
                recur(child_node)

        # Iterate over root nodes and recur
        for n in nodes:
            if n.parent_node is None:
                recur(n)
