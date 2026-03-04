"""Application configuration module.

Provides centralized settings for the CodeEcoScan service using
pydantic-settings for environment-variable–based overrides.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application-level configuration.

    All fields can be overridden via environment variables with the
    ``CODEECOSCAN_`` prefix (e.g. ``CODEECOSCAN_DEBUG=true``).

    Attributes:
        APP_NAME: Display name of the service.
        APP_VERSION: Semantic version string.
        DEBUG: Enable debug-level logging and verbose error messages.
        HEAVY_IMPORT_MODULES: Frozen set of module names considered
            energy-heavy for detection purposes.
    """

    APP_NAME: str = "CodeEcoScan"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    HEAVY_IMPORT_MODULES: frozenset[str] = frozenset(
        {"tensorflow", "torch", "sklearn", "keras", "pandas"}
    )

    model_config = {"env_prefix": "CODEECOSCAN_"}


def get_settings() -> Settings:
    """Return a ``Settings`` instance.

    This factory function exists so that FastAPI ``Depends()`` can inject
    settings without relying on a module-level singleton.
    """
    return Settings()
