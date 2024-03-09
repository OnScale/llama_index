"""
A basic example of a tree-sitter grammar for Python.
"""


@foo
class Example:
    """A simple example class"""

    def __init__(self, name: str) -> None:
        self.name = name

    def say_hello(self):
        """A simple example method"""
        print(f"Hello, {self.name}!")

    @bar
    def baz(self):
        pass


def foo(bar: str) -> None:
    """A simple example function"""


@bar
def baz():
    pass
