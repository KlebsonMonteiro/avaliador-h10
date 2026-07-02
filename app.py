import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF  # Certifique-se de adicionar 'fpdf2' no seu files requirements.txt

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
            "rgb": (5, 150, 105),
            "bg": "#ECFDF5",
            "border": "#A7F3D0",
            "description": "Interface exemplar com altíssima usabilidade.",
        }
    if score >= 70:
        return {
            "label": "Bom",
            "color": "#2563EB",
            "rgb": (37, 99, 235),
            "bg": "#EFF6FF",
            "border": "#BFDBFE",
            "description": "Boa usabilidade com oportunidades pontuais de melhoria.",
        }
    if score >= 55:
        return {
            "label": "Regular",
            "color": "#D97706",
            "rgb": (217, 119, 6),
            "bg": "#FFFBEB",
            "border": "#FDE68A",
            "description": "Usabilidade aceitável, mas com problemas que merecem atenção.",
        }
    if score >= 40:
        return {
            "label": "Deficiente",
            "color": "#EA580C",
            "rgb": (234, 88, 12),
            "bg": "#FFF7ED",
            "border": "#FED7AA",
            "description": "Problemas relevantes afetam a experiência do usuário.",
        }
    return {
        "label": "Crítico",
        "color": "#DC2626",
        "rgb": (220, 38, 38),
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


class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 10)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, "NEXUS ANALYZER SCORE — RELATÓRIO TÉCNICO", 0, 1, "L")
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")


def generate_pdf_report(url, answers, total, by_heuristic):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    cls = get_classification(total)
    strengths = sorted(HEURISTICS, key=lambda h: by_heuristic[h["id"]], reverse=True)[:3]
    priorities = sorted(HEURISTICS, key=lambda h: by_heuristic[h["id"]])[:3]

    # Título Principal
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, "Relatório de Avaliação Heurística", 0, 1, "L")
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 6, f"Site Avaliado: {url}", 0, 1, "L")
    pdf.cell(0, 6, f"Data da Avaliação: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", 0, 1, "L")
    pdf.ln(6)

    # Painel de Score Geral (Destacado)
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(10, pdf.get_y(), 190, 24, "F")
    
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(71, 85, 105)
    pdf.set_xy(15, pdf.get_y() + 3)
    pdf.cell(40, 6, "PONTUAÇÃO GERAL:", 0, 0, "L")
    
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(*cls["rgb"])
    pdf.cell(30, 6, f"{total} / 100", 0, 0, "L")
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, f"Nível: {cls['label']}", 0, 1, "L")
    
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.set_x(15)
    pdf.cell(0, 6, cls["description"], 0, 1, "L")
    pdf.ln(10)

    # Destaques: Pontos Fortes e Ajustes
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "Resumo Estratégico", 0, 1, "L")
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(5, 150, 105)
    pdf.cell(95, 6, "Maiores Pontos Fortes:", 0, 0, "L")
    pdf.set_text_color(217, 119, 6)
    pdf.cell(95, 6, "Áreas Prioritárias de Ajuste:", 0, 1, "L")
    
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(51, 65, 85)
    for i in range(3):
        h_s = strengths[i]
        h_p = priorities[i]
        pdf.cell(95, 5, f"- {h_s['shortName']} ({by_heuristic[h_s['id']]}%)", 0, 0, "L")
        pdf.cell(95, 5, f"- {h_p['shortName']} ({by_heuristic[h_p['id']]}%)", 0, 1, "L")
    
    pdf.ln(8)

    # Tabela Detalhada por Critério
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "Análise Detalhada por Critério", 0, 1, "L")
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(15, 23, 42)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(15, 7, "ID", 1, 0, "C", True)
    pdf.cell(85, 7, "Heurística", 1, 0, "L", True)
    pdf.cell(40, 7, "Resposta", 1, 0, "C", True)
    pdf.cell(20, 7, "Peso", 1, 0, "C", True)
    pdf.cell(30, 7, "Conformidade", 1, 1, "C", True)

    # Linhas da Tabela
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(51, 65, 85)
    
    for h in HEURISTICS:
        score = by_heuristic[h["id"]]
        val = answers.get(h["id"], 0)
        lbl = get_answer_label(val)
        
        # Zebra striping simples intercalando cores de fundo
        bg_toggle = pdf.page_no() % 2 == 0
        pdf.set_fill_color(248, 250, 252) if
