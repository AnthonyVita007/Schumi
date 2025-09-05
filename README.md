# SCHUMI — Sistema di Gestione e Valutazione Autisti 🚗

Un’unica piattaforma, semplice e modulare, per gestire l’intero ciclo di vita degli autisti: registrazione con CSV di simulazione, classificazione dello stile di guida, e monitoraggio in tempo reale tramite webcam.

- **Filosofia:** chiaro flusso operativo, componenti indipendenti, AI opzionale con fallback automatici.
- **Stack:** Flask + SQLAlchemy con SQLite di default; frontend leggero HTML/CSS/JS; moduli AI plug-and-play.
- **Risultato:** puoi iniziare subito, poi abilitare le analisi AI quando vuoi, senza blocchi funzionali.

## Tecnologie Utilizzate 🧩

### Backend
- **Python 3.x** — Linguaggio di programmazione principale
- **Flask 3.0.0** — Framework web per API REST e serving delle pagine
- **SQLAlchemy 2.0.23** — ORM per gestione database
- **SQLite** — Database per persistenza dati
- **Werkzeug 3.0.1** — Utilities WSGI e gestione sicurezza

### Frontend
- **HTML5** — Markup semantico per le pagine web
- **CSS3** — Styling moderno con variabili CSS e design responsivo
- **JavaScript Vanilla** — Logica frontend per interazioni e API calls
- **Canvas API** — Overlay per visualizzazione real-time di face detection

### AI/ML Components
- **TensorFlow** — Framework per modelli di emotion detection
- **OpenCV** — Computer vision per rilevamento volti tramite Haar Cascade
- **NumPy** — Elaborazione numerica per preprocessing immagini

### Design e UX
- **Palette Colori Verde** — Identità visiva basata su tonalità di verde (#2ECC71)
- **Design Responsivo** — Compatibile con desktop, tablet e mobile
- **Tipografia Moderna** — Font sans-serif per massima leggibilità

## Funzionamento ⚙️

Il flusso si articola in quattro passi essenziali, esposti anche nell’interfaccia:

1) **Simulazione** 🎮  
- L’autista svolge una sessione su un simulatore.  
- Il simulatore esporta un **CSV** con la telemetria.

2) **Registrazione** 📝  
- Vai su “Autisti” (/drivers) e aggiungi un autista allegando il **CSV**.  
- Il sistema salva il profilo, archivia il file e calcola metriche di base (punti, durata, velocità media).

3) **Classificazione** 🏷️  
- Dalla scheda dell’autista esegui la classificazione.  
- Oggi è simulata (pesi/probabilità); in futuro o opzionalmente può usare un modello **ML** reale sui CSV.  
- Vengono tracciati lo **storico** e la **confidence**.

4) **Monitoraggio in tempo reale** 🎥  
- Entra in “Monitor” per uno specifico autista (/monitor/<id>).  
- Concedi l’accesso alla webcam e avvia/ferma la sessione.  
- Se presente il modello **AI**, vengono mostrati emozione e bounding box; altrimenti **fallback** con dati simulati (stress/focus/calm).

**Pagine principali**  
- **Home (/)** — panoramica e flusso.  
- **Autisti (/drivers)** — lista, aggiunta/modifica, classificazione, accesso al monitoraggio.  
- **Monitor (/monitor/<id>)** — webcam, overlay e (se disponibile) analisi AI.

**Note operative**  
- Il **database SQLite** e le tabelle vengono creati al primo avvio.  
- Se il DB è vuoto, l’app inserisce **tre autisti di esempio**.  
- La cartella upload dei CSV è **data/simulations** (creata al primo salvataggio).

## Setup 🛠️

**Prerequisiti**  
- **Anaconda o Miniconda** 🐍 (consigliato per riproducibilità)  
- **Git**  
- **Webcam** (solo per monitoraggio; facoltativa per il resto)

1) **Installa Anaconda**  
- Scarica e installa dal sito ufficiale:  
  https://www.anaconda.com/download

2) **Clona il repository**
```bash
git clone https://github.com/AnthonyVita007/Schumi.git
cd Schumi
```

3) **Crea e attiva l’environment** con il file .yml  
- Il progetto include **shumi_env.yml** con Python e dipendenze (Flask, SQLAlchemy, TensorFlow, OpenCV, ecc.).
```bash
conda env create -f shumi_env.yml
conda activate shumi_env
```

4) **Configura variabili d’ambiente (opzionale)**  
- Server:
  - **`FLASK_HOST`** (default 0.0.0.0)
  - **`FLASK_PORT`** (default 5000)
  - **`FLASK_DEBUG`** (True/False)
  - **`FLASK_USE_RELOADER`** (0/1 — consigliato 0 su Windows)
  - **`FLASK_THREADED`** (0/1 — consigliato 1)
- AI:
  - **`EMOTION_MODEL_PATH`** (default app/ai/models/frank_emotion_detector_model.keras)
  - **`HAAR_CASCADE_PATH`** (default app/ai/haarcascades/haarcascade_frontalface_default.xml; fallback automatico a OpenCV)

Esempi (macOS/Linux):
```bash
export FLASK_USE_RELOADER=0
export FLASK_THREADED=1
```
Esempi (Windows PowerShell):
```powershell
$env:FLASK_USE_RELOADER="0"
$env:FLASK_THREADED="1"
```

5) **Abilita l’AI per l’emotion detection (opzionale)**  
- Posiziona il modello Keras in:  
  app/ai/models/frank_emotion_detector_model.keras  
- Se il modello non è presente, il monitoraggio userà comunque **dati simulati**.

6) **Avvia l’applicazione**
```bash
python run.py
```
- Apri il browser su **http://localhost:5000**  
- Verifica il corretto funzionamento su **/**, **/drivers** e **/monitor/<id>**.

**Suggerimenti 💡**  
- **Windows:** per massima stabilità usa `FLASK_USE_RELOADER=0` e `FLASK_THREADED=1`.  
- **Permessi webcam:** consenti l’accesso dal browser per usare il monitoraggio.  
- **Cartelle/DB:** vengono creati automaticamente; non sono richiesti passaggi manuali.