"""
Testes de integração da API FastAPI.

Usam SQLite em memória no lugar do PostgreSQL só para não depender de um
banco real rodando durante o `pytest` — a lógica de negócio (calcular_ponto)
já é testada separadamente em test_ponto.py / tests_boundary.py / test_mcdc_coberture.py.
"""
import os
import sys
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import Base, get_db  # noqa: E402
import app as app_module  # noqa: E402

engine_teste = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
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


def test_cria_funcionario():
    resp = client.post("/funcionarios", json={"nome": "Ana Silva", "matricula": "001"})
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Ana Silva"


def test_nao_permite_matricula_duplicada():
    client.post("/funcionarios", json={"nome": "Ana Silva", "matricula": "001"})
    resp = client.post("/funcionarios", json={"nome": "Outra Pessoa", "matricula": "001"})
    assert resp.status_code == 400


def test_bater_ponto_e_ver_espelho():
    funcionario = client.post("/funcionarios", json={"nome": "João", "matricula": "002"}).json()

    client.post(f"/funcionarios/{funcionario['id']}/bater-ponto")
    resp = client.get(f"/funcionarios/{funcionario['id']}/espelho")

    assert resp.status_code == 200
    dados = resp.json()
    assert len(dados["marcacoes"]) == 1
    # número ímpar de marcações -> erro esperado (regra de negócio)
    assert dados["erro"] == "Número ímpar de marcações"


def test_espelho_sem_marcacoes():
    funcionario = client.post("/funcionarios", json={"nome": "Maria", "matricula": "003"}).json()
    resp = client.get(f"/funcionarios/{funcionario['id']}/espelho?dia=2020-01-01")
    dados = resp.json()
    assert dados["marcacoes"] == []
    assert "Nenhuma marcação" in dados["erro"]


def test_funcionario_inexistente_da_404():
    resp = client.get("/funcionarios/9999/espelho")
    assert resp.status_code == 404
