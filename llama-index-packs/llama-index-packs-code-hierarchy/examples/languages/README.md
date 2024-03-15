# Getting tag names

To get tag names for a language, [install the tree-sitter-cli](https://tree-sitter.github.io/tree-sitter/creating-parsers#installation)

Then run `tree-sitter init-config`

Then create a `~/src` directory as described https://dcreager.net/2021/06/getting-started-with-tree-sitter/

Then install the following languages:

```bash
cd ~/src
git clone https://github.com/tree-sitter/tree-sitter-python
git clone https://github.com/tree-sitter/tree-sitter-c-sharp
git clone https://github.com/tree-sitter/tree-sitter-c
git clone https://github.com/tree-sitter/tree-sitter-cpp
git clone https://github.com/tree-sitter/tree-sitter-go
git clone https://github.com/tree-sitter/tree-sitter-java
git clone https://github.com/tree-sitter/tree-sitter-javascript
git clone https://github.com/tree-sitter/tree-sitter-php
git clone https://github.com/tree-sitter/tree-sitter-rust
git clone https://github.com/tree-sitter/tree-sitter-typescript
```

Now you may parse the example files like so:

For the python example:

`tree-sitter query tree-sitter-python-tags.scm test/highlight/tree-sitter-python-tags.py`

NOTE: I generated most of these examples via chatgpt

# Contributing

Please run `python scripts/generate_tags.py` to get output examples for each query. Please commit these files so we can know when they change and compare them.
