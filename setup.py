from __future__ import annotations

from pathlib import Path
import tomllib
from setuptools import find_packages, setup

ROOT = Path(__file__).resolve().parent


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_project_metadata() -> dict[str, object]:
    pyproject_text = read_text(ROOT / "pyproject.toml")
    data = tomllib.loads(pyproject_text)
    return data.get("project", {})


PROJECT_METADATA = load_project_metadata()


setup(
    name=PROJECT_METADATA["name"],
    version=PROJECT_METADATA["version"],
    description=PROJECT_METADATA.get("description", ""),
    long_description=read_text(ROOT / "README.md"),
    long_description_content_type="text/markdown",
    author=PROJECT_METADATA.get("authors", [{}])[0].get("name", ""),
    license=PROJECT_METADATA.get("license", {}).get("text", ""),
    python_requires=PROJECT_METADATA.get("requires-python", ">=3.11"),
    install_requires=PROJECT_METADATA.get("dependencies", []),
    extras_require=PROJECT_METADATA.get("optional-dependencies", {}),
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    package_data={"": ["*.md", "*.txt", "*.json", "*.yaml", "*.yml"]},
    entry_points={"console_scripts": ["acra=acra.cli:app_main"]},
    classifiers=PROJECT_METADATA.get("classifiers", []),
    keywords=PROJECT_METADATA.get("keywords", []),
    project_urls=PROJECT_METADATA.get("urls", {}),
)
