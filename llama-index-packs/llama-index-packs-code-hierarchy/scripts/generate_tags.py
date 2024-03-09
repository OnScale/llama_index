from pathlib import Path
from llama_index.packs.code_hierarchy import CodeHierarchyNodeParser

from llama_index.core.readers import SimpleDirectoryReader

import json


def main() -> int:
    exit_code = 0
    for language, file_extension in [
        ("c_sharp", "cs"),
        ("c", "c"),
        ("cpp", "cpp"),
        ("go", "go"),
        ("java", "java"),
        ("javascript", "js"),
        ("php", "php"),
        ("python", "py"),
        ("ruby", "rb"),
        ("rust", "rs"),
        ("typescript", "ts"),
    ]:
        print(f"Processing {language}")
        files = SimpleDirectoryReader(
            input_files=Path("llama_index/packs/code_hierarchy/queries/").glob(
                f"*.{file_extension}"
            )
        ).load_data()
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
