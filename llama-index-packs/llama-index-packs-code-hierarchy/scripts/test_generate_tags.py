from .generate_tags import main


def test_generate_tags():
    assert main() == 0
