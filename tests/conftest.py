"""Shared pytest fixtures and paths."""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Return the absolute path of the repository root."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def sample_data_dir(repo_root: Path) -> Path:
    """Return the path to data/ containing provided sample CSV files."""
    return repo_root / "data"


@pytest.fixture(scope="session")
def test_data_dir(repo_root: Path) -> Path:
    """Return the path to tests/data/ containing purpose-built test fixtures."""
    return repo_root / "tests" / "data"
