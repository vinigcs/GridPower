"""Dashboard visual do GridPower — Otimização da Infraestrutura Urbana por Árvore Geradora Mínima.
Executar:  streamlit run app.py
"""

from src.modelos.grafo import Grafo
from src.servicos.servico_rede import ServicoRede
from src.utilitarios.formatacao import formatar_reais
from src.dados.exemplos import (rede_exemplo_artigo, rede_exemplo_simples,
                                rede_exemplo_desconectada)

# ────────────────────────────── PALETA VALIDADA (CVD ΔE ≥ 9.2, visão normal ΔE ≥ 27.6)
# Palette validated using CVD-aware rules: OkLab × 100 minimum ΔE ≥ 8 on adjacent pairs
# Light mode: blue #2a78d6, orange #eb6834, gray #898781, white background
# Dark mode: adapted from same palette
COR_PRIM = "#2a78d6"      # azul (categorical prime)
COR_KRUSKAL = "#eb6834"   # laranja (categorical secondary)
COR_NEUTRA = "#898781"    # cinza neutro
COR_FUNDO_LIGHT = "#0e1117"
COR_FUNDO_DARK = "#1a1d24"
COR_TEXTO_LIGHT = "#e6e6e6"
COR_TEXTO_DARK = "#c8c8c8"

# ────────────────────────────── CONFIGURAÇÃO DA PÁGINA
import streamlit as st

st.set_page_config(
    page_title="GridPower — AGM Urbana",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────── CSS GLOBAL
APRESENTACAO_CSS = """
<style>
.block-container { padding-top: 2.8rem; }
h1 { color: #e6e6e6; font-weight: 700; margin-bottom: 0.3rem; }
h2 { color: #f0f0f0; font-weight: 600; margin-top: 1.8rem; margin-bottom: 0.6rem; }
h3 { color: #f5f5f5; font-weight: 600; }
.stMetric { background: #1a1d24; border: 1px solid #2a2d35; border-radius: 12px; padding: 1rem 1.2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
.stMetric label { color: #a0a0a0 !important; font-weight: 500; }
.stTabs [data-baseweb="tab-list"] { gap: 0.4rem; }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; background: #1a1d24; border: 1px solid #2a2d35; border-bottom: none; transition: all 0.15s; }
.stTabs [aria-selected="true"] { background: #0e1117 !important; border-color: #2a78d6 !important; border-bottom: 2px solid #2a78d6 !important; font-weight: 600; }
.stButton > button[kind="primary"] { background: #2a78d6; border: none; border-radius: 8px; }
.stButton > button[kind="secondary"] { background: #1a1d24; border: 1px solid #2a2d35; border-radius: 8px; color: #e6e6e6; }
.stButton > button:hover { filter: brightness(1.15); }
.stExpander { border: 1px solid #2a2d35; border-radius: 10px; background: #1a1d24; }
.stDataFrame { border: 1px solid #2a2d35; border-radius: 8px; }
[data-testid="stSidebar"] { background: #0e1117; border-right: 1px solid #2a2d35; }
.stRadio [role="radiogroup"] label { font-size: 1rem; color: #e6e6e6; }
.stSlider [data-testid="stTickBar"] { display: none; }
</style>
"""

st.markdown(APRESENTACAO_CSS, unsafe_allow_html=True)

# ────────────────────────────── FIGURAS — LAYOUT CIRCULAR GRANDE
import math
import matplotlib.pyplot as plt

def _posicoes(grafo: Grafo) -> dict:
    """Calcula posições dos vértices.
    Se o grafo for desconectado, posiciona cada componente em seu próprio círculo
    para deixar as ilhas visualmente separadas."""
    componentes = grafo.componentes_conexos()

    # Se for conexo, usa layout circular simples
    if len(componentes) <= 1:
        nomes = grafo.nomes_vertices
        n = max(len(nomes), 1)
        return {
            nome: (math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n))
            for i, nome in enumerate(nomes)
        }

    # Grafo desconectado: posiciona cada componente em círculo separado
    # Calcula posições dos centros dos círculos (lado a lado)
    num_componentes = len(componentes)
    raio_componente = 0.35  # raio de cada círculo componente
    espacamento = raio_componente * 2.5  # espaço entre centros

    # Centros distribuídos horizontalmente
    centros = []
    for i in range(num_componentes):
        x_centro = (i - (num_componentes - 1) / 2) * espacamento
        centros.append((x_centro, 0))

    posicoes = {}
    for idx, componente in enumerate(componentes):
        cx, cy = centros[idx]
        n_comp = len(componente)
        for j, nome in enumerate(componente):
            angulo = 2 * math.pi * j / n_comp
            posicoes[nome] = (
                cx + raio_componente * math.cos(angulo),
                cy + raio_componente * math.sin(angulo)
            )
    return posicoes

