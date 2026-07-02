import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Configuração da página
st.set_page_config(
    page_title="Avaliador Heurístico H10",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    div.stButton > button {
        background: #f8fafc;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 0.45rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: none;
    }
    div.stButton > button:hover {
        background: #eef2ff;
        border-color: #bfdbfe;
        color: #0f172a;
    }
    div.stButton > button:focus {
        outline: none;
        box-shadow: 0 0 0 0.2rem rgba(37, 99, 235, 0.15);
    }
    button[kind="primary"] {
        background: linear-gradient(180deg, #16a34a 0%, #15803d 100%) !important;
        color: #ffffff !important;
        border-color: #166534 !important;
        box-shadow: 0 4px 10px rgba(22, 163, 74, 0.18) !important;
    }
    button[kind="secondary"] {
        background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border-color: #1e40af !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.18) !important;
    }
    button[kind="tertiary"] {
        background: linear-gradient(180deg, #e2e8f0 0%, #cbd5e1 100%) !important;
        color: #0f172a !important;
        border-color: #94a3b8 !important;
        box-shadow: none !important;
    }
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(180deg, #0f766e 0%, #0b5d5a 100%) !important;
        color: #ffffff !important;
        border: 1px solid #0d5c58 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Lista com as 10 heurísticas
HEURISTICS = [
    {
        "id": 1,
        "shortName": "Status Visível",
        "fullName": "Visibilidade do Status do Sistema",
        "description": "O sistema mantém os usuários informados sobre o que está acontecendo, com feedback adequado em tempo razoável.",
        "question": "O site fornece feedback claro sobre as ações do usuário — como estados de carregamento, confirmações de formulário e indicadores de progresso?",
        "weight": 1.2,
    },
    {
        "id": 2,
        "shortName": "Linguagem Natural",
        "fullName": "Correspondência com o Mundo Real",
        "description": "O sistema usa palavras, frases e conceitos familiares ao usuário, em vez de jargões orientados ao sistema.",
        "question": "O vocabulário, ícones e metáforas utilizados são familiares e intuitivos para o público-alvo da interface?",
        "weight": 1.0,
    },
    {
        "id": 3,
        "shortName": "Controle do Usuário",
        "fullName": "Controle e Liberdade do Usuário",
        "description": "Usuários frequentemente escolhem funções por engano e precisam de saídas de emergência claramente sinalizadas.",
        "question": "O usuário pode desfazer ações, voltar a estados anteriores e cancelar processos sem consequências indesejadas?",
        "weight": 1.1,
    },
    {
        "id": 4,
        "shortName": "Consistência",
        "fullName": "Consistência e Padrões",
        "description": "Os usuários não devem ter que se perguntar se palavras, situações ou ações diferentes significam a mesma coisa.",
        "question": "O design mantém padrões visuais, textuais e comportamentais consistentes ao longo de toda a interface?",
        "weight": 1.0,
    },
    {
        "id": 5,
        "shortName": "Prevenção de erros",
        "fullName": "Prevenção de erros",
        "description": "Melhor que boas mensagens de erro é um design cuidadoso que previne problemas antes que ocorram.",
        "question": "O sistema implementa validações, confirmações e restrições que evitam ativamente que o usuário cometa erros?",
        "weight": 1.3,
    },
    {
        "id": 6,
        "shortName": "Reconhecimento",
        "fullName": "Reconhecimento em vez de Memorização",
        "description": "Minimize a carga de memória tornando objetos, ações e opções visíveis ao longo da jornada do usuário.",
        "question": "As opções, ações e informações relevantes estão sempre visíveis sem exigir que o usuário memorize etapas anteriores?",
        "weight": 1.1,
    },
    {
        "id": 7,
        "shortName": "Eficiência de Uso",
        "fullName": "Flexibilidade e Eficiência de Uso",
        "description": "Aceleradores permitem que usuários experientes realizem ações mais rapidamente do que iniciantes.",
        "question": "O sistema oferece atalhos, personalização e fluxos alternativos que aumentam a eficiência de usuários recorrentes?",
        "weight": 0.9,
    },
    {
        "id": 8,
        "shortName": "Minimalismo",
        "fullName": "Design Estético e Minimalista",
        "description": "Interfaces não devem conter informação irrelevante — cada elemento extra compete com informações relevantes.",
        "question": "A interface elimina elementos desnecessários e prioriza apenas o que é essencial para a conclusão de cada tarefa?",
        "weight": 1.0,
    },
    {
        "id": 9,
        "shortName": "Recuperação de Erros",
        "fullName": "Reconhecer e Recuperar de Erros",
        "description": "Mensagens de erro devem ser em linguagem simples, indicar o problema com precisão e sugerir uma solução.",
        "question": "As mensagens de erro são claras, não técnicas e orientam o usuário sobre como resolver o problema encontrado?",
        "weight": 1.2,
    },
    {
        "id": 10,
        "shortName": "Documentação",
        "fullName": "Ajuda e Documentação",
        "description": "Mesmo que seja melhor o sistema dispensar documentação, pode ser necessário fornecer ajuda e suporte contextual.",
        "question": "O sistema oferece ajuda contextual, tutoriais ou documentação acessível quando o usuário precisa de suporte?",
        "weight": 0.8,
    },
]

ANSWER_OPTIONS = [
    {"value": 0, "label": "Discordo totalmente", "sublabel": "Não implementado ou muito mal feito"},
    {"value": 1, "label": "Discordo", "sublabel": "Pouco implementado"},
    {"value": 2, "label": "Às vezes", "sublabel": "Parcialmente implementado"},
    {"value": 3, "label": "Concordo", "sublabel": "Bem implementado com pequenas melhorias possíveis"},
    {"value": 4, "label": "Concordo totalmente", "sublabel": "Implementado perfeitamente"},
]


def get_answer_label(value):
    for option in ANSWER_OPTIONS:
        if option["value"] == value:
            return option["label"]
    return "—"


def calculate_score(answers):
    weighted_sum = 0
    max_weighted_sum = 0
    by_heuristic = {}

    for h in HEURISTICS:
        value = answers.get(h["id"], 0)
        weighted_sum += value * h["weight"]
        max_weighted_sum += 4 * h["weight"]
        by_heuristic[h["id"]] = round((value / 4) * 100)

    if max_weighted_sum == 0:
        total = 0
    else:
        total = round((weighted_sum / max_weighted_sum) * 100)

    return total, by_heuristic


def get_classification(score):
    if score >= 85:
        return {
            "label": "Excelente",
            "color": "#059669",
            "bg": "#ECFDF5",
            "border": "#A7F3D0",
            "description": "Interface exemplar com altíssima usabilidade.",
        }
    if score >= 70:
        return {
            "label": "Bom",
            "color": "#2563EB",
            "bg": "#EFF6FF",
            "border": "#BFDBFE",
            "description": "Boa usabilidade com oportunidades pontuais de melhoria.",
        }
    if score >= 55:
        return {
            "label": "Regular",
            "color": "#D97706",
            "bg": "#FFFBEB",
            "border": "#FDE68A",
            "description": "Usabilidade aceitável, mas com problemas que merecem atenção.",
        }
    if score >= 40:
        return {
            "label": "Deficiente",
            "color": "#EA580C",
            "bg": "#FFF7ED",
            "border": "#FED7AA",
            "description": "Problemas relevantes afetam a experiência do usuário.",
        }
    return {
        "label": "Crítico",
        "color": "#DC2626",
        "bg": "#FEF2F2",
        "border": "#FECACA",
        "description": "Problemas graves de usabilidade comprometendo o sistema.",
    }


def normalize_url(raw_url):
    text = raw_url.strip()
    if not text:
        return ""
    if not text.startswith(("http://", "https://")):
        text = f"https://{text}"
    return text


def generate_pdf_report(url, answers, total, by_heuristic):
    """Gera o relatório de avaliação heurística em formato PDF e retorna os bytes do arquivo."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title="Relatório de Avaliação Heurística H10",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleCustom",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=14,
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#334155"),
        leading=15,
    )
    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=8,
    )
    sub_heading_style = ParagraphStyle(
        "SubHeadingCustom",
        parent=styles["Heading3"],
        fontSize=11,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6,
    )

    cls = get_classification(total)
    elements = []

    elements.append(Paragraph("Relatório de Avaliação Heurística", title_style))
    elements.append(Paragraph("Baseado nas 10 Heurísticas de Nielsen", subtitle_style))

    elements.append(Paragraph(f"<b>Site avaliado:</b> {url}", body_style))
    elements.append(Paragraph(f"<b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}", body_style))
    elements.append(
        Paragraph(
            f"<b>Pontuação geral:</b> {total}/100 — "
            f"<font color='{cls['color']}'><b>{cls['label']}</b></font>",
            body_style,
        )
    )
    elements.append(Paragraph(cls["description"], body_style))

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(HRFlowable(width="100%", color=colors.HexColor("#cbd5e1"), thickness=1))

    elements.append(Paragraph("Análise por Heurística", heading_style))

    table_data = [["ID", "Heurística", "Pontuação", "Resposta", "Peso"]]
    for h in HEURISTICS:
        score = by_heuristic[h["id"]]
        value = answers.get(h["id"], 0)
        label = get_answer_label(value)
        table_data.append(
            [
                f"H{h['id']:02d}",
                h["fullName"],
                f"{score}%",
                f"{label} ({value}/4)",
                f"×{h['weight']}",
            ]
        )

    table = Table(table_data, colWidths=[1.6 * cm, 6.3 * cm, 2.2 * cm, 4.6 * cm, 1.8 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))

    strengths = sorted(HEURISTICS, key=lambda h: by_heuristic[h["id"]], reverse=True)[:3]
    priorities = sorted(HEURISTICS, key=lambda h: by_heuristic[h["id"]])[:3]

    elements.append(Paragraph("Pontos Fortes", sub_heading_style))
    for h in strengths:
        elements.append(
            Paragraph(f"✓ {h['fullName']} — {by_heuristic[h['id']]}%", body_style)
        )

    elements.append(Paragraph("Áreas Prioritárias", sub_heading_style))
    for h in priorities:
        elements.append(
            Paragraph(f"! {h['fullName']} — {by_heuristic[h['id']]}%", body_style)
        )

    elements.append(Spacer(1, 1 * cm))
    elements.append(HRFlowable(width="100%", color=colors.HexColor("#cbd5e1"), thickness=1))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(
        Paragraph(
            "Gerado por Avaliador Heurístico H10",
            ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#94a3b8")),
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def reset_state():
    st.session_state.view = "home"
    st.session_state.url = ""
    st.session_state.current = 0
    st.session_state.answers = {}


if "view" not in st.session_state:
    st.session_state.view = "home"
if "url" not in st.session_state:
    st.session_state.url = ""
if "current" not in st.session_state:
    st.session_state.current = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}


# ─── HOME PAGE ───────────────────────────────────────────────────────────────
if st.session_state.view == "home":
    st.markdown(
        """
        <style>
        .block-container { padding-top: 0; }
        .hero-box {
            background: linear-gradient(90deg, #eef4ff 0%, #f8fafc 50%, #eefbf6 100%);
            border: 1px solid #dbe7ff;
            border-radius: 18px;
            padding: 36px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        }
        .card-mini {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 18px;
            text-align: center;
            box-shadow: inset 0 -1px 0 rgba(15, 23, 42, 0.04);
        }
        .heuristic-card {
            background: linear-gradient(90deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 10px;
        }
        .info-panel {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-box">
            <div style='display:flex; flex-wrap:wrap; align-items:center; gap:24px;'>
                <div style='flex:1.2; min-width:300px;'>
                    <div style='font-size:12px; font-weight:700; color:#2563eb; letter-spacing:1px;'>10 HEURÍSTICAS · NIELSEN</div>
                    <h1 style='font-size:48px; margin: 12px 0; color:#0f172a;'><span style='font-style:normal; color:#2563eb;'>NEXUS ANALYZER SCORE</span></h1>
                    <p style='font-size:16px; color:#475569; line-height:1.6;'>Um instrumento de avaliação heurística baseado nas 10 heurísticas de Jakob Nielsen, com pontuação ponderada de critérios.</p>
                </div>
                <div style='flex:1; min-width:280px;'>
                    <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px;'>
                        <div class='card-mini'><div style='font-size:32px; font-weight:700; color:#2563eb;'>10</div><div style='font-size:12px; color:#64748b;'>Heurísticas avaliadas</div></div>
                        <div class='card-mini'><div style='font-size:32px; font-weight:700; color:#2563eb;'>5</div><div style='font-size:12px; color:#64748b;'>Níveis de classificação</div></div>
                        <div class='card-mini'><div style='font-size:32px; font-weight:700; color:#2563eb;'>×1.3</div><div style='font-size:12px; color:#64748b;'>Pesos máximos</div></div>
                        <div class='card-mini'><div style='font-size:32px; font-weight:700; color:#2563eb;'>100</div><div style='font-size:12px; color:#64748b;'>Score máximo</div></div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("\n")
    if st.button("Iniciar avaliação", key="btn_iniciar_home", use_container_width=True, type="secondary"):
        st.session_state.view = "url"
        st.rerun()

    st.markdown("\n")
    st.subheader("As 10 heurísticas avaliadas")

    for h in HEURISTICS:
        st.markdown(
            f"<div class='heuristic-card'>"
            f"<div style='font-size:13px; font-weight:700; color:#0f172a;'>H{h['id']} · {h['fullName']}</div>"
            f"<div style='font-size:12px; color:#64748b; margin-top:6px;'>{h['description']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("\n")
    st.markdown(
        """
        <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px;'>
            <div class='info-panel'><div style='font-weight:700; margin-bottom:6px; color:#0f172a;'>Lei de Fitts</div><div style='font-size:13px; color:#64748b;'>Influência na acessibilidade e localização de elementos.</div></div>
            <div class='info-panel'><div style='font-weight:700; margin-bottom:6px; color:#0f172a;'>Lei de Hick</div><div style='font-size:13px; color:#64748b;'>Ajuda a medir a complexidade de escolha nas interfaces.</div></div>
            <div class='info-panel'><div style='font-weight:700; margin-bottom:6px; color:#0f172a;'>AVALIAÇÃO NEXUS</div><div style='font-size:13px; color:#64748b;'>O resultado final combina peso e avaliação de cada critério.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── URL PAGE ─────────────────────────────────────────────────────────────────
elif st.session_state.view == "url":
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px'><div style='width:32px;height:32px;border-radius:8px;background:#0F172A;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700'>H10</div><span style='font-size:14px;font-weight:600'>Avaliador Heurístico</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.title("Qual site será avaliado?")
    st.write("Informe a URL da interface que você deseja avaliar pelas heurísticas de Nielsen.")

    url_input = st.text_input(
        "URL do site",
        value=st.session_state.url,
        placeholder="exemplo.com.br",
        key="url_input",
    )

    if st.button("Avançar para perguntas", type="secondary"):
        normalized = normalize_url(url_input)
        if normalized:
            st.session_state.url = normalized
            st.session_state.answers = {}
            st.session_state.current = 0
            st.session_state.view = "assessment"
            st.rerun()
        else:
            st.warning("Informe uma URL válida para continuar.")

    st.info("Dica: mantenha o site aberto em outra aba para consultar a interface em tempo real.")

# ─── ASSESSMENT PAGE ──────────────────────────────────────────────────────────
elif st.session_state.view == "assessment":
    st.markdown(
        "<div style='display:flex;justify-content:space-between;align-items:center'><div style='display:flex;align-items:center;gap:10px'><div style='width:32px;height:32px;border-radius:8px;background:#0F172A;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700'>H10</div><span style='font-size:14px;font-weight:600'>Avaliador Heurístico</span></div><span style='color:#64748B'>"
        f"{len(st.session_state.answers)} / {len(HEURISTICS)} Respondidas"
        "</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    progress = len(st.session_state.answers) / len(HEURISTICS)
    st.progress(progress)

    # Botões de atalho superiores
    step_cols = st.columns(len(HEURISTICS))
    for i, h in enumerate(HEURISTICS):
        with step_cols[i]:
            if st.button(f"H{h['id']}", key=f"step_{h['id']}", use_container_width=True):
                st.session_state.current = i
                st.rerun()
            
            if i == st.session_state.current:
                st.markdown("<div style='height:6px;background:#0F172A;border-radius:999px'></div>", unsafe_allow_html=True)
            elif h["id"] in st.session_state.answers:
                st.markdown("<div style='height:6px;background:#22C55E;border-radius:999px'></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='height:6px;background:#CBD5E1;border-radius:999px'></div>", unsafe_allow_html=True)

    current_heuristic = HEURISTICS[st.session_state.current]

    st.caption(f"Avaliando item {st.session_state.current + 1} de {len(HEURISTICS)}")
    st.markdown(f"<h3 style='color:#0f172a; margin-top:0;'>{current_heuristic['fullName']}</h3>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:#1e293b; font-size:15px; line-height:1.6;'>{current_heuristic['description']}</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div style='background:#eef2ff; border:1px solid #c7d2fe; border-left:4px solid #2563eb; "
        f"border-radius:8px; padding:14px 16px; margin:10px 0 16px 0;'>"
        f"<span style='color:#0f172a; font-size:16px; font-weight:700;'>👉 {current_heuristic['question']}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Renderização de botões de opção de resposta
    current_saved_value = st.session_state.answers.get(current_heuristic["id"], None)

    for option in ANSWER_OPTIONS:
        is_selected = (current_saved_value == option["value"])
        btn_type = "primary" if is_selected else "tertiary"
        
        if st.button(
            f"{option['label']} — {option['sublabel']}",
            key=f"opt_{current_heuristic['id']}_{option['value']}",
            use_container_width=True,
            type=btn_type
        ):
            st.session_state.answers[current_heuristic["id"]] = option["value"]
            st.rerun()

    st.write("\n")
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button("Voltar Anterior", type="tertiary") and st.session_state.current > 0:
            st.session_state.current -= 1
            st.rerun()
            
    with col_next:
        if st.session_state.current < len(HEURISTICS) - 1:
            if st.button("Próxima Pergunta", type="secondary"):
                if current_heuristic["id"] not in st.session_state.answers:
                    st.warning("Por favor, selecione uma das opções acima antes de avançar.")
                else:
                    st.session_state.current += 1
                    st.rerun()
        else:
            if st.button("Finalizar e Ver Resultados", type="secondary"):
                if len(st.session_state.answers) < len(HEURISTICS):
                    st.error("Você precisa responder todas as 10 heurísticas antes de ver o resultado global.")
                else:
                    st.session_state.view = "results"
                    st.rerun()

# ─── RESULTADO PAGINA ─────────────────────────────────────────────────────────────
elif st.session_state.view == "results":
    total, by_heuristic = calculate_score(st.session_state.answers)
    cls = get_classification(total)

    st.title("Resultados da Avaliação Heurística")
    st.markdown(f"**URL analisada:** `{st.session_state.url}`")

    score_col, text_col = st.columns([1, 2])
    with score_col:
        st.markdown(
            f"<div style='border:1px solid {cls['border']};background:{cls['bg']};padding:24px;border-radius:16px;text-align:center'>"
            f"<div style='font-size:14px;color:{cls['color']};font-weight:600;margin-bottom:6px'>SCORE FINAL</div>"
            f"<div style='font-size:54px;font-weight:800;color:{cls['color']}'>{total}%</div>"
            f"<div style='font-size:13px;color:#64748b;margin-top:4px'>Média ponderada por impacto</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with text_col:
        st.markdown("### Avaliação")
        st.markdown(
            f"<div style='padding:16px;border-left:4px solid {cls['border']};background:{cls['bg']};border-radius:8px'>"
            f"<strong style='color:{cls['color']};font-size:18px;'>Nível {cls['label']}</strong><br>"
            f"<p style='margin-top:6px;color:#334155;'>{cls['description']}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Mapeamento de pontos fortes e fracos ordenados estritamente por pontuação
    sorted_heuristics = sorted(HEURISTICS, key=lambda h: by_heuristic[h["id"]], reverse=True)
    strengths = sorted_heuristics[:3]
    priorities = sorted(HEURISTICS, key=lambda h: by_heuristic[h["id"]])[:3]

    c1, c2 = st.columns(2)
    with c1:
        st.success("🏆 Maiores Pontos Fortes")
        for h in strengths:
            st.markdown(f"**{h['shortName']}:** `{by_heuristic[h['id']]}%` de conformidade.")

    with c2:
        st.warning("⚠️ Áreas Prioritárias de Ajuste")
        for h in priorities:
            st.markdown(f"**{h['shortName']}:** `{by_heuristic[h['id']]}%` — Requer atenção imediata.")

    st.markdown("---")

    # Configuração do gráfico radar (Plotly)
    radar_categories = [h["shortName"] for h in HEURISTICS]
    radar_scores = [by_heuristic[h["id"]] for h in HEURISTICS]
    
    # Fechamento do polígono geométrico do radar
    radar_categories.append(radar_categories[0])
    radar_scores.append(radar_scores[0])

    radar = go.Figure()
    radar.add_trace(
        go.Scatterpolar(
            r=radar_scores,
            theta=radar_categories,
            fill="toself",
            line_color="#2563EB",
            fillcolor="rgba(37, 99, 235, 0.15)",
        )
    )
    radar.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 100]}},
        showlegend=False,
        title="Mapeamento das 10 Heurísticas (Visão Geral)",
    )
    st.plotly_chart(radar, use_container_width=True)

    st.markdown("---")
    st.subheader("Análise detalhada por critério")
    
    for h in HEURISTICS:
        score = by_heuristic[h["id"]]
        value = st.session_state.answers.get(h["id"], 0)
        label = get_answer_label(value)

        st.markdown(f"**H{h['id']} · {h['fullName']}**")
        st.progress(score / 100)
        st.caption(f"Status avaliado: **{label}** · (Peso Multiplicador: ×{h['weight']}) · Grau de Conformidade: {score}%")
        st.markdown("<br>", unsafe_allow_html=True)

    # Geração e exportação do relatório em PDF
    report_pdf = generate_pdf_report(st.session_state.url, st.session_state.answers, total, by_heuristic)

    st.download_button(
        label="📄 Baixar Relatório em PDF",
        data=report_pdf,
        file_name=f"relatorio_heuristico_h10_{datetime.now().strftime('%Y-%m-%d')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Iniciar Nova Avaliação Completa", type="tertiary", use_container_width=True):
        reset_state()
        st.rerun()
