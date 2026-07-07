import time
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"

def test_erro_bater_ponto_sem_funcionario(page: Page):
    page.route("**/funcionarios", lambda route: route.fulfill(json=[]))
    page.goto(BASE_URL)
    
    expect(page.locator("#espelho-conteudo")).to_have_text("Cadastre um funcionário para começar.", timeout=5000)

    mensagens_alerta = []
    
    page.on("dialog", lambda dialog: (mensagens_alerta.append(dialog.message), dialog.dismiss()))

    page.evaluate("document.getElementById('btn-bater-ponto').click()")
    
    page.wait_for_timeout(1000)

    assert "Cadastre e selecione um funcionário primeiro." in mensagens_alerta


def test_erro_cadastro_matricula_duplicada(page: Page):
    page.goto(BASE_URL)
    matricula = f"dup_{int(time.time())}"

    page.click("#btn-cadastrar")
    page.fill("#input-nome", "Usuário 1")
    page.fill("#input-matricula", matricula)
    page.click("#form-cadastro button[type='submit']")

    expect(page.locator("#select-funcionario")).to_contain_text(matricula, timeout=5000)

    page.click("#btn-cadastrar")
    page.fill("#input-nome", "Usuário 2")
    page.fill("#input-matricula", matricula)

    mensagens_alerta = []
    page.on("dialog", lambda dialog: (mensagens_alerta.append(dialog.message), dialog.dismiss()))

    page.evaluate("document.querySelector('#form-cadastro button[type=submit]').click()")
    page.wait_for_timeout(1000)

    assert "Matrícula já cadastrada" in mensagens_alerta
