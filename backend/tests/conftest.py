"""Pytest configuration and fixtures."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import create_app
from app.models.user import User, Role
from app.models.session import Session, Window, AgentState, AttentionItem, AttentionKind


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncClient:
    """Create a test client with overridden database dependency."""
    async def override_get_db():
        yield db_session
    
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        role=Role.OPERATOR,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user."""
    user = User(
        email="admin@example.com",
        username="admin",
        role=Role.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_session(db_session: AsyncSession, test_user: User) -> Session:
    """Create a test session."""
    session = Session(name="Test Session", space="testing")
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


@pytest_asyncio.fixture
async def test_window(db_session: AsyncSession, test_session: Session) -> Window:
    """Create a test window."""
    window = Window(
        session_id=test_session.id,
        workspace=1,
        index=0,
        title="Test Window",
        agent_state=AgentState.IDLE,
    )
    db_session.add(window)
    await db_session.commit()
    await db_session.refresh(window)
    return window
