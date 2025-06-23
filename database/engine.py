from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool, NullPool, QueuePool
from contextlib import asynccontextmanager
from asyncio import sleep
from sqlalchemy.exc import OperationalError

db_url = 'sqlite+aiosqlite:///sqlite.db'

Base = declarative_base()

engine = create_async_engine(
    db_url,
    future=True,
    echo=False,
    poolclass=NullPool,
    connect_args={
        'check_same_thread': False,
        'timeout': 30
    }
)

async def create_base():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def get_session(max_attempts=3, retry_delay=0.1):
    attempt = 0
    while True:
        try:
            async with sessionmaker(
                engine,
                class_=AsyncSession,
                autoflush=True,
                expire_on_commit=False
            )() as session:
                yield session
                return
        except OperationalError as e:
            if "database is locked" in str(e) and attempt < max_attempts:
                attempt += 1
                await sleep(retry_delay * attempt)
                continue
            await session.rollback()
            raise
        except Exception:   
            await session.rollback()
            raise
        finally:
            try:
                await session.close()
            except:
                pass
