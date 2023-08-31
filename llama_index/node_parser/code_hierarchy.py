from typing import Any, List, Optional, Sequence

from pydantic import Field
from tree_sitter import Node
from llama_index.callbacks.base import CallbackManager
from llama_index.callbacks.schema import CBEventType, EventPayload
from llama_index.node_parser.extractors.metadata_extractors import MetadataExtractor
from llama_index.node_parser.interface import NodeParser
from llama_index.node_parser.simple import SimpleNodeParser
from llama_index.schema import BaseNode, Document, NodeRelationship, TextNode
from llama_index.text_splitter.code_splitter import CodeSplitter
from llama_index.utils import get_tqdm_iterable
from pydantic import BaseModel

# TODO: Expand these for new languages
DEFAULT_NAME_IDENTIFIERS = {
    "python": ["identifier"],
    "javascript": ["identifier", "type_identifier", "property_identifier"],
    "typescript": ["identifier", "type_identifier", "property_identifier"],
    "html": ["start_tag"],
    "cpp": ["function_declarator", "type_identifier"],
}

DEFAULT_SPLIT_ON_TYPES = {
    "python": ["function_definition", "class_definition"],
    "javascript": [
        "function_declaration",
        "class_declaration",
        "lexical_declaration",
        "method_definition",
    ],
    "typescript": [
        "function_declaration",
        "class_declaration",
        "interface_declaration",
        "method_definition",
        "lexical_declaration",
    ],
    "html": ["element"],
    "cpp": ["class_specifier", "function_definition"],
}


class _ScopeItem(BaseModel):
    """Like a Node from tree_sitter, but with only the str information we need."""

    name: str
    type: str


class _ChunkNodeOutput(BaseModel):
    """The output of a chunk_node call."""

    this_document: Optional[TextNode]
    children_documents: List[TextNode]


