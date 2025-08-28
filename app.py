import streamlit as st
import openai
from ebooklib import epub
from bs4 import BeautifulSoup
import fitz  # PyMuPDF do PDF

# 🔑 ustaw swój klucz OpenAI
openai.api_key = "TWÓJ_API_KEY"

# ---------- Funkcje ----------
def read_epub(file):
    book = epub.read_epub(file)
    text = ""
    for item in book.get_items():
        if item.get_type() == 9:  # HTML w EPUB
            soup = BeautifulSoup(item.get_body_content(), "html.parser")
            text += soup.get_text() + "\n"
    return text

def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

def analyze_and_color(text):
    prompt = f"""
    Oznacz części mowy w poniższym tekście:
    - Czasowniki: <span style='color:orange'>...</span>
    - Rzeczowniki: <span style='color:blue'>...</span>
    - Przymiotniki: <span style='color:green'>...</span>
    - Zaimek (I, he, she, we, they): <span style='color:red'>...</span>

    Tekst:
    {text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

def explain_sentence(sentence):
    prompt = f"""
    Wyjaśnij krok po kroku zdanie:
    {sentence}

    1. Podaj polskie tłumaczenie.  
    2. Rozbij na części mowy.  
    3. Wyjaśnij konstrukcję gramatyczną.  
    4. Dodaj ciekawostkę stylistyczną (jeśli jest).
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

# ---------- Interfejs ----------
st.title("📚 Nauka angielskiego z ebooków")

uploaded_file = st.file_uploader("Wgraj plik EPUB lub PDF", type=["epub", "pdf"])

if uploaded_file:
    if uploaded_file.type == "application/epub+zip":
        text = read_epub(uploaded_file)
    else:
        text = read_pdf(uploaded_file)

    pages = text.split("\n\n")  # dzielenie na akapity
    page_num = st.number_input("Wybierz stronę:", 0, len(pages)-1, 0)
    page_text = pages[page_num][:1000]  # limit długości

    st.markdown("### Oryginalny tekst")
    st.write(page_text)

    if st.button("Analizuj stronę"):
        colored = analyze_and_color(page_text)
        st.markdown(colored, unsafe_allow_html=True)

    sentence = st.text_input("Podaj zdanie do analizy:")
    if sentence:
        explanation = explain_sentence(sentence)
        st.markdown("### Wyjaśnienie")
        st.write(explanation)
