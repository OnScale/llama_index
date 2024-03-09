from .generate_tags import main
import git


def test_generate_tags():
    assert main() == 0


def test_no_changes():
    repo = git.Repo(search_parent_directories=True)
    assert not repo.is_dirty(untracked_files=False)