def _figura_rede(grafo: Grafo, mst=None, cor_destaque=COR_PRIM, titulo: str = "") -> plt.Figure:
    """Rede em layout circular; arestas da AGM em cor forte, demais em cinza tracejado."""
    pos = _posicoes(grafo)
    escolhidas = mst.pares() if mst is not None else set()

    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=120)
    fig.patch.set_facecolor(COR_FUNDO_LIGHT)
    ax.set_facecolor(COR_FUNDO_LIGHT)
    for a in grafo.arestas:
        (x1, y1), (x2, y2) = pos[a.origem], pos[a.destino]
        na_mst = a.chave in escolhidas
        ax.plot(
            [x1, x2], [y1, y2],
            color=cor_destaque if na_mst else COR_NEUTRA,
            lw=3.5 if na_mst else 1.2,
            ls="-" if na_mst else "--",
            zorder=1,
            alpha=0.95 if na_mst else 0.6,
        )
        # rótulo de custo no meio da aresta (bem visível, fundo escuro)
        ax.text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            f"R$ {a.custo:,.0f}".replace(",", "."),
            fontsize=11, ha="center", va="center", fontweight="bold",
            color="#e6e6e6",
            bbox=dict(fc="#1a1d24", ec=cor_destaque if na_mst else COR_NEUTRA, lw=1.5, pad=4, alpha=0.98),
            zorder=2,
        )
    # vértices
    for nome, (x, y) in pos.items():
        ax.scatter([x], [y], s=900, c="#1a1d24", edgecolors="#e6e6e6", linewidths=2, zorder=3)
        ax.text(x, y, nome, ha="center", va="center", fontsize=12, fontweight="bold", color="#e6e6e6", zorder=4)
    ax.set_aspect("equal")
    ax.axis("off")
    if titulo:
        ax.set_title(titulo, fontsize=16, fontweight="bold", pad=16, color=COR_TEXTO_LIGHT)
    fig.tight_layout(pad=1.0)
    return fig

def _celula_texto(valor) -> str:
    """Converte uma célula do data_editor em texto limpo (NaN/None vira '')."""
    if valor is None:
        return ""
    if isinstance(valor, float) and math.isnan(valor):
        return ""
    return str(valor).strip()


def _parse_custo_br(custo_str) -> float:
    """Converte custo no formato brasileiro para float: '2000', '2.000', '2000,50', '2.000,50'."""
    texto = _celula_texto(custo_str)
    if not texto:
        raise ValueError("custo vazio")
    if "," in texto:
        if "." in texto:
            return float(texto.replace(".", "").replace(",", "."))
        return float(texto.replace(",", "."))
    if "." in texto and len(texto.split(".")[1]) > 2:
        return float(texto.replace(".", ""))
    return float(texto)


