import os
import sys
from datetime import datetime, date

# permite importar calcular_ponto.py que está na raiz do projeto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Base, engine, get_db
import models
import schemas
from calcular_ponto import (
    calcular_horas_trabalhadas,
    calcular_atraso,
    calcular_horas_extras,
    calcular_adicional_noturno,
    verify_dia_descanso,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Ponto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HORARIO_ESPERADO_ENTRADA = 8  # 08:00


@app.post("/funcionarios", response_model=schemas.FuncionarioOut)
def criar_funcionario(dados: schemas.FuncionarioCreate, db: Session = Depends(get_db)):
    existente = db.query(models.Funcionario).filter_by(matricula=dados.matricula).first()
    if existente:
        raise HTTPException(400, "Matrícula já cadastrada")
    funcionario = models.Funcionario(nome=dados.nome, matricula=dados.matricula)
    db.add(funcionario)
    db.commit()
    db.refresh(funcionario)
    return funcionario


@app.get("/funcionarios", response_model=list[schemas.FuncionarioOut])
def listar_funcionarios(db: Session = Depends(get_db)):
    return db.query(models.Funcionario).all()


@app.post("/funcionarios/{funcionario_id}/bater-ponto", response_model=schemas.MarcacaoOut)
def bater_ponto(funcionario_id: int, is_feriado: bool = False, db: Session = Depends(get_db)):
    funcionario = db.query(models.Funcionario).get(funcionario_id)
    if not funcionario:
        raise HTTPException(404, "Funcionário não encontrado")

    marcacao = models.Marcacao(
        funcionario_id=funcionario_id,
        horario=datetime.now(),
        is_feriado=is_feriado,
    )
    db.add(marcacao)
    db.commit()
    db.refresh(marcacao)
    return marcacao


@app.get("/funcionarios/{funcionario_id}/espelho", response_model=schemas.EspelhoPontoOut)
def espelho_do_dia(funcionario_id: int, dia: str | None = None, db: Session = Depends(get_db)):
    """Calcula o espelho de ponto de um dia específico (padrão: hoje).
    `dia` no formato AAAA-MM-DD."""
    funcionario = db.query(models.Funcionario).get(funcionario_id)
    if not funcionario:
        raise HTTPException(404, "Funcionário não encontrado")

    data_referencia = date.fromisoformat(dia) if dia else date.today()

    marcacoes_db = (
        db.query(models.Marcacao)
        .filter(
            models.Marcacao.funcionario_id == funcionario_id,
            func.date(models.Marcacao.horario) == data_referencia,
        )
        .order_by(models.Marcacao.horario)
        .all()
    )

    horarios = [m.horario for m in marcacoes_db]
    is_feriado = any(m.is_feriado for m in marcacoes_db)
    is_descanso = verify_dia_descanso(
        datetime.combine(data_referencia, datetime.min.time()), is_feriado
    )

    resposta = {
        "funcionario": funcionario,
        "data": data_referencia.isoformat(),
        "marcacoes": horarios,
        "total_trabalhado": "00:00:00",
        "atraso": "00:00:00",
        "horas_extras": "00:00:00",
        "adicional_noturno": "00:00:00",
        "is_dia_de_descanso": is_descanso,
        "erro": None,
    }

    if not horarios:
        resposta["erro"] = "Nenhuma marcação registrada nesse dia."
        return resposta

    try:
        total = calcular_horas_trabalhadas(horarios)
        resposta["total_trabalhado"] = str(total)

        esperado_entrada = datetime.combine(data_referencia, datetime.min.time()).replace(
            hour=HORARIO_ESPERADO_ENTRADA
        )
        atraso = calcular_atraso(esperado_entrada, horarios[0])
        resposta["atraso"] = str(atraso)

        extras = calcular_horas_extras(total, is_dia_de_descanso=is_descanso)
        resposta["horas_extras"] = str(extras)

        noturno = calcular_adicional_noturno(horarios)
        resposta["adicional_noturno"] = str(noturno)

    except ValueError as e:
        resposta["erro"] = str(e)

    return resposta


# serve o frontend estático (index.html, style.css, script.js)
app.mount(
    "/",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend"), html=True),
    name="frontend",
)
