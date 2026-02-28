from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from packages.config.app_paths import ensure_runtime_paths
from packages.database.models import Base


def build_database_url() -> str:
    db_path = ensure_runtime_paths().database_path
    return f"sqlite+aiosqlite:///{db_path.as_posix()}"


@dataclass(slots=True)
class Database:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    @classmethod
    def create(cls, database_url: str | None = None) -> "Database":
        url = database_url or build_database_url()
        engine = create_async_engine(url, future=True, echo=False)
        factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        return cls(engine=engine, session_factory=factory)

    async def init_models(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self) -> None:
        await self.engine.dispose()

