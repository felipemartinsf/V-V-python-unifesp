import os
import sys
from datetime import datetime
from sqlalchemy.pool import StaticPool

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import Base, get_db 
import app as app_module 
from models import Marcacao

engine_teste = create_engine(
    "sqlite:///:memory:", 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
SessionTeste = sessionmaker(bind=engine_teste)

def _override_get_db():
    db = SessionTeste()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def banco_limpo():
    Base.metadata.create_all(bind=engine_teste)
    app_module.app.dependency_overrides[get_db] = _override_get_db
    yield
    Base.metadata.drop_all(bind=engine_teste)

client = TestClient(app_module.app)

def test_integracao_calculo_persistido():
    response_func = client.post("/funcionarios", json={"nome": "Carlos Teste", "matricula": "888"})
    assert response_func.status_code == 200
    funcionario_id = response_func.json()["id"]

    db = SessionTeste()
    
    try:
        marcacao_entrada = Marcacao(
            funcionario_id=funcionario_id,
            horario=datetime(2023, 10, 25, 8, 15, 0), 
            is_feriado=False
        )
        marcacao_saida = Marcacao(
            funcionario_id=funcionario_id,
            horario=datetime(2023, 10, 25, 17, 0, 0), 
            is_feriado=False
        )
        
        db.add_all([marcacao_entrada, marcacao_saida])
        db.commit()
    finally:
        db.close()

    response_espelho = client.get(f"/funcionarios/{funcionario_id}/espelho?dia=2023-10-25")
    
    assert response_espelho.status_code == 200
    espelho = response_espelho.json()

    assert len(espelho["marcacoes"]) == 2
    
    assert espelho["atraso"] != "0:00:00" 
    
    assert espelho["is_dia_de_descanso"] is False
