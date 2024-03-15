"""
Reads the example files in the `llama_index/examples/languages/` directory and processes them using the
`CodeHierarchyNodeParser` to generate the JSON and Markdown outputs for each language. The outputs are saved in the
`examples/outputs/` directory.
"""

from pathlib import Path
from llama_index.packs.code_hierarchy import CodeHierarchyNodeParser

from llama_index.core.readers import SimpleDirectoryReader

import json

from llama_index.packs.code_hierarchy.signature import DEFAULT_SIGNATURE_IDENTIFIERS


def main() -> int:
    """
    Reads the example files in the `llama_index/examples/languages/` directory and processes them using the
    `CodeHierarchyNodeParser` to generate the JSON and Markdown outputs for each language. The outputs are saved in the
    `examples/outputs/` directory.
    """
    exit_code = 0
    file_extensions = {
        "c_sharp": "cs",
        "c": "c",
        "cpp": "cpp",
        "go": "go",
        "java": "java",
        "javascript": "js",
        "php": "php",
        "python": "py",
        "ruby": "rb",
        "rust": "rs",
        "typescript": "ts",
        "html": "html",
    }
    for language in DEFAULT_SIGNATURE_IDENTIFIERS:
        file_extension = file_extensions[language]
        print(f"Processing {language}")
        files = list(
            SimpleDirectoryReader(
                input_files=Path("llama_index/examples/languages/").glob(
                    f"*.{file_extension}"
                )
            ).load_data()
        )
        assert len(files) != 0, f"No files found matching glob *.{file_extension}"
        assert (
            len(files) > 1
        ), f"More than one file found matching glob *.{file_extension}"
        parser = CodeHierarchyNodeParser(language=language, skeleton=True)
        try:
            nodes = parser.get_nodes_from_documents(files)
        except Exception as e:
            print(f"Error processing {language}: {e}")
            exit_code = 1
            continue

        # A simple test for empty parsing
        if len(nodes) == 0 or len(nodes) == 1:
            print(f"Error processing {language}: No nodes found")
            exit_code = 1
            continue

        with open(f"examples/outputs/{language}.json", "w") as f:
            json.dump([node.dict() for node in nodes], f, indent=4)
        with open(f"examples/outputs/{language}.md", "w") as f:
            for node in nodes:
                f.write(f"## {node.node_id}\n\n")
                f.write(f"```{language}\n{node.text}\n```\n\n")

    return exit_code


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
