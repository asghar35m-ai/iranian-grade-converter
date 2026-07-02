import streamlit as st

st.set_page_config(
    page_title="Iranian Grade Converter",
    page_icon="🎓",
    layout="centered"
)

texts = {
    "Deutsch 🇩🇪": {
        "title": "🇮🇷 Iranische Note → 🇩🇪 Deutsche Note",
        "input": "Iranische Note eingeben",
        "button": "Umrechnen",
        "result": "Deutsche Note",
        "formula": "Berechnung",
        "note": "Berechnet mit der Bayerischen Formel. Die endgültige Anerkennung erfolgt durch die jeweilige Hochschule."
    },
    "English 🇬🇧": {
        "title": "🇮🇷 Iranian Grade → 🇩🇪 German Grade",
        "input": "Enter Iranian grade",
        "button": "Convert",
        "result": "German grade",
        "formula": "Calculation",
        "note": "Calculated using the Bavarian formula. Final recognition depends on the individual university."
    },
    "فارسی 🇮🇷": {
        "title": "🇮🇷 تبدیل نمره ایران به نمره آلمان 🇩🇪",
        "input": "نمره ایرانی را وارد کنید",
        "button": "تبدیل",
        "result": "نمره آلمانی",
        "formula": "محاسبه",
        "note": "محاسبه با فرمول باواریایی انجام شده است. پذیرش نهایی به دانشگاه مربوطه بستگی دارد."
    }
}

language = st.selectbox(
    "Language / Sprache / زبان",
    list(texts.keys())
)

t = texts[language]

st.title(t["title"])

note = st.number_input(
    t["input"],
    min_value=10.00000,
    max_value=20.00000,
    value=18.00000,
    step=0.00001,
    format="%.5f"
)

if st.button(t["button"]):
    german_grade = 1 + 3 * ((20 - note) / 10)

    st.success(f"{t['result']}: {german_grade:.5f}")

    st.subheader(t["formula"])
    st.code(
        f"1 + 3 × ((20 - {note:.5f}) / 10) = {german_grade:.5f}"
    )

    st.info(t["note"])