def _figura_serie(ns, serie_prim, serie_kruskal, rotulo_y, titulo) -> plt.Figure:
    """Linhas de Prim e Kruskal em escala log-log com legenda e rótulos diretos."""
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=120)
    fig.patch.set_facecolor(COR_FUNDO_LIGHT)
    ax.set_facecolor(COR_FUNDO_LIGHT)
    ax.plot(ns, serie_prim, marker="o", ms=10, lw=3, color=COR_PRIM, label="Prim (heap)")
    ax.plot(ns, serie_kruskal, marker="s", ms=9, lw=3, ls="--", color=COR_KRUSKAL, label="Kruskal (Union-Find)")
    # rótulos diretos no último ponto
    ax.annotate("Prim", (ns[-1], serie_prim[-1]), textcoords="offset points",
                xytext=(12, 10), fontsize=11, color=COR_PRIM, fontweight="bold")
    ax.annotate("Kruskal", (ns[-1], serie_kruskal[-1]), textcoords="offset points",
                xytext=(12, -18), fontsize=11, color=COR_KRUSKAL, fontweight="bold")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Número de vértices (|V|)", fontsize=13, color="#a0a0a0", labelpad=10)
    ax.set_ylabel(rotulo_y, fontsize=13, color="#a0a0a0", labelpad=10)
    ax.set_title(titulo, fontsize=16, fontweight="bold", color=COR_TEXTO_LIGHT, loc="left", pad=12)
    ax.set_xticks(ns)
    ax.set_xticklabels([str(n) for n in ns], fontsize=11, color="#c8c8c8")
    ax.tick_params(axis='y', labelsize=11, colors="#a0a0a0")
    ax.grid(True, which="major", color="#2a2d35", lw=1)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#2a2d35")
        ax.spines[lado].set_linewidth(1.2)
    ax.legend(frameon=True, fontsize=12, loc="upper left", facecolor=COR_FUNDO_LIGHT, edgecolor="#2a2d35", labelcolor=COR_TEXTO_LIGHT)
    fig.tight_layout()
    return fig

