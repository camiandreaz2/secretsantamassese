import streamlit as st
import streamlit.components.v1 as components # Rinominiamo per chiarezza
import random
import smtplib
from email.mime.text import MIMEText


lottie_babbo_url = "https://lottie.host/embed/9e8b9ea1-673b-4d26-bcd5-1cfbe148737e/WdRibmGOU1.lottie"
lottie_neve_url = "https://lottie.host/embed/ca25cd91-521d-4bba-8b22-d9cb9e5b7826/ornD9D5peJ.lottie"
lottie_pacco_url = "https://lottie.host/embed/310e18b7-4fe0-45fc-836e-32942c7ec687/bUXLpA2FLl.lottie"

st.markdown(f"""
    <style>
        /*
        z-index 1
        in modo che si posizioni SOPRA la nostra neve.
        "position: relative" è necessario affinché z-index funzioni
        */
        .main .block-container {{
            position: relative;
            z-index: 1;
        }}

        .lottie-iframe {{
            border: none;
            width: 100%;
            height: 100%;
        }}

        /* Contenitore per lo sfondo di neve */
        #neve-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            /*z-index: 0 lo mette sopra lo sfondo base ma sotto il contenuto */
            z-index: 0;
            pointer-events: none;
            opacity: 0.7;
        }}

        /* Contenitore per Babbo Natale (angolo in alto a sinistra) */
        #babbo-corner {{
            position: fixed;
            top: 70px;
            left: 30px;
            width: 250px;
            height: 250px;
            z-index: 999; /* Rimane sopra a tutto */
            pointer-events: none;
        }}

        /* Contenitore per il pacco (angolo in basso a destra) */
        #pacco-corner {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 250px;
            height: 250px;
            z-index: 999; /* Rimane sopra a tutto */
            pointer-events: none;
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


# --- Blocco di Autenticazione  ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

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