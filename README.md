# FastAPI Auth

Drop in API endpoints for handling various authentication securely in FastAPI

## Features

- User registration with email verification
- Login / Logout
- Password change
- Extensible User Model
- Social media authentication

## Tech details

### Databases Supported

The following databases are supported currently:

- Postgres ( via asyncpg )
- MySQL ( via aiomysql )

The environment variable `AUTH_DATABASE_URL` dictates which database the package uses.

Examples:

- For postgres, use a connection string like: `postgresql+asyncpg://user:pass@hostname/dbname`
- For mysql, use a connection string like: `mysql+aiomysql://user:pass@hostname/dbname?charset=utf8mb4`

### Email Backends

We currently support the following email backends:

- SMTP Backend
- Console Backend
- Azure Communication Services

Note: PRs are welcome to add more email backends

#### Configuring Email Backends

- Chose the email backend using the environment variable `AUTH_EMAIL_BACKEND`, the values can be:
  - `smtp` for SMTP Backend
  - `console` for Console Backend
  - `azure` for Azure Communication Services

### Field-Level Encryption

The package includes built-in field-level encryption for sensitive data using Fernet symmetric encryption. This ensures that sensitive values like OAuth client secrets are encrypted at rest in the database.

#### Encryption Key Setup

1. Generate an encryption key:

   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

2. Add the key to your environment file (`.dev.env`, `.prod.env`, etc.):

   ```env
   ENCRYPTION_KEY=<generated_key>
   ```

#### Using EncryptedString

The `EncryptedString` TypeDecorator automatically encrypts values when writing to the database and decrypts them when reading. It's already used for `client_secret` in the `SocialProvider` model, but you can use it for any sensitive field:

```python
from models.common import EncryptedString
from sqlalchemy.orm import Mapped, mapped_column

class YourModel(Base):
    sensitive_field: Mapped[str] = mapped_column(EncryptedString, nullable=False)
```

**Important Notes:**

- Encryption/decryption happens automatically - no code changes needed in your application logic
- The same encryption key must be used consistently across all environments
- If you have existing plaintext values, you'll need a migration script to encrypt them
- Store the encryption key securely (environment variables, secret management services)

### Settings Configuration

The package uses a flexible settings system that supports both environment-based configuration and programmatic overrides.

#### Environment-Based Configuration

Settings are loaded from environment variables or `.env` files. The environment file is determined by the `ENVIRONMENT` variable (defaults to `dev`), which loads `.dev.env`, `.prod.env`, etc.

**Required Environment Variables:**

- `AUTH_DATABASE_URL` - Database connection string
- `AUTH_TIMEZONE` - Timezone (defaults to "UTC")
- `JWT_SECRET_KEY` - Secret key for JWT token signing
- `ENCRYPTION_KEY` - Fernet encryption key for field-level encryption
- `AUTH_EMAIL_BACKEND` - Email backend to use (`smtp`, `console`, or `azure`)

**Email Backend Specific Variables:**

- **SMTP**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS`, `SMTP_TIMEOUT`
- **Azure**: `AZURE_EMAIL_SERVICE_NAME`, `AZURE_EMAIL_SERVICE_ENDPOINT`, `AZURE_EMAIL_SERVICE_API_KEY`

#### Programmatic Configuration Override

For advanced use cases or testing, you can override settings programmatically using the `configure()` function:

```python
from settings import Settings, configure

# Create a custom settings object
custom_settings = Settings(
    auth_database_url="postgresql+asyncpg://user:pass@localhost/db",
    jwt_secret_key="your-secret-key",
    encryption_key="your-encryption-key",
    # ... other settings
)

# Configure the auth system to use these settings
configure(custom_settings)

# Now get_settings() will return your custom settings
from settings import get_settings
settings = get_settings()  # Returns custom_settings
```

**Use Cases for Programmatic Configuration:**

- Testing with different configurations
- Multi-tenant applications with different settings per tenant
- Dynamic configuration loading from external sources
- Overriding defaults without environment variables

**Important:** Once `configure()` is called, the global settings object takes precedence over environment variables. To revert to environment-based configuration, you would need to restart the application or clear the global state.