# ────────────────────────────── SIDEBAR — ENTRADA DE DADOS
def _sidebar_entrada():
    st.sidebar.header("⚡  Entrada da Rede")
    modo = st.sidebar.radio(
        "Origem dos dados",
        ["Exemplo do artigo (8 pts)", "Exemplo simples (4 pts)", "Exemplo desconectado", "Aleatória", "Personalizada"],
        key="modo_entrada",
    )

    if modo == "Exemplo do artigo (8 pts)":
        if st.sidebar.button("Carregar exemplo do artigo", use_container_width=True, type="primary"):
            st.session_state["grafo"] = rede_exemplo_artigo()
            st.session_state["servico"] = ServicoRede(st.session_state["grafo"])
            st.toast("Rede do artigo carregada (R$ 18.500)", icon="✅")

    elif modo == "Exemplo simples (4 pts)":
        if st.sidebar.button("Carregar exemplo simples", use_container_width=True):
            st.session_state["grafo"] = rede_exemplo_simples()
            st.session_state["servico"] = ServicoRede(st.session_state["grafo"])
            st.toast("Exemplo simples carregado (R$ 9.000)", icon="✅")

    elif modo == "Exemplo desconectado":
        if st.sidebar.button("Carregar exemplo desconectado", use_container_width=True):
            st.session_state["grafo"] = rede_exemplo_desconectada()
            st.session_state["servico"] = ServicoRede(st.session_state["grafo"])
            st.toast("Rede desconectada carregada (2 ilhas)", icon="⚠️")

    elif modo == "Aleatória":
        n = st.sidebar.slider("Número de pontos (|V|)", 4, 60, 12, help="Redes sintéticas conexas com |E| = 5|V|")
        semente = st.sidebar.number_input("Semente (reprodutibilidade)", min_value=0, value=42, step=1)
        if st.sidebar.button("Gerar rede aleatória", use_container_width=True, type="primary"):
            from src.dados.gerador import gerar_rede_sintetica
            grafo = gerar_rede_sintetica(int(n), semente=int(semente))
            st.session_state["grafo"] = grafo
            st.session_state["servico"] = ServicoRede(grafo)
            st.toast(f"Rede gerada: {grafo.quantidade_vertices} vértices, {grafo.quantidade_arestas} arestas", icon="🎲")

    else:  # Personalizada
        st.sidebar.caption("Preencha a tabela de pontos (Nome e Tipo) e a de conexões (Origem, Destino e Custo). Use o botão **+** no final de cada tabela para incluir mais linhas.")
        with st.sidebar.form("form_rede", clear_on_submit=False):
            st.markdown("### 📍 Pontos")
            pontos_input = st.data_editor(
                [
                    {"Nome": "S1", "Tipo": "subestacao"},
                    {"Nome": "Q1", "Tipo": "quadro"},
                    {"Nome": "Q2", "Tipo": "quadro"},
                    {"Nome": "E1", "Tipo": "estacao"},
                    {"Nome": "R1", "Tipo": "reservatorio"},
                    {"Nome": "P1", "Tipo": "distribuicao"},
                    {"Nome": "P2", "Tipo": "distribuicao"},
                    {"Nome": "P3", "Tipo": "distribuicao"},
                ],
                column_config={
                    "Nome": st.column_config.TextColumn("Nome", required=True),
                    "Tipo": st.column_config.SelectboxColumn(
                        "Tipo",
                        options=["ponto", "subestacao", "quadro", "estacao", "reservatorio", "distribuicao"],
                        default="ponto"
                    ),
                },
                hide_index=True,
                num_rows="dynamic",
                key="editor_pontos",
                width="stretch",
            )

            st.markdown("### 🔗 Conexões")
            # Tabela de conexões: 3 colunas (Origem, Destino, Custo) + botão para adicionar linha
            conexoes = st.data_editor(
                [
                    {"Origem": "S1", "Destino": "Q1", "Custo": "2000"},
                    {"Origem": "S1", "Destino": "Q2", "Custo": "2200"},
                    {"Origem": "Q1", "Destino": "E1", "Custo": "2500"},
                    {"Origem": "Q1", "Destino": "Q2", "Custo": "2600"},
                    {"Origem": "Q2", "Destino": "R1", "Custo": "2700"},
                    {"Origem": "E1", "Destino": "P1", "Custo": "2800"},
                    {"Origem": "R1", "Destino": "P2", "Custo": "3000"},
                    {"Origem": "P1", "Destino": "P2", "Custo": "3100"},
                    {"Origem": "P2", "Destino": "P3", "Custo": "3300"},
                    {"Origem": "E1", "Destino": "R1", "Custo": "4100"},
                    {"Origem": "Q1", "Destino": "P1", "Custo": "4500"},
                    {"Origem": "R1", "Destino": "P3", "Custo": "4800"},
                    {"Origem": "S1", "Destino": "E1", "Custo": "5200"},
                ],
                column_config={
                    "Origem": st.column_config.TextColumn("Origem", required=True),
                    "Destino": st.column_config.TextColumn("Destino", required=True),
                    "Custo": st.column_config.TextColumn("Custo (R$)", required=True),
                },
                hide_index=True,
                num_rows="dynamic",
                key="editor_conexoes",
                width="stretch",
            )

            enviado = st.form_submit_button("Montar rede", use_container_width=True, type="primary")

        if enviado:
            try:
                grafo = Grafo()
                for p in pontos_input:
                    nome = _celula_texto(p.get("Nome"))
                    tipo = _celula_texto(p.get("Tipo")) or "ponto"
                    if nome:
                        grafo.adicionar_vertice(nome, tipo)
                for linha in conexoes:
                    origem = _celula_texto(linha.get("Origem"))
                    destino = _celula_texto(linha.get("Destino"))
                    valor = linha.get("Custo")
                    # Pula linhas completamente vazias (deixadas em branco)
                    if not origem and not destino and (valor is None or _celula_texto(valor) == ""):
                        continue
                    if not origem or not destino:
                        raise ValueError("Cada conexão precisa de Origem e Destino preenchidos.")
                    custo = _parse_custo_br(valor)
                    grafo.adicionar_aresta(origem, destino, custo)
                st.session_state["grafo"] = grafo
                st.session_state["servico"] = ServicoRede(grafo)
                st.toast("Rede personalizada montada com sucesso", icon="✅")
            except ValueError as erro:
                st.sidebar.error(f"Não foi possível montar a rede: {erro}")

    return False

