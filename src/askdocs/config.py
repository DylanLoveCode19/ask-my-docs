"""Validated configuration loaded from environment, .env, and config/app.yaml."""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class ModelConfig(BaseModel):
    """Local model identifiers; models are loaded in later milestones."""

    model_config = ConfigDict(extra="forbid")
    embedding: str = Field(min_length=1)
    reranker: str = Field(min_length=1)


class ChunkingConfig(BaseModel):
    """Token budget and overlap for future ingestion."""

    model_config = ConfigDict(extra="forbid")
    size_tokens: int = Field(gt=0)
    overlap_tokens: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_overlap(self) -> Self:
        """Require overlap to leave room for new tokens in each chunk."""
        if self.overlap_tokens >= self.size_tokens:
            raise ValueError("overlap_tokens must be smaller than size_tokens")
        return self


class RetrievalConfig(BaseModel):
    """Candidate counts and the reciprocal rank fusion constant."""

    model_config = ConfigDict(extra="forbid")
    bm25_top_n: int = Field(gt=0)
    dense_top_n: int = Field(gt=0)
    fusion_top_m: int = Field(gt=0)
    top_k: int = Field(gt=0)
    rrf_k: int = Field(gt=0)


class Settings(BaseSettings):
    """Runtime settings; instantiate from the repository working directory."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        yaml_file="config/app.yaml",
        yaml_file_encoding="utf-8",
        extra="forbid",
    )

    models: ModelConfig
    chunking: ChunkingConfig
    retrieval: RetrievalConfig
    llm_base_url: str = ""
    llm_api_key: SecretStr = SecretStr("")
    llm_model: str = ""
    judge_base_url: str = ""
    judge_api_key: SecretStr = SecretStr("")
    judge_model: str = ""
    llm_price_input_per_m: float = Field(ge=0)
    llm_price_output_per_m: float = Field(ge=0)
    langfuse_public_key: str = ""
    langfuse_secret_key: SecretStr = SecretStr("")
    langfuse_host: str = "https://cloud.langfuse.com"
    qdrant_url: str = "http://localhost:6333"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Prefer explicit arguments, environment and .env over YAML defaults."""
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )
