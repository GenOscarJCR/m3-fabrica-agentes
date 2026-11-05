"""Configuración de la base de datos SQLite para la aplicación de empleados."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATOS_DIR = os.path.join(os.path.dirname(__file__), "datos")
os.makedirs(DATOS_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATOS_DIR, 'empleados.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
