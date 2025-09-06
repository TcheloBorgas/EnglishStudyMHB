from pathlib import Path
import streamlit as st

from src.ui.config import build_paths, configure_page, get_openai_api_key, WORD_LIMIT
from src.repositories.word_repository import WordRepository
from src.repositories.state_repository import StateRepository
from src.services.openai_client import OpenAIClientFactory
from src.services.generator_service import GeneratorService
from src.services.tts_service import TTSService
from src.services.grammar_check_service import GrammarCheckService
from src.use_cases.pick_word import WordPicker
from src.use_cases.check_answer import contains_target_token
from src.ui.components import (
    app_header,
    voice_selector,
    word_card,
    audio_button,
    prompt_block,
    action_buttons,
    progress_bar,
    sidebar_stats,
    render_grammar_feedback,
)

def _ensure_session_keys() -> None:
    if "current" not in st.session_state:
        st.session_state.current = {"word": None, "sentence": None, "question": None}

def _draw_new(picker: WordPicker, words: list[str], counts: dict[str, int], restricted: set[str],
              generator: GeneratorService, save_state_cb) -> None:
    word = picker.pick(words, counts, restricted)
    if not word:
        st.warning("Todas as palavras atingiram o limite. Zere o progresso para recomeçar.")
        return
    new_count = picker.update_counts(word, counts)
    if picker.should_restrict(new_count):
        restricted.add(word)
    pair = generator.generate_pair(word)
    st.session_state.current = {"word": word, "sentence": pair.sentence, "question": pair.question}
    save_state_cb(counts, list(restricted))

def render_main(project_root: Path) -> None:
    configure_page()
    app_header()

    paths = build_paths(project_root)
    paths.audio_cache.mkdir(parents=True, exist_ok=True)

    word_repo = WordRepository(paths.words_file)
    state_repo = StateRepository(paths.state_file)

    try:
        api_key = get_openai_api_key()
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    client = OpenAIClientFactory.create(api_key)
    generator = GeneratorService(client)
    tts = TTSService(api_key, paths.audio_cache)
    grammar = GrammarCheckService(client)  # <-- novo serviço
    picker = WordPicker(WORD_LIMIT)

    try:
        words = word_repo.load_words()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    counts, restricted_list = state_repo.load()
    restricted = set(restricted_list)

    _ensure_session_keys()

    voice = voice_selector(default_index=0)

    new_clicked = st.button("🎲 Sortear palavra", type="primary")
    clear_clicked = st.button("🧹 Zerar contagens & restrições")

    def save_state(c, r):
        state_repo.save(c, r)

    if clear_clicked:
        counts.clear()
        restricted.clear()
        save_state(counts, list(restricted))
        st.success("Progresso zerado.")

    if new_clicked or (st.session_state.current["word"] is None and len(restricted) < len(words)):
        _draw_new(picker, words, counts, restricted, generator, save_state)

    current = st.session_state.current

    if current["word"]:
        word_card(current["word"], current["sentence"])

        if audio_button():
            try:
                audio_path = tts.synthesize(current["sentence"], voice)
                st.audio(str(audio_path), format="audio/mp3")
            except Exception as e:
                st.error(f"Falha ao gerar TTS: {e}")

        answer = prompt_block(current["question"], f"Escreva uma frase usando ‘{current['word']}’...")
        check, nxt = action_buttons()

        if check:
            # 1) Verificação se usou a palavra
            used = contains_target_token(answer, current["word"])
            if used:
                st.success("✔ Você usou a palavra alvo.")
            else:
                st.warning(f"Tente novamente. Sua resposta deve conter **{current['word']}**.")

            # 2) Feedback gramatical (mesmo se não usou, ainda pode ver correções)
            if answer.strip():
                try:
                    feedback = grammar.check(answer, current["word"])
                    render_grammar_feedback(feedback)
                except Exception as e:
                    st.error(f"Não foi possível avaliar a gramática: {e}")

        if nxt:
            _draw_new(picker, words, counts, restricted, generator, save_state)

        progress_bar(counts.get(current["word"], 0))

    sidebar_stats(total=len(words), blocked=len(restricted), counts=counts)
