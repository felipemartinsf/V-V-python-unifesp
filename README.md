# Sistema de Ponto — Trabalho de V&V

Sistema simples de registro de ponto usado como base para praticar técnicas
de teste de software (TDD, MC/DC, Análise de Valor Limite / Boundary Testing).

## Stack

- **Backend/API**: FastAPI
- **Frontend**: HTML + CSS + JavaScript puro
- **Banco**: PostgreSQL
- **Testes**: pytest

## Estrutura

```
calcular_ponto.py     # regra de negócio pura (sem dependências externas)
main.py               # CLI original (console) — mantida e testada
backend/
  app.py              # aplicação FastAPI (endpoints da API)
  database.py         # conexão com PostgreSQL (SQLAlchemy)
  models.py           # modelos ORM (Funcionario, Marcacao)
  schemas.py          # schemas Pydantic
frontend/
  index.html
  style.css
  script.js
sql/
  schema.sql          # DDL de referência das tabelas
tests/
  test_ponto.py         # testes unitários da regra de negócio
  tests_boundary.py      # Boundary Value Analysis
  test_mcdc_coberture.py # MC/DC (verify_dia_descanso)
  test_api.py             # testes de integração da API (SQLite em memória)
```

## Setup

1. Crie e ative um ambiente virtual, depois instale as dependências:

   ```bash
   pip install -r requirements.txt
   # ou, se preferir uv (já usado no projeto):
   uv pip install -r requirements.txt
   ```

2. Crie o banco PostgreSQL:

   ```bash
   createdb sistema_ponto
   # ou dentro do psql: CREATE DATABASE sistema_ponto;
   ```

3. (Opcional) ajuste a string de conexão via variável de ambiente, se seu
   Postgres não usar as credenciais padrão (`postgres:postgres@localhost:5432`):

   ```bash
   export DATABASE_URL="postgresql://usuario:senha@localhost:5432/sistema_ponto"
   ```

4. Suba a API (ela cria as tabelas automaticamente no primeiro start e também
   serve o frontend):

   ```bash
   cd backend
   uvicorn app:app --reload
   ```

5. Acesse **http://localhost:8000** no navegador para usar o sistema.
   A documentação interativa da API fica em **http://localhost:8000/docs**.

## Rodando os testes

```bash
pytest -v
```

Isso executa:
- `test_ponto.py` — testes unitários gerais da regra de negócio (bom
  candidato para desenvolvimento em **TDD**: escreva o teste, veja falhar,
  implemente).
- `tests_boundary.py` — **Boundary Value Analysis**: valores exatamente no
  limite da tolerância de atraso e da janela de adicional noturno (ex.: 10min
  exatos vs. 10min+1s; 22:00 exato vs. 22:00:01).
- `test_mcdc_coberture.py` — **MC/DC** em `verify_dia_descanso(data, is_feriado)`,
  que tem duas condições (A = é domingo, B = é feriado) combinadas com `or`.
  Os 3 testes cobrem as combinações necessárias para MC/DC de uma expressão
  `A or B`.
- `test_api.py` — testes de integração da API, usando SQLite em memória (não
  precisa de um Postgres real rodando para os testes passarem).

## Observações sobre a regra de negócio (decisões tomadas)

- Tolerância de atraso na entrada: **10 minutos** (acima disso conta o atraso
  cheio, sem descontar a tolerância).
- Carga diária padrão: **8 horas**.
- Adicional noturno: janela **22:00–05:00**, com limites exclusivos (bater
  ponto exatamente às 22:00 ainda não conta; 22:00:01 já conta).
- Dia de descanso (domingo ou feriado): **todo** tempo trabalhado conta como
  hora extra.

## Nota sobre um ajuste feito no teste original

Em `test_ponto.py`, o teste `test_trabalho_em_dia_de_folga` chamava
`calcular_horas_extras(horas, carga_diaria)` passando dois `timedelta` — mas
não há como saber que o dia era domingo a partir só de dois `timedelta` (não
tem nenhuma data ali). Ajustei a chamada para
`calcular_horas_extras(horas, carga_diaria, is_dia_de_descanso=True)`, deixando
explícito o que o teste já pressupunha implicitamente. Também corrigi o
`main.py`, que importava de `calculador_ponto` (nome de arquivo inexistente)
em vez de `calcular_ponto`.
