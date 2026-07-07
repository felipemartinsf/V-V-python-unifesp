import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import app
from backend.database import Base, get_db
from backend.schemas import FuncionarioCreate

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_integracao_fluxo_registro():
    payload = {"nome": "Marco Silva", "matricula": "12345"} 
    response_create = client.post("/funcionarios", json=payload)
    
    assert response_create.status_code == 200
    funcionario = response_create.json()
    assert funcionario["nome"] == "Marco Silva"
    assert "id" in funcionario
    
    funcionario_id = funcionario["id"]

    response_ponto = client.post(f"/funcionarios/{funcionario_id}/bater-ponto?is_feriado=false")
    assert response_ponto.status_code == 200
    marcacao = response_ponto.json()
    assert "horario" in marcacao # Baseado em MarcacaoOut

    response_espelho = client.get(f"/funcionarios/{funcionario_id}/espelho")
    assert response_espelho.status_code == 200
    espelho = response_espelho.json()
    
    assert espelho["funcionario"]["matricula"] == "12345"
    assert len(espelho["marcacoes"]) == 1
    assert espelho["is_dia_de_descanso"] is False
