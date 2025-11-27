#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
################################################################################

import os
import subprocess
from pathlib import Path

import pytest

import run_omop_es


def run_subprocess_with_defaults(
    command, cwd=None, check=True, capture_output=True, text=False
) -> subprocess.CompletedProcess:
    """Run a subprocess command and return the output."""
    result = subprocess.run(
        command, cwd=cwd, check=check, capture_output=capture_output, text=text
    )
    return result


@pytest.fixture(scope="session")
def temp_gitrepo(tmp_path_factory):
    """Creates a temporary directory with git repository and changes to it."""
    old_wd = os.getcwd()
    repo_path = tmp_path_factory.mktemp("test_repo")
    os.chdir(repo_path)
    yield
    os.chdir(old_wd)


@pytest.fixture(scope="session")
def mock_git_repo(temp_gitrepo):
    """Create a temporary git repository with branches, tags, and commits for testing."""

    repo_path = Path(os.getcwd())

    # Initialize git repo; note that `git init -b` doesn't work on the GAE's version of git
    # so we switch to 'main' branch explicitly
    run_subprocess_with_defaults(["git", "init"])
    run_subprocess_with_defaults(["git", "checkout", "-b", "main"])
    run_subprocess_with_defaults(["git", "config", "user.email", "test@test.com"])
    run_subprocess_with_defaults(["git", "config", "user.name", "Test User"])

    # Create initial commit
    (repo_path / "README.md").write_text("Initial commit")
    run_subprocess_with_defaults(["git", "add", "."], check=True, capture_output=True)
    run_subprocess_with_defaults(
        ["git", "commit", "-m", "Initial commit"],
        check=True,
        capture_output=True,
    )

    # Get the commit SHA
    result = run_subprocess_with_defaults(["git", "rev-parse", "HEAD"], text=True)
    commit_sha = result.stdout.strip()

    # Create a tag
    run_subprocess_with_defaults(["git", "tag", "v1.0.0"])

    # Create a feature branch
    run_subprocess_with_defaults(["git", "checkout", "-b", "feature"])
    (repo_path / "feature.txt").write_text("Feature content")
    run_subprocess_with_defaults(["git", "add", "."])
    run_subprocess_with_defaults(["git", "commit", "-m", "Add feature"])

    # Switch back to main
    run_subprocess_with_defaults(["git", "checkout", "main"])

    return {
        "path": repo_path,
        "url": str(repo_path),
        "commit_sha": commit_sha,
        "short_sha": commit_sha[:7],
    }


def test_validate_ref_with_valid_branch(mock_git_repo):
    """Test that validate_ref succeeds with a valid branch name."""
    run_omop_es.validate_ref(mock_git_repo["url"], "main")


def test_validate_ref_with_valid_tag(mock_git_repo):
    """Test that validate_ref succeeds with a valid tag."""
    run_omop_es.validate_ref(mock_git_repo["url"], "v1.0.0")


def test_validate_ref_with_valid_commit_sha(mock_git_repo):
    """Test that validate_ref succeeds with a valid commit SHA."""
    run_omop_es.validate_ref(mock_git_repo["url"], mock_git_repo["commit_sha"])


def test_validate_ref_with_invalid_ref(mock_git_repo):
    """Test that validate_ref raises RuntimeError with an invalid ref."""
    with pytest.raises(RuntimeError, match="Failed to fetch reference"):
        run_omop_es.validate_ref(mock_git_repo["url"], "nonexistent_branch_xyz")


def test_get_latest_commit_sha_with_branch(mock_git_repo):
    """Test that get_latest_commit_sha returns a valid SHA for a branch."""
    sha = run_omop_es.get_latest_commit_sha(mock_git_repo["url"], "main")
    assert run_omop_es.is_valid_sha(sha)
    assert len(sha) == 40


def test_get_latest_commit_sha_with_tag(mock_git_repo):
    """Test that get_latest_commit_sha returns a valid SHA for a tag."""
    sha = run_omop_es.get_latest_commit_sha(mock_git_repo["url"], "v1.0.0")
    assert run_omop_es.is_valid_sha(sha)
    assert len(sha) == 40
    assert sha == mock_git_repo["commit_sha"]


def test_get_latest_commit_sha_with_full_sha(mock_git_repo):
    """Test that get_latest_commit_sha returns the same SHA when given a full SHA."""
    result = run_omop_es.get_latest_commit_sha(
        mock_git_repo["url"], mock_git_repo["commit_sha"]
    )
    assert result == mock_git_repo["commit_sha"]


def test_get_latest_commit_sha_with_short_sha(mock_git_repo):
    """Test that get_latest_commit_sha returns the same SHA when given a short SHA."""
    result = run_omop_es.get_latest_commit_sha(
        mock_git_repo["url"], mock_git_repo["short_sha"]
    )
    assert result == mock_git_repo["short_sha"]


def test_get_latest_commit_sha_with_invalid_ref(mock_git_repo):
    """Test that get_latest_commit_sha raises RuntimeError with an invalid ref."""
    with pytest.raises(RuntimeError, match="Failed to fetch reference"):
        run_omop_es.get_latest_commit_sha(
            mock_git_repo["url"], "nonexistent_branch_xyz"
        )


def test_get_latest_commit_sha_with_invalid_sha(mock_git_repo):
    """Test that get_latest_commit_sha raises RuntimeError with an invalid SHA."""
    non_existent_sha = "1234567890abcdef1234567890abcdef12345678"
    assert run_omop_es.is_valid_sha(non_existent_sha)
    with pytest.raises(RuntimeError, match="Failed to fetch reference"):
        run_omop_es.get_latest_commit_sha(mock_git_repo["url"], non_existent_sha)
