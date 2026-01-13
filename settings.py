import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic_extra_types.timezone_name import TimeZoneName
from pydantic_settings import BaseSettings, SettingsConfigDict

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
BASE_DIR = Path(__file__).parent

# Global state to hold the configured env file path
_env_file_path: Optional[Path] = None


def get_env_file_path() -> Path:
    """
    Get the environment file path with the following priority:
    1. Programmatic override (via set_env_file_path())
    2. AUTH_ENV_FILE environment variable
    3. ENVIRONMENT-based path (.{ENVIRONMENT}.env)
    4. Default (.dev.env)

    If the file doesn't exist, it will be created automatically.

    Returns:
        Path to the environment file
    """
    global _env_file_path

    # Priority 1: Programmatic override
    if _env_file_path is not None:
        env_file = _env_file_path
    # Priority 2: AUTH_ENV_FILE environment variable
    elif os.getenv("AUTH_ENV_FILE"):
        env_file = Path(os.getenv("AUTH_ENV_FILE"))
    # Priority 3: ENVIRONMENT-based path
    else:
        env_file = BASE_DIR / f".{ENVIRONMENT}.env"

    # Resolve relative paths to absolute
    if not env_file.is_absolute():
        env_file = BASE_DIR / env_file

    # Auto-create env file if it doesn't exist
    if not env_file.exists():
        env_file.parent.mkdir(parents=True, exist_ok=True)
        env_file.write_text(
            f"# Environment configuration file for {ENVIRONMENT} environment\n"
            "# Add your configuration variables here\n"
            "# This file was auto-generated\n"
        )

    return env_file


def set_env_file_path(path: Union[str, Path]) -> None:
    """
    Set a custom environment file path programmatically.
    This takes precedence over environment variables.

    Args:
        path: Path to the environment file (can be absolute or relative to BASE_DIR)
    """
    global _env_file_path
    _env_file_path = Path(path)
    # Clear the cache so get_settings() picks up the new path
    get_settings.cache_clear()


class Settings(BaseSettings):
    # Basic Settings
    auth_database_url: str
    auth_timezone: TimeZoneName = "UTC"
    project_name: str = "fastapi-auth"

    # JWT Settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30  # 30 minutes
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 30  # 30 days
    jwt_audience: str = "fastapi-auth"

    # Encryption Settings
    encryption_key: str  # Fernet encryption key for field-level encryption

    # Configuring email backends
    email_backend: Union[Literal["smtp"], Literal["azure"], Literal["console"]] = "smtp"

    # Configure the template directory to use, we will have default as well
    templates_dir: str = os.path.join(Path(__file__).parent, "templates")

    # SMTP Settings ( only required if email_backend is "smtp" )
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from: str
    smtp_use_tls: bool = True
    smtp_timeout: int = 10

    # Azure Email Settings ( only required if email_backend is "azure" )
    azure_email_service_name: str
    azure_email_service_endpoint: str
    azure_email_service_api_key: str

    # Custom Model Settings (optional - use default models if not specified)
    custom_user_model: Optional[str] = (
        None  # Import path for custom User model (e.g., "myapp.models.CustomUser")
    )
    custom_user_profile_model: Optional[str] = (
        None  # Import path for custom UserProfile model
    )

    # Auth settings for password, emails etc
    passwordless_login_enabled: bool = False
    email_verification_required: bool = False


# Set initial model_config - will be updated dynamically in get_settings()
Settings.model_config = SettingsConfigDict(
    env_file=get_env_file_path(), env_file_encoding="utf-8"
)


# Global state to hold the configured settings
_settings: Optional[Settings] = None


def configure(settings: Settings) -> None:
    """
    Globally configure the auth system with a specific settings object.
    This is the entrypoint for "Plug and Play" dynamic configuration.
    """
    global _settings
    _settings = settings
    # Clear the cache so the next call picks up the new global
    get_settings.cache_clear()


@lru_cache
def get_settings() -> Settings:
    """
    Get the current settings.
    If `configure()` was called, returns that object.
    Otherwise, loads from environment variables (defaults).
    """
    if _settings is not None:
        return _settings
    # Update model_config with current env_file path before instantiation
    Settings.model_config = SettingsConfigDict(
        env_file=get_env_file_path(), env_file_encoding="utf-8"
    )
    return Settings()
