import time
from datetime import datetime
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"

def test_e2e_registro_ponto_com_sucesso(page: Page):
    page.goto(BASE_URL)

    hoje = datetime.now().strftime("%Y-%m-%d")
    page.fill("#input-data", hoje)

    matricula_unica = str(int(time.time()))
    nome_unico = f"Manoel {matricula_unica}"

    page.click("#btn-cadastrar")
    page.fill("#input-nome", nome_unico)
    page.fill("#input-matricula", matricula_unica)
    page.click("#form-cadastro button[type='submit']")

    select = page.locator("#select-funcionario")
    expect(select).to_contain_text(matricula_unica)

    page.select_option("#select-funcionario", label=f"{nome_unico} ({matricula_unica})")

    page.click("#btn-bater-ponto")

    ticket = page.locator(".ticket__tipo").first
    expect(ticket).to_be_visible()
    expect(ticket).to_have_text("ENTRADA 1")
