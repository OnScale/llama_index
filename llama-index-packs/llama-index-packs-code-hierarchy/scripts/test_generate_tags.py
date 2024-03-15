from .generate_tags import main
import git


def test_generate_tags():
    """
    Test that all the example files are processed without errors.
    """
    assert main() == 0


def test_no_changes():
    """
    Test that all example changes have been committed for PR review. Useful in CICD.
    """
    repo = git.Repo(search_parent_directories=True)
    assert not repo.is_dirty(untracked_files=False)
