import json
import random
import streamlit as st


CHO = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

JUNG = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
    "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"
]

JONG = [
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
    "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

SPLIT_MAP = {
    "ㄲ": ["ㄱ", "ㄱ"],
    "ㄸ": ["ㄷ", "ㄷ"],
    "ㅃ": ["ㅂ", "ㅂ"],
    "ㅆ": ["ㅅ", "ㅅ"],
    "ㅉ": ["ㅈ", "ㅈ"],

    "ㄳ": ["ㄱ", "ㅅ"],
    "ㄵ": ["ㄴ", "ㅈ"],
    "ㄶ": ["ㄴ", "ㅎ"],
    "ㄺ": ["ㄹ", "ㄱ"],
    "ㄻ": ["ㄹ", "ㅁ"],
    "ㄼ": ["ㄹ", "ㅂ"],
    "ㄽ": ["ㄹ", "ㅅ"],
    "ㄾ": ["ㄹ", "ㅌ"],
    "ㄿ": ["ㄹ", "ㅍ"],
    "ㅀ": ["ㄹ", "ㅎ"],
    "ㅄ": ["ㅂ", "ㅅ"],

    "ㅘ": ["ㅗ", "ㅏ"],
    "ㅙ": ["ㅗ", "ㅏ", "ㅣ"],
    "ㅚ": ["ㅗ", "ㅣ"],
    "ㅝ": ["ㅜ", "ㅓ"],
    "ㅞ": ["ㅜ", "ㅓ", "ㅣ"],
    "ㅟ": ["ㅜ", "ㅣ"],
    "ㅢ": ["ㅡ", "ㅣ"],
    "ㅐ": ["ㅏ", "ㅣ"],
    "ㅒ": ["ㅑ", "ㅣ"],
    "ㅔ": ["ㅓ", "ㅣ"],
    "ㅖ": ["ㅕ", "ㅣ"],
}


def expand_jamo(j):
    return SPLIT_MAP.get(j, [j])


def decompose_word(word):
    result = []

    for ch in word:
        code = ord(ch)

        if not (ord("가") <= code <= ord("힣")):
            return None

        s_index = code - ord("가")

        cho_index = s_index // (21 * 28)
        jung_index = (s_index % (21 * 28)) // 28
        jong_index = s_index % 28

        cho = CHO[cho_index]
        jung = JUNG[jung_index]
        jong = JONG[jong_index]

        result.extend(expand_jamo(cho))
        result.extend(expand_jamo(jung))

        if jong:
            result.extend(expand_jamo(jong))

    return result


def judge(answer_jamo, guess_jamo):
    result = ["없음"] * 5
    remaining = {}

    for i in range(5):
        if guess_jamo[i] == answer_jamo[i]:
            result[i] = "정위치"
        else:
            remaining[answer_jamo[i]] = remaining.get(answer_jamo[i], 0) + 1

    for i in range(5):
        if result[i] == "정위치":
            continue

        if remaining.get(guess_jamo[i], 0) > 0:
            result[i] = "위치다름"
            remaining[guess_jamo[i]] -= 1
        else:
            result[i] = "없음"

    return result


@st.cache_data
def load_words():
    with open("game_words_5jamo.json", "r", encoding="utf-8") as f:
        return json.load(f)


def render_row(jamo, result):
    color_map = {
        "정위치": "#4CAF50",
        "위치다름": "#FFC107",
        "없음": "#9E9E9E"
    }

    cells = ""

    for i in range(5):
        color = color_map[result[i]]
        cells += f"""
        <div class="jamo-cell" style="background-color: {color};">
            {jamo[i]}
        </div>
        """

    st.markdown(
        f"""
        <div class="jamo-row">
            {cells}
        </div>
        """,
        unsafe_allow_html=True
    )


def start_new_game(words):
    answer_item = random.choice(words)

    st.session_state.answer_item = answer_item
    st.session_state.answer_word = answer_item["word"]
    st.session_state.answer_jamo = answer_item["jamo"]
    st.session_state.history = []
    st.session_state.game_over = False
    st.session_state.message = ""


def main():
    st.set_page_config(
        page_title="한글 자모 퀴즈!",
        page_icon="🎯",
        layout="centered"
    )

    st.title("한글 자모 퀴즈")
    st.markdown(
    """
    <style>
    .jamo-row {
        display: flex;
        flex-direction: row;
        flex-wrap: nowrap;
        gap: 8px;
        margin-bottom: 14px;
        width: 100%;
        overflow-x: auto;
    }

    .jamo-cell {
        width: 56px;
        height: 56px;
        min-width: 56px;
        border-radius: 8px;
        color: white;
        font-size: 28px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
    }

    @media (max-width: 480px) {
        .jamo-row {
            gap: 6px;
        }

        .jamo-cell {
            width: 48px;
            height: 48px;
            min-width: 48px;
            font-size: 24px;
            border-radius: 7px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)
    st.write("표준국어대사전 단어를 자모 5칸으로 맞히는 게임입니다. 표준 국어 대사전 데이터를 기반으로 합니다.")

    words = load_words()
    allowed_words = {item["word"]: item for item in words}

    max_try = 5

    if "answer_word" not in st.session_state:
        start_new_game(words)

    with st.expander("규칙 보기"):
        st.write("정답은 자모 분해 결과가 정확히 5칸인 단어입니다.")
        st.write("쌍자음, 겹받침, 복합모음은 기본 자모 단위로 분해합니다.")
        st.write("초록색: 위치까지 맞음")
        st.write("노란색: 정답에 있지만 위치가 다름")
        st.write("회색: 정답에 없음")

    st.write(f"남은 횟수: {max_try - len(st.session_state.history)} / {max_try}")

    with st.form("guess_form", clear_on_submit=True):
        guess_word = st.text_input(
            "단어 입력",
            disabled=st.session_state.game_over
        )

        submit = st.form_submit_button(
            "입력",
            disabled=st.session_state.game_over
        )

    if submit:
        guess_word = guess_word.strip()

        if not guess_word:
            st.session_state.message = "단어를 입력하세요."

        elif guess_word not in allowed_words:
            guess_jamo = decompose_word(guess_word)

            if guess_jamo is None:
                st.session_state.message = "한글 단어만 입력할 수 있습니다."

            elif len(guess_jamo) != 5:
                st.session_state.message = (
                    f"이 단어는 자모 {len(guess_jamo)}칸입니다. "
                    f"분해 결과: {' '.join(guess_jamo)}"
                )

            else:
                st.session_state.message = "5자모 단어이지만, 현재 단어 목록에는 없습니다."

        else:
            guess_jamo = allowed_words[guess_word]["jamo"]
            result = judge(st.session_state.answer_jamo, guess_jamo)

            st.session_state.history.append({
                "word": guess_word,
                "jamo": guess_jamo,
                "result": result
            })

            st.session_state.message = ""

            if guess_word == st.session_state.answer_word:
                st.session_state.game_over = True
                st.session_state.message = (
                    f"정답입니다. 정답: {st.session_state.answer_word}"
                )

            elif len(st.session_state.history) >= max_try:
                st.session_state.game_over = True
                st.session_state.message = (
                    f"실패했습니다. 정답: {st.session_state.answer_word}"
                )

    if st.session_state.message:
        st.info(st.session_state.message)

    st.divider()

    for row in st.session_state.history:
        st.write(f"입력 단어: {row['word']}")
        render_row(row["jamo"], row["result"])

    if st.session_state.game_over:
        st.subheader("정답 정보")
        st.write("정답:", st.session_state.answer_word)
        st.write("자모:", " ".join(st.session_state.answer_jamo))
        st.write("뜻:", st.session_state.answer_item.get("definition", ""))

    if st.button("새 게임"):
        start_new_game(words)
        st.rerun()

    # 개발 중 정답 확인용. 배포할 때는 주석 처리하세요.
    #with st.expander("개발용 정답 확인"):
        #st.write(st.session_state.answer_word)
        st.write(" ".join(st.session_state.answer_jamo))


if __name__ == "__main__":
    main()
