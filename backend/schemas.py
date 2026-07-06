from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class FuncionarioCreate(BaseModel):
    nome: str
    matricula: str


class FuncionarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    matricula: str


class MarcacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    horario: datetime
    is_feriado: bool


class EspelhoPontoOut(BaseModel):
    funcionario: FuncionarioOut
    data: str
    marcacoes: list[datetime]
    total_trabalhado: str
    atraso: str
    horas_extras: str
    adicional_noturno: str
    is_dia_de_descanso: bool
    erro: Optional[str] = None
