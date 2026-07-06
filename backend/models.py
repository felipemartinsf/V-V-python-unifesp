from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Funcionario(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    matricula = Column(String(30), unique=True, nullable=False, index=True)

    marcacoes = relationship(
        "Marcacao", back_populates="funcionario", cascade="all, delete-orphan"
    )


class Marcacao(Base):
    __tablename__ = "marcacoes"

    id = Column(Integer, primary_key=True, index=True)
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=False)
    horario = Column(DateTime, nullable=False, default=datetime.now)
    is_feriado = Column(Boolean, default=False)

    funcionario = relationship("Funcionario", back_populates="marcacoes")
