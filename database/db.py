import traceback

from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from settings import Settings, get_settings
from utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseSession:
    def __init__(self, config: Settings, fail_silently: bool = False):
        self.config = config
        self.fail_silently = fail_silently
        self.engine = create_async_engine(config.auth_database_url, echo=False)
        self.SessionLocal = async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_session(self):
        try:
            async with self.SessionLocal() as session:
                yield session
        except Exception as e:
            logger.error(f"Failed to get database session: {e}")
            logger.error(traceback.format_exc())
            if not self.fail_silently:
                raise e


def get_session(settings: Settings = Depends(get_settings)) -> AsyncSession:
    return DatabaseSession(settings).get_session()