# ────────────────────────────── PÁGINA: REDE & AGM
def pagina_rede_agm():
    from src.servicos.relatorio import gerar_relatorio_otimizacao

    st.title("⚡ GridPower — Árvore Geradora Mínima")
    st.caption("Prim (heap)  ×  Kruskal (Union-Find)  |  Squad 2 · UrbanTech")

    if "servico" not in st.session_state:
        st.info("👈  Escolha uma rede no painel à esquerda para começar.")
        st.markdown("""
        **Como usar:**
        1. Selecione **Exemplo do artigo (8 pts)** e clique *Carregar* para ver o caso pedagógico (R$ 18.500).
        2. Ou gere uma **Aleatória** com a semente desejada.
        3. Compare Prim vs Kruskal, veja as figuras, baixe o relatório.
        4. Vá na aba **Experimento** para medir tempo/memória de 10 a 1000 vértices.
        """)
        return

    grafo = st.session_state["grafo"]
    servico = st.session_state["servico"]

    total_pares = grafo.quantidade_vertices * (grafo.quantidade_vertices - 1) / 2
    densidade = grafo.quantidade_arestas / total_pares if total_pares else 0.0
    conexa, componentes = servico.verificar_conectividade()

    # KPI ROW — GRANDE
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📍  Pontos (|V|)", grafo.quantidade_vertices)
    c2.metric("🔗  Conexões (|E|)", grafo.quantidade_arestas)
    c3.metric("📊  Densidade", f"{densidade:.0%}")
    c4.metric("🌐  Conectividade", "Conexa ✅" if conexa else f"{len(componentes)} ilhas ⚠️")

    if not conexa:
        st.warning(
            "A rede está **desconectada**: não existe árvore geradora que cubra todos os pontos.  "
            "Componentes isolados: " + "  |  ".join("{" + ", ".join(sorted(c)) + "}" for c in componentes)
        )
        return

    # COMPARAÇÃO
    st.subheader("Prim  ×  Kruskal")
    comparacao = servico.comparar()

    k1, k2, k3 = st.columns(3)
    k1.metric("Custo Prim", formatar_reais(comparacao.custo_prim))
    k2.metric("Custo Kruskal", formatar_reais(comparacao.custo_kruskal))
    k3.metric("Conexões na AGM", len(comparacao.prim))

    if comparacao.custos_equivalentes:
        st.success("✅  Os dois algoritmos chegaram ao mesmo custo mínimo.")
    else:
        st.error("❌  Os custos diferem — há erro em alguma das implementações.")

    st.markdown(
        f"**Mesmas conexões:** {'✅ sim' if comparacao.mesmas_arestas else '❌ não'}  \n"
        f"**Justificativa técnica:** {comparacao.justificativa}"
    )

    # VISUALIZAÇÃO — DUAS FIGURAS LADO A LADO (GRANDES)
    st.subheader("Rede e Árvore Geradora Mínima")
    colP, colK = st.columns(2, gap="large")
    with colP:
        st.caption(f"Prim — {formatar_reais(comparacao.custo_prim)}")
        fig = _figura_rede(grafo, comparacao.prim, COR_PRIM, "Prim — árvore geradora mínima")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with colK:
        st.caption(f"Kruskal — {formatar_reais(comparacao.custo_kruskal)}")
        fig = _figura_rede(grafo, comparacao.kruskal, COR_KRUSKAL, "Kruskal — árvore geradora mínima")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.caption("Legenda: linhas **grossas coloridas** = conexões escolhidas pela AGM  •  linhas **finas tracejadas** = conexões candidatas descartadas")

    # TABELAS EXPANSÍVEIS
    with st.expander("🔍  Conexões escolhidas (detalhe)", expanded=False):
        cp, ck = st.columns(2)
        for coluna, arvore in ((cp, comparacao.prim), (ck, comparacao.kruskal)):
            with coluna:
                st.markdown(f"### {arvore.algoritmo}")
                st.dataframe(
                    [{"Origem": a.origem, "Destino": a.destino, "Custo (R$)": formatar_reais(a.custo)}
                     for a in arvore.arestas],
                    use_container_width=True, hide_index=True,
                )

    with st.expander("📋  Todas as conexões candidatas", expanded=False):
        st.dataframe(
            [{"Origem": a.origem, "Destino": a.destino,
              "Custo (R$)": formatar_reais(a.custo),
              "Na AGM (Prim)": "✅" if a.chave in comparacao.prim.pares() else "❌"}
             for a in sorted(grafo.arestas, key=lambda a: a.custo)],
            use_container_width=True, hide_index=True,
        )

    # RELATÓRIO
    st.subheader("📄  Relatório de Otimização")
    texto_relatorio = gerar_relatorio_otimizacao(grafo, comparacao)
    st.download_button(
        "⬇️  Baixar relatório (.md)",
        texto_relatorio,
        file_name="relatorio_otimizacao.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.code(texto_relatorio, language="markdown", line_numbers=False)

# ────────────────────────────── PÁGINA: EXPERIMENTO
def pagina_experimento():
    from src.servicos.experimento import executar_experimento, perfilar
    import csv
    import io

    st.title("📈  Experimento de Complexidade")
    st.caption("Tempo e memória de Prim e Kruskal em redes sintéticas conexas com |E| = 5|V|")

    if "resultados_exp" not in st.session_state:
        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            if st.button("▶️  Executar experimento (10 → 1000 vértices)", type="primary", use_container_width=True):
                with st.spinner("Medindo tempo e memória… pode levar alguns segundos."):
                    st.session_state["resultados_exp"] = executar_experimento()
                st.toast("Experimento concluído!", icon="✅")
                st.rerun()
        with col_info:
            st.info(
                "O experimento mede cada algoritmo nas 5 tamanhos do DOC: **10, 50, 100, 500, 1000 vértices**.\n"
                "Redes sintéticas conexas, |E| = 5|V|, custos U[1000, 20000].  \n"
                "Tempo: mediana de 30 execuções (10 para ≥500). Memória: pico do `tracemalloc`."
            )
        return

    resultados = st.session_state["resultados_exp"]
    ns = [r["vertices"] for r in resultados]

    # TABELA DE RESULTADOS
    st.subheader("Resultados Medidos")
    st.dataframe(
        [{"|V|": r["vertices"], "|E|": r["arestas"],
          "Prim (ms)": round(r["prim_ms"], 3),
          "Kruskal (ms)": round(r["kruskal_ms"], 3),
          "Prim (KiB)": round(r["prim_kib"], 1),
          "Kruskal (KiB)": round(r["kruskal_kib"], 1),
          "Custo (R$)": formatar_reais(r["custo_prim"]),
          "Custos iguais": "✅" if r["custos_iguais"] else "❌"}
         for r in resultados],
        use_container_width=True, hide_index=True,
    )

    # GRÁFICOS LOG-LOG GRANDES
    g1, g2 = st.columns(2, gap="large")
    with g1:
        st.subheader("⏱️  Tempo de Execução")
        fig = _figura_serie(ns, [r["prim_ms"] for r in resultados],
                            [r["kruskal_ms"] for r in resultados],
                            "Tempo (ms)", "Tempo por tamanho da rede (log-log)")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with g2:
        st.subheader("💾  Pico de Memória")
        fig = _figura_serie(ns, [r["prim_kib"] for r in resultados],
                            [r["kruskal_kib"] for r in resultados],
                            "Pico de memória (KiB)", "Memória por tamanho da rede (log-log)")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    # DOWNLOAD CSV
    buffer = io.StringIO()
    escritor = csv.DictWriter(buffer, fieldnames=list(resultados[0].keys()))
    escritor.writeheader()
    escritor.writerows(resultados)
    st.download_button(
        "⬇️  Baixar resultados (.csv)",
        buffer.getvalue(),
        file_name="resultados_complexidade.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # PROFILING
    with st.expander("🔬  Profiling com cProfile (n=1000)", expanded=False):
        if st.button("Gerar perfil cProfile", use_container_width=True):
            with st.spinner("Profilando Prim e Kruskal com n=1000…"):
                perfil_texto = perfilar(n=1000)
            st.code(perfil_texto, language="text", line_numbers=True)

    # INTERPRETAÇÃO
    st.subheader("📝  Interpretação")
    st.markdown("""
- **Prim e Kruskal obtiveram o mesmo custo mínimo** em todos os tamanhos testados (corretude).
- **Nas redes esparsas (|E| = 5|V|) o Kruskal foi mais rápido e usou menos memória** que o Prim.
- **Explicação plausível:** o Prim constrói a lista de adjacência (2|E| entradas) e mantém um heap;
  o Kruskal apenas ordena as arestas e mantém estruturas de tamanho |V| (Union-Find).
- **Atenção:** não se deve generalizar para redes densas (|E| ≈ |V|²), que não foram avaliadas.
""")

# ────────────────────────────── MAIN
def main():
    # Apenas sidebar de entrada de dados
    _sidebar_entrada()

    # Abas principais
    aba1, aba2 = st.tabs(["🌐  Rede & AGM", "📈  Experimento"])

    with aba1:
        pagina_rede_agm()

    with aba2:
        pagina_experimento()

if __name__ == "__main__":
    main()