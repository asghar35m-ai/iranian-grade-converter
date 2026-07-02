import streamlit as st

st.title("Iranische Note → Deutsche Note")

note = st.number_input(
    "Iranische Note eingeben",
    min_value=10.0,
    max_value=20.0,
    step=0.01
)

if st.button("Umrechnen"):
    deutsch = 1 + 3 * ((20 - note) / (20 - 10))
    deutsch = round(deutsch, 2)

    st.success(f"Deutsche Note: {deutsch}")
    st.caption("Berechnet mit der Bayerischen Formel.")
    exit()
    import streamlit as st

st.title("Iranische Note → Deutsche Note")

note = st.number_input(
    "Iranische Note eingeben",
    min_value=10.0,
    max_value=20.0,
    step=0.01
)

if st.button("Umrechnen"):
    deutsch = 1 + 3 * ((20 - note) / (20 - 10))
    deutsch = round(deutsch, 2)

    st.success(f"Deutsche Note: {deutsch}")
    st.caption("Berechnet mit der Bayerischen Formel.")
