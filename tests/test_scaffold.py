"""Offline acceptance checks for the M0 scaffold."""

import os
from importlib import import_module
from importlib.metadata import version
from pathlib import Path
from shutil import copyfile

import pytest
from fastapi import FastAPI
from pydantic import ValidationError

from askdocs.config import Settings

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Load checked-in defaults without reading developer credentials."""
    for name in list(os.environ):
        if name.lower().split("__", maxsplit=1)[0] in Settings.model_fields:
            monkeypatch.delenv(name)
    (tmp_path / "config").mkdir()
    copyfile(ROOT / "config/app.yaml", tmp_path / "config/app.yaml")
    monkeypatch.chdir(tmp_path)


def test_package_and_api_import_without_services() -> None:
    assert version("askdocs")
    for package in ("ingest", "retrieval", "generation", "obs", "api", "evals"):
        assert import_module(f"askdocs.{package}")
    assert isinstance(import_module("askdocs.api.main").app, FastAPI)


def test_defaults_load_without_credentials() -> None:
    settings = Settings()
    assert settings.models.embedding
    assert settings.models.reranker
    assert settings.chunking.size_tokens > settings.chunking.overlap_tokens
    assert settings.retrieval.top_k > 0
    assert settings.llm_api_key.get_secret_value() == ""
    assert settings.llm_model == ""


def test_environment_overrides_dotenv_and_yaml(monkeypatch: pytest.MonkeyPatch) -> None:
    Path(".env").write_text(
        "LLM_MODEL=dotenv-model\nLLM_PRICE_INPUT_PER_M=1.5\n", encoding="utf-8"
    )
    monkeypatch.setenv("LLM_MODEL", "environment-model")
    monkeypatch.setenv("LLM_PRICE_INPUT_PER_M", "2.5")
    settings = Settings()
    assert settings.llm_model == "environment-model"
    assert settings.llm_price_input_per_m == 2.5


def test_dotenv_and_secret_redaction() -> None:
    Path(".env").write_text(
        "LLM_API_KEY=unit-test-secret\nLLM_PRICE_INPUT_PER_M=1.5\n",
        encoding="utf-8",
    )
    settings = Settings()
    assert settings.llm_api_key.get_secret_value() == "unit-test-secret"
    assert "unit-test-secret" not in repr(settings)
    assert settings.llm_price_input_per_m == 1.5


@pytest.mark.parametrize("overlap", [-1, 128, 129])
def test_invalid_chunk_overlap_is_rejected(overlap: int) -> None:
    with pytest.raises(ValidationError):
        Settings(chunking={"size_tokens": 128, "overlap_tokens": overlap})


def test_invalid_retrieval_count_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETRIEVAL__TOP_K", "0")
    with pytest.raises(ValidationError):
        Settings()


def test_negative_price_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PRICE_INPUT_PER_M", "-1")
    with pytest.raises(ValidationError):
        Settings()
