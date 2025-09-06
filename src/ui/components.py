import streamlit as st
from typing import Dict
from src.ui.config import APP_TITLE, SUPPORTED_VOICES, WORD_LIMIT
from src.domain.models import GrammarFeedback

def app_header() -> str:
    st.title(APP_TITLE)
    st.caption("Pratique vocabulário com frases, áudio e perguntas em inglês.")
    return "header"

def voice_selector(default_index: int = 0) -> str:
    return st.selectbox("Voz (TTS)", SUPPORTED_VOICES, index=default_index)

def word_card(word: str, sentence: str) -> None:
    st.subheader(f"Palavra: **{word}**")
    st.write(f"Exemplo: _{sentence}_")

def audio_button() -> bool:
    return st.button("🔊 Ouvir a frase")

def prompt_block(question: str, placeholder: str) -> str:
    st.markdown("---")
    st.write("**Pergunta** (responda usando a palavra alvo):")
    st.info(question)
    return st.text_area("Sua resposta (digite em inglês):", key="answer", height=120, placeholder=placeholder)

def action_buttons() -> tuple[bool, bool]:
    col1, col2 = st.columns([1, 2])
    with col1:
        check = st.button("Verificar resposta ✅")
    with col2:
        nxt = st.button("Próxima palavra ➡️")
    return check, nxt

def progress_bar(count_value: int) -> None:
    st.progress(min(count_value, WORD_LIMIT) / WORD_LIMIT,
                text=f"Progresso dessa palavra: {count_value}/{WORD_LIMIT} (após {WORD_LIMIT}, é bloqueada)")

def sidebar_stats(total: int, blocked: int, counts: Dict[str, int]) -> None:
    with st.sidebar:
        st.header("📊 Progresso")
        st.write(f"Palavras totais: **{total}**")
        st.write(f"Bloqueadas ({WORD_LIMIT}+): **{blocked}**")
        st.write(f"Restantes: **{total - blocked}**")
        if st.checkbox("Ver 10 contagens aleatórias"):
            import random
            sample = random.sample(list(counts.items()), k=min(10, len(counts)))
            st.write({k: v for k, v in sample})

def render_grammar_feedback(feedback: GrammarFeedback) -> None:
    """
    Mostra o feedback de gramática de forma compacta e útil.
    """
    st.markdown("---")
    st.subheader("📝 Feedback de gramática")
    colA, colB = st.columns([3, 1])
    with colA:
        if feedback.ok:
            st.success("Boa! Sua frase está aceitável para A2–B1.")
        else:
            st.warning("Sua frase pode melhorar.")
    with colB:
        st.metric("Score", f"{feedback.score:.1f}/5")

    if feedback.issues:
        st.write("**Pontos de melhoria:**")
        for it in feedback.issues[:5]:
            st.write(f"- {it}")

    if feedback.corrected:
        st.write("**Sugestão corrigida:**")
        st.info(feedback.corrected)
