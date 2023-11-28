import os

from sqlalchemy import Integer, String, Column, select, insert
from sqlalchemy.ext.asyncio import \
    AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import pandas as pd

from config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args = {"check_same_thread": False},
    future=True,
    echo=False,
)

async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def connect():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(255))
    name = Column(String(500))
    link = Column(String(255))
    regular_price = Column(String(255))
    promo_price = Column(String(255))
    brand = Column(String(255))

    @staticmethod
    async def add(**kwargs):
        session: AsyncSession = [i async for i in get_session()][0]
        async with session:
            query = insert(Product).values(**kwargs)
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def export():
        print('Начинаем экспорт данных')
        session: AsyncSession = [i async for i in get_session()][0]
        async with session:
            query = select(Product)
            execute = await session.execute(query)
            result = execute.unique().scalars().all()
            df = pd.DataFrame([{
                'id': row.product_id,
                'name': row.name,
                'link': row.link,
                'regular_price': row.regular_price,
                'promo_price': row.promo_price,
                'brand': row.brand
            } for row in result])
            df.to_excel(
                os.path.join(settings.BASE_DIR, 'coffee_metro.xlsx'),
                index=False
            )
