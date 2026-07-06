const API = ""; // mesma origem (backend serve o frontend)

const relogioEl = document.getElementById("relogio");
const selectFuncionario = document.getElementById("select-funcionario");
const btnBaterPonto = document.getElementById("btn-bater-ponto");
const btnCadastrar = document.getElementById("btn-cadastrar");
const checkFeriado = document.getElementById("check-feriado");
const inputData = document.getElementById("input-data");
const espelhoConteudo = document.getElementById("espelho-conteudo");
const tplMarcacao = document.getElementById("tpl-marcacao");

const dialogCadastro = document.getElementById("dialog-cadastro");
const formCadastro = document.getElementById("form-cadastro");
const btnCancelar = document.getElementById("btn-cancelar");

function atualizarRelogio() {
  relogioEl.textContent = new Date().toLocaleTimeString("pt-BR");
}
setInterval(atualizarRelogio, 1000);
atualizarRelogio();

inputData.value = new Date().toISOString().slice(0, 10);

async function carregarFuncionarios() {
  const resp = await fetch(`${API}/funcionarios`);
  const funcionarios = await resp.json();
  selectFuncionario.innerHTML = funcionarios
    .map((f) => `<option value="${f.id}">${f.nome} (${f.matricula})</option>`)
    .join("");
  if (funcionarios.length) carregarEspelho();
  else espelhoConteudo.textContent = "Cadastre um funcionário para começar.";
}

function formatarDuracao(strHhMmSs) {
  // vem no formato "H:MM:SS" (str do timedelta) -> "HHh MMm"
  const partes = strHhMmSs.split(":");
  const h = parseInt(partes[0], 10);
  const m = parseInt(partes[1], 10);
  return `${h}h ${String(m).padStart(2, "0")}m`;
}

async function carregarEspelho() {
  const funcionarioId = selectFuncionario.value;
  if (!funcionarioId) return;

  const dia = inputData.value;
  const resp = await fetch(`${API}/funcionarios/${funcionarioId}/espelho?dia=${dia}`);

  if (!resp.ok) {
    espelhoConteudo.innerHTML = `<div class="espelho__vazio">Erro ao carregar espelho.</div>`;
    return;
  }

  const dados = await resp.json();
  renderizarEspelho(dados);
}

function renderizarEspelho(dados) {
  espelhoConteudo.innerHTML = "";

  if (!dados.marcacoes.length) {
    espelhoConteudo.innerHTML = `<div class="espelho__vazio">${dados.erro || "Sem marcações nesse dia."}</div>`;
    return;
  }

  dados.marcacoes.forEach((horario, i) => {
    const clone = tplMarcacao.content.cloneNode(true);
    const tipo = i % 2 === 0 ? "ENTRADA" : "SAÍDA";
    clone.querySelector(".ticket__tipo").textContent = `${tipo} ${Math.floor(i / 2) + 1}`;
    clone.querySelector(".ticket__hora").textContent = new Date(horario).toLocaleTimeString("pt-BR");
    espelhoConteudo.appendChild(clone);
  });

  if (dados.erro) {
    const aviso = document.createElement("div");
    aviso.className = "espelho__vazio";
    aviso.textContent = dados.erro;
    espelhoConteudo.appendChild(aviso);
    return;
  }

  const resumo = document.createElement("div");
  resumo.className = "resumo";
  resumo.innerHTML = `
    <div class="resumo__item">
      <div class="resumo__label">Total trabalhado</div>
      <div class="resumo__valor">${formatarDuracao(dados.total_trabalhado)}</div>
    </div>
    <div class="resumo__item">
      <div class="resumo__label">Atraso</div>
      <div class="resumo__valor ${dados.atraso !== "0:00:00" ? "resumo__valor--alerta" : "resumo__valor--ok"}">${formatarDuracao(dados.atraso)}</div>
    </div>
    <div class="resumo__item">
      <div class="resumo__label">Horas extras</div>
      <div class="resumo__valor resumo__valor--destaque">${formatarDuracao(dados.horas_extras)}</div>
    </div>
    <div class="resumo__item">
      <div class="resumo__label">Adicional noturno</div>
      <div class="resumo__valor resumo__valor--destaque">${formatarDuracao(dados.adicional_noturno)}</div>
    </div>
  `;
  espelhoConteudo.appendChild(resumo);

  if (dados.is_dia_de_descanso) {
    const tag = document.createElement("div");
    tag.className = "tag-descanso";
    tag.textContent = "★ DIA DE DESCANSO — tudo trabalhado conta como extra";
    espelhoConteudo.appendChild(tag);
  }
}

btnBaterPonto.addEventListener("click", async () => {
  const funcionarioId = selectFuncionario.value;
  if (!funcionarioId) return alert("Cadastre e selecione um funcionário primeiro.");

  const isFeriado = checkFeriado.checked;
  await fetch(`${API}/funcionarios/${funcionarioId}/bater-ponto?is_feriado=${isFeriado}`, {
    method: "POST",
  });
  carregarEspelho();
});

selectFuncionario.addEventListener("change", carregarEspelho);
inputData.addEventListener("change", carregarEspelho);

btnCadastrar.addEventListener("click", () => dialogCadastro.showModal());
btnCancelar.addEventListener("click", () => dialogCadastro.close());

formCadastro.addEventListener("submit", async (e) => {
  e.preventDefault();
  const nome = document.getElementById("input-nome").value;
  const matricula = document.getElementById("input-matricula").value;

  const resp = await fetch(`${API}/funcionarios`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, matricula }),
  });

  if (!resp.ok) {
    const erro = await resp.json();
    alert(erro.detail || "Erro ao cadastrar.");
    return;
  }

  dialogCadastro.close();
  formCadastro.reset();
  await carregarFuncionarios();
});

carregarFuncionarios();