class CodeBlockNodeParser(NodeParser):
    """Split code using a AST parser.

    Add metadata about the scope of the code block and relationships between
    code blocks.
    """

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return cls.__name__

    language: str = Field(
        description="The programming languge of the code being split."
    )
    split_on_types: List[str] = Field(description="The types of nodes to split on.")
    name_identifiers: List[str] = Field(
        description="The types of nodes to use as the name of the scope."
    )
    min_characters: int = Field(
        default=0, description="Minimum number of characters per chunk."
    )
    code_splitter: Optional[CodeSplitter] = Field(
        description="The text splitter to use when splitting documents."
    )
    metadata_extractor: Optional[MetadataExtractor] = Field(
        default=None, description="Metadata extraction pipeline to apply to nodes."
    )
    callback_manager: CallbackManager = Field(
        default_factory=CallbackManager, exclude=True
    )

    def __init__(
        self,
        language: str,
        split_on_types: Optional[List[str]] = None,
        name_identifiers: Optional[List[str]] = None,
        code_splitter: Optional[CodeSplitter] = None,
        callback_manager: Optional[CallbackManager] = None,
        metadata_extractor: Optional[MetadataExtractor] = None,
        min_characters: int = 0,
    ):
        callback_manager = callback_manager or CallbackManager([])
        if split_on_types is None:
            try:
                split_on_types = DEFAULT_SPLIT_ON_TYPES[language]
            except KeyError:
                # TODO: Provide documentation on how to discover this
                # TODO: request user make a PR to add this language
                raise ValueError(
                    f"Must provide split_on_types for language {language}."
                )

        if name_identifiers is None:
            try:
                name_identifiers = DEFAULT_NAME_IDENTIFIERS[language]
            except KeyError:
                raise ValueError(
                    f"Must provide name_identifiers for language {language}."
                )

        super().__init__(
            language=language,
            callback_manager=callback_manager,
            metadata_extractor=metadata_extractor,
            split_on_types=split_on_types,
            name_identifiers=name_identifiers,
            code_splitter=code_splitter,
            min_characters=min_characters,
        )

    def _get_node_name(self, node: Node) -> str:
        """Get the name of a node."""

        def recur(node: Node) -> str:
            for child in node.children:
                if child.type in self.name_identifiers:
                    return child.text
                if child.children:
                    return recur(child)
            return ""

        return recur(node)

    def _chunk_node(
        self,
        parent: Node,
        text: str,
        _context_list: Optional[List[_ScopeItem]] = None,
        _root: bool = True,
    ) -> _ChunkNodeOutput:
        """
        Args:
            parent (Node): The parent node to chunk
            text (str): The text of the entire document
            _context_list (Optional[List[_ScopeItem]]): The scope context of the parent node
            _root (bool): Whether or not this is the root node
        """
        if _context_list is None:
            _context_list = []

        child_documents: List[TextNode] = []

        # Create this node
        current_chunk = text[parent.start_byte : parent.end_byte]

        # Return early if the chunk is too small
        if len(current_chunk) < self.min_characters and not _root:
            return _ChunkNodeOutput(
                this_document=None,
                children_documents=[],
            )

        if parent.type in self.split_on_types or _root:
            # Get the new context
            if not _root:
                new_context = _ScopeItem(
                    name=self._get_node_name(parent),
                    type=parent.type,
                )
                _context_list.append(new_context)
            this_document = TextNode(
                text=current_chunk,
                metadata={
                    "inclusive_scopes": [cl.dict() for cl in _context_list],
                },
                relationships={
                    NodeRelationship.CHILD: [],
                },
            )
        else:
            this_document = None

        # Iterate over children
        for child in parent.children:
            if child.children:
                # Recurse on the child
                next_chunks = self._chunk_node(
                    child, text, _context_list=_context_list.copy(), _root=False
                )

                # If there is a this_document, then we need to add the children to this_document
                if this_document is not None:
                    # If there is both a this_document inside next_chunks and this_document, then we need to add the next_chunks.this_document to this_document as a child
                    if next_chunks.this_document is not None:
                        this_document.relationships[NodeRelationship.CHILD].append(
                            next_chunks.this_document.as_related_node_info()
                        )
                        next_chunks.this_document.relationships[
                            NodeRelationship.PARENT
                        ] = this_document.as_related_node_info()

                    # If there is not a this_document inside next_chunks then we need to add the children to this_document as children
                    else:
                        this_document.relationships[NodeRelationship.CHILD].extend(
                            next_chunks.children_documents
                        )
                        for child_document in next_chunks.children_documents:
                            child_document.relationships[
                                NodeRelationship.PARENT
                            ] = this_document.as_related_node_info()

                # Add the new document to the list, flatten the structure by adding the next_chunks.this_document to the list as well
                if next_chunks.this_document is not None:
                    child_documents.append(next_chunks.this_document)
                child_documents.extend(next_chunks.children_documents)

        return _ChunkNodeOutput(
            this_document=this_document,
            children_documents=child_documents,
        )

    def get_nodes_from_documents(
        self,
        documents: Sequence[Document],
        show_progress: bool = False,
    ) -> List[BaseNode]:
        """Parse documents into nodes.

        Args:
            documents (Sequence[Document]): documents to parse

        """
        out: List[BaseNode] = []
        with self.callback_manager.event(
            CBEventType.CHUNKING,
            payload={EventPayload.CHUNKS: [document.text for document in documents]},
        ) as event:
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
                raise e

            documents_with_progress = get_tqdm_iterable(
                documents, show_progress, "Parsing documents into nodes"
            )
            for document in documents_with_progress:
                text = document.text
                tree = parser.parse(bytes(text, "utf-8"))

                if (
                    not tree.root_node.children
                    or tree.root_node.children[0].type != "ERROR"
                ):
                    # Chunk the code
                    _chunks = self._chunk_node(tree.root_node, document.text)
                    assert (
                        _chunks.this_document is not None
                    ), "Root node must be a chunk"
                    chunks = [_chunks.this_document] + _chunks.children_documents

                    # Add your metadata to the chunks here
                    for chunk in chunks:
                        chunk.metadata = {
                            "language": self.language,
                            **chunk.metadata,
                            **document.metadata,
                        }
                        chunk.relationships[
                            NodeRelationship.SOURCE
                        ] = document.as_related_node_info()

                    # Now further split the code by lines and characters
                    if self.code_splitter:
                        simple = SimpleNodeParser(
                            text_splitter=self.code_splitter,
                            include_metadata=True,
                            include_prev_next_rel=True,
                            metadata_extractor=self.metadata_extractor,
                            callback_manager=self.callback_manager,
                        )
                        chunks = simple.process_nodes(chunks)

                    # Or just extract metadata
                    elif self.metadata_extractor:
                        chunks = self.metadata_extractor.process_nodes(chunks)

                    event.on_end(
                        payload={EventPayload.CHUNKS: chunks},
                    )

                    out += chunks
                else:
                    raise ValueError(
                        f"Could not parse code with language {self.language}."
                    )

        return out