import streamlit as st
import streamlit.components.v1 as components
import base64
import random
import smtplib
from email.mime.text import MIMEText

file_audio_path = "audio/jingle_bells.mp3" 
lottie_babbo_url = "https://lottie.host/embed/9e8b9ea1-673b-4d26-bcd5-1cfbe148737e/WdRibmGOU1.lottie"
lottie_neve_url = "https://lottie.host/embed/ca25cd91-521d-4bba-8b22-d9cb9e5b7826/ornD9D5peJ.lottie"
lottie_pacco_url = "https://lottie.host/embed/310e18b7-4fe0-45fc-836e-32942c7ec687/bUXLpA2FLl.lottie"

st.markdown('''
<meta name="viewport" content="width=device-width, initial-scale=1.0">
''', unsafe_allow_html=True)

st.markdown(f"""
    <style>
        /* Stili di base per tutti gli schermi (desktop) */
        .main .block-container {{
            position: relative;
            z-index: 1;
        }}

        .lottie-iframe {{
            border: none;
            width: 100%;
            height: 100%;
        }}

        #neve-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
            opacity: 0.7;
        }}

        #babbo-corner {{
            position: fixed;
            top: 70px;
            left: 30px;
            width: 250px; /* Grande per desktop */
            height: 250px;
            z-index: 999;
            pointer-events: none;
        }}

        #pacco-corner {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 250px; /* Grande per desktop */
            height: 250px;
            z-index: 999;
            pointer-events: none;
        }}

        /* --- MEDIA QUERY PER SMARTPHONE --- */
        /* Queste regole verranno applicate solo se la larghezza dello schermo è 768px o inferiore */
        @media (max-width: 768px) {{
            #babbo-corner {{
                width: 120px;  /* Più piccolo per mobile */
                height: 120px;
                top: 50px;     /* Meno distanza dal bordo */
                left: 10px;
            }}

            #pacco-corner {{
                width: 120px;  /* Più piccolo per mobile */
                height: 120px;
                bottom: 10px;  /* Meno distanza dal bordo */
                right: 10px;
            }}
        }}

    </style>

    <div id="neve-bg">
        <iframe class="lottie-iframe" src="{lottie_neve_url}"></iframe>
    </div>
    <div id="babbo-corner">
        <iframe class="lottie-iframe" src="{lottie_babbo_url}"></iframe>
    </div>
    <div id="pacco-corner">
        <iframe class="lottie-iframe" src="{lottie_pacco_url}"></iframe>
    </div>
    """,
    unsafe_allow_html=True
)

def autoplay_audio(file_path: str):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true" loop="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            components.html(md, height=0)
    except FileNotFoundError:
        pass

# --- Blocco di Autenticazione  ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if st.session_state.authenticated:
    autoplay_audio(file_audio_path)

if not st.session_state.authenticated:
    st.title("🔒 Accesso all'app Secret Santa")
    pwd = st.text_input("Inserisci la password dell'organizzatore", type="password")

    if st.button("Entra"):
        if pwd == st.secrets["app_password"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Password errata")
    st.stop()


st.write("<h1 style='text-align:center;'>🎅 Secret Santa – Natale Magico 🎄</h1>", unsafe_allow_html=True)
#st.audio("audio/jingle_bells.mp3", format="audio/mp3")

# --- Funzioni Python ---
def genera_abbinamenti(partecipanti):
    destinazioni = partecipanti[:]

    while True:
        random.shuffle(destinazioni)
        if all(p != d for p, d in zip(partecipanti, destinazioni)):
            return list(zip(partecipanti, destinazioni))

sender_email = st.secrets["email"]
sender_password = st.secrets["password"]

def invia_email(email_dest, nome_dest, assegnato_a):
    corpo = f"""
Ciao {nome_dest}! 🎄

Abbiamo girato, mescolato, rigirato… e alla fine il destino ha scelto per te.

🧦 Il fortunatissimo destinatario del tuo regalo sarà:
👉 {assegnato_a}

Sì, puoi insultare il fato.
Sì, puoi ridere.
Sì, devi comprare davvero un regalo.

Forza, rendilo indimenticabile! 🎁
"""

    msg = MIMEText(corpo)
    msg["Subject"] = "🎁 Il Natale non è mai stato così strano"
    msg["From"] = sender_email
    msg["To"] = email_dest

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        return str(e)


# --- UI App ---
st.write("### 🎁 Inserisci i partecipanti nel formato:")
st.code("Nome Cognome, email@example.com", language="text")

with st.form("form_partecipanti"):
    input_text = st.text_area("Lista partecipanti", height=200)
    submitted = st.form_submit_button("Genera e invia assegnazioni 🎄")


if submitted:
    righe = input_text.strip().split("\n")
    nomi = []
    emails = {}
    email_set = set()
    nome_set = set()

    partecipanti_validi = True
    for riga in righe:
        if not riga.strip():
            continue
        try:
            nome, email = [x.strip() for x in riga.split(",")]
            if not nome or not email:
                raise ValueError("Nome o email mancanti")
        except Exception:
            st.error(f"❌ Formato errato nella riga: '{riga}'")
            partecipanti_validi = False
            continue

        if nome in nome_set:
            st.error(f"❌ Nome duplicato: {nome}")
            partecipanti_validi = False
        if email in email_set:
            st.error(f"❌ Email duplicata: {email}")
            partecipanti_validi = False

        nome_set.add(nome)
        email_set.add(email)
        nomi.append(nome)
        emails[nome] = email
    
    if not partecipanti_validi:
        st.stop()

    if len(nomi) < 2:
        st.error("❌ Servono almeno 2 partecipanti.")
        st.stop()

    with st.spinner("Genero gli abbinamenti e invio le email... 💌"):
        abbinamenti = genera_abbinamenti(nomi)

        report = []
        for donatore, destinatario in abbinamenti:
            esito = invia_email(emails[donatore], donatore, destinatario)
            report.append((donatore, esito))

    st.success("🎉 Abbinamenti generati e email elaborate!")
    st.write("### 📨 Risultato invii")

    for nome, esito in report:
        if esito is True:
            st.write(f"✔ Email inviata con successo a **{nome}** 🎅")
        else:
            st.write(f"❌ Errore nell'invio a {nome}: `{esito}`")