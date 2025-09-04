# **Sistema di Gestione e Valutazione Autisti**

Una piattaforma integrata per registrare, analizzare e monitorare le performance degli autisti, sviluppata con Python Flask e tecnologie web moderne, seguendo principi di programmazione orientata agli oggetti.

## **Descrizione**

Il **Sistema di Gestione e Valutazione Autisti** è un'applicazione web completa che permette la gestione degli autisti aziendali attraverso un flusso di lavoro strutturato in quattro fasi principali:

1. **Simulazione** - Raccolta dati di guida attraverso sessioni simulate
2. **Registrazione** - Inserimento autisti nel sistema con caricamento file CSV
3. **Classificazione** - Analisi automatica dello stile di guida tramite algoritmi ML
4. **Monitoraggio** - Tracciamento in tempo reale dello stato emotivo e comportamentale

## **Tecnologie Utilizzate**

### **Backend**
- **Python 3.x** - Linguaggio di programmazione principale
- **Flask 3.0.0** - Framework web per API REST e serving delle pagine
- **SQLAlchemy 2.0.23** - ORM per gestione database
- **SQLite** - Database per persistenza dati
- **Werkzeug 3.0.1** - Utilities WSGI e gestione sicurezza

### **Frontend**
- **HTML5** - Markup semantico per le pagine web
- **CSS3** - Styling moderno con variabili CSS e design responsivo
- **JavaScript Vanilla** - Logica frontend per interazioni e API calls
- **Canvas API** - Overlay per visualizzazione real-time di face detection

### **AI/ML Components**
- **TensorFlow** - Framework per modelli di emotion detection
- **OpenCV** - Computer vision per rilevamento volti tramite Haar Cascade
- **NumPy** - Elaborazione numerica per preprocessing immagini

### **Design e UX**
- **Palette Colori Verde** - Identità visiva basata su tonalità di verde (#2ECC71)
- **Design Responsivo** - Compatibile con desktop, tablet e mobile
- **Tipografia Moderna** - Font sans-serif per massima leggibilità

## **Struttura del Progetto**

```
/project_root
├── app/
│   ├── __init__.py          # Inizializzazione applicazione Flask
│   ├── models.py            # Modelli SQLAlchemy (Driver, SimulationData, etc.)
│   ├── routes.py            # Endpoint API e route per pagine web
│   ├── services.py          # Logica di business e servizi
│   ├── utils.py             # Funzioni di utilità
│   └── config.py            # Configurazioni applicazione
├── static/
│   ├── css/
│   │   ├── style.css        # Foglio di stile principale
│   │   └── chart.css        # Stili specifici per grafici
│   ├── js/
│   │   └── main.js          # JavaScript principale
│   └── img/                 # Immagini e icone
├── templates/
│   ├── base.html            # Template base con struttura comune
│   ├── landing_page.html    # Pagina di atterraggio
│   ├── drivers.html         # Gestione autisti
│   ├── monitor.html         # Monitoraggio real-time
│   └── error.html           # Pagina errori
├── data/
│   └── simulations/         # Directory file CSV caricati
├── run.py                   # Script avvio server di sviluppo
├── requirements.txt         # Dipendenze Python
└── README.md               # Documentazione progetto
```

## **Caratteristiche Principali**

### **🔧 Architettura Robusta**
- **Programmazione OOP** - Codice organizzato in classi ben strutturate
- **Pattern MVC** - Separazione logica tra modelli, viste e controlli
- **API RESTful** - Endpoint standardizzati per comunicazione client-server
- **Gestione Errori** - Sistema completo di logging e handling eccezioni

### **👥 Gestione Autisti**
- Registrazione nuovo autista con dati anagrafici
- Caricamento file CSV contenenti dati simulazione
- Visualizzazione elenco autisti con filtri e ricerca
- Gestione stati e classificazioni

### **🤖 Classificazione Intelligente**
- Simulazione analisi ML per determinare stile di guida
- Classificazioni: Principiante, Efficiente, Esperto
- Cronologia classificazioni per ogni autista
- Confidence score per affidabilità risultati

### **📊 Monitoraggio Real-Time con AI**
- Interfaccia webcam per acquisizione video in tempo reale
- **Rilevamento volti** tramite Haar Cascade con fallback automatico
- **Analisi emozioni** tramite modelli TensorFlow integrati
- Overlay canvas con bounding box e etichette emozioni
- **Stabilità AI** con threading sicuro e gestione errori

### **🎨 Interfaccia Moderna**
- Design pulito e intuitivo
- Palette verde per identità aziendale
- Componenti interattivi (modal, form, card)
- Feedback visivo per azioni utente

## **Installazione e Configurazione**

### **Prerequisiti**
- Python 3.8+ installato sul sistema
- pip (package manager Python)
- Git per clonazione repository

### **Passaggi Installazione**

1. **Clonazione Repository**
   ```bash
   git clone https://github.com/AnthonyVita007/Schumi.git
   cd Schumi
   ```

2. **Installazione Dipendenze**
   ```bash
   pip install -r requirements.txt
   
   # Per funzionalità AI (opzionale ma consigliato)
   pip install tensorflow opencv-python numpy
   ```

3. **Configurazione Ambiente** (Opzionale)
   ```bash
   # Creazione file .env per variabili ambiente
   touch .env
   
   # Aggiungi configurazioni personalizzate
   echo "FLASK_ENV=development" >> .env
   echo "SECRET_KEY=your-secret-key-here" >> .env
   
   # Configurazioni server per stabilità (Windows)
   echo "FLASK_USE_RELOADER=0" >> .env  # Disabilita auto-reload
   echo "FLASK_THREADED=1" >> .env      # Abilita threading
   
   # Path AI custom (opzionali)
   echo "EMOTION_MODEL_PATH=/path/to/custom/model.keras" >> .env
   echo "HAAR_CASCADE_PATH=/path/to/custom/cascade.xml" >> .env
   ```

4. **Avvio Applicazione**
   ```bash
   python run.py
   ```

5. **Accesso Applicazione**
   - Apri browser e vai su: `http://localhost:5000`
   - L'applicazione sarà disponibile con dati di esempio precaricati

## **Guida all'Utilizzo**

### **1. Pagina Principale**
- Panoramica del sistema con spiegazione del flusso di lavoro
- Accesso rapido alla gestione autisti
- Descrizione delle caratteristiche principali

### **2. Gestione Autisti (`/drivers`)**
- **Visualizzazione**: Elenco autisti con informazioni essenziali
- **Ricerca**: Filtro per nome, classificazione, stato monitoraggio
- **Aggiunta**: Modal per registrazione nuovo autista con upload CSV
- **Dettagli**: Card autisti cliccabili per aprire modal dettagli/editing
- **Azioni**: Nel modal dettagli: modifica nome/cognome, sostituzione file CSV, classificazione e eliminazione autista
- **Monitoraggio**: Accesso diretto al monitoraggio tramite link nelle card

### **3. Monitoraggio (`/monitor/<driver_id>`)**
- **Webcam**: Acquisizione video in tempo reale (richiede permessi browser)
- **Face Detection**: Rilevamento automatico volti con overlay visivo
- **Analisi AI**: Classificazione emozioni in tempo reale se modello disponibile
- **Fallback**: Sistema robusto con dati mock se AI non disponibile
- **Controlli**: Avvio/stop sessione monitoraggio

## **API Endpoints**

### **Gestione Autisti**
- `GET /api/drivers` - Lista tutti gli autisti
- `POST /api/drivers` - Registra nuovo autista
- `GET /api/drivers/<id>` - Dettagli autista specifico
- `PUT/PATCH /api/drivers/<id>` - Aggiorna informazioni autista
- `DELETE /api/drivers/<id>` - Elimina autista
- `GET /api/drivers/<id>/classify` - Esegui classificazione

### **Monitoraggio**
- `GET /api/drivers/<id>/monitor` - Dati preparazione monitoraggio
- `POST /api/drivers/<id>/monitor/start` - Avvia sessione monitoraggio
- `POST /api/drivers/<id>/monitor/stop` - Interrompi sessione
- `GET /api/drivers/<id>/monitor/data` - Dati emotivi real-time (fallback)
- `POST /api/drivers/<id>/monitor/frame` - Analisi AI frame webcam (nuovo)

### **Utility**
- `GET /api/health` - Stato salute applicazione

## **Configurazione AI e Stabilità**

### **Haar Cascade Fallback**
Il sistema implementa un fallback automatico robusto per il caricamento delle Haar Cascade:

1. **Path Custom**: Tenta caricamento da `HAAR_CASCADE_PATH` (configurabile)
2. **Fallback Automatico**: Se fallisce, usa cascade built-in di OpenCV (`cv2.data.haarcascades`)
3. **Validazione**: Verifica sempre che la cascade non sia vuota prima dell'uso
4. **Logging**: Traccia dettagliato del processo di caricamento nei log

### **Stabilità Threading**
Per garantire stabilità su Windows e sistemi multi-thread:

- **Serializzazione AI**: Lock dedicato per face detection + model inference
- **Thread OpenCV**: Limitazione automatica thread interni (`cv2.setNumThreads(1)`)
- **Configurabile**: Server reloader e threading tramite variabili ambiente

### **Variabili d'Ambiente Server**
```bash
# Stabilità raccomandata per Windows
FLASK_USE_RELOADER=0  # Disabilita auto-reload (evita conflitti)
FLASK_THREADED=1      # Abilita threading (migliori performance)

# Path AI personalizzati (opzionali)
EMOTION_MODEL_PATH=/custom/path/model.keras
HAAR_CASCADE_PATH=/custom/path/cascade.xml
```

### **Requisiti Windows**
- **Percorsi ASCII**: Evitare caratteri non-ASCII nei path di progetto
- **Threading**: Usare `FLASK_USE_RELOADER=0` per stabilità massima
- **Dependencies**: Installare TensorFlow e OpenCV tramite pip

## **Considerazioni su Design e Stile**

### **Palette Colori**
- **Primario**: `#2ECC71` (Verde Emerald) - Elementi principali e CTA
- **Secondario**: `#90EE90` (Verde Chiaro) - Accenti e highlights  
- **Neutri**: `#ECF0F1` (Clouds) - Sfondi e separatori
- **Testo**: `#2C3E50` (Midnight Blue) - Testo principale

### **Tipografia**
- **Font Family**: Segoe UI, system-ui, sans-serif
- **Gerarchia**: H1-H4 per struttura contenuti
- **Leggibilità**: Contrasto ottimizzato per accessibilità

### **Componenti UI**
- **Bottoni**: Stili primary, secondary, danger con hover effects
- **Card**: Layout contenuti con shadow e bordi arrotondati
- **Modal**: Overlay per form e dialoghi
- **Form**: Validazione real-time con feedback visivo

## **Note sullo Sviluppo**

### **Sezioni Stub per Integrazione ML**

Il sistema è stato progettato per facilitare l'integrazione futura di modelli di Machine Learning reali:

1. **Classificatore**: `ClassificationService.classify_driver()` simula l'analisi CSV
2. **Analisi Emotiva**: `MonitoringService.generate_emotion_data()` genera dati mock
3. **Computer Vision**: Struttura predisposta per integrazione webcam analysis

### **Estensibilità**

- **Database**: Facile migrazione da SQLite a PostgreSQL/MySQL
- **API**: Struttura RESTful standard per integrazione esterna
- **Frontend**: Componenti modulari per aggiunta nuove funzionalità
- **Configurazione**: Sistema configurazione flessibile per ambienti diversi

## **Deployment Produzione**

Per deploy in produzione, considerare:

1. **WSGI Server**: Gunicorn al posto del server sviluppo Flask
2. **Database**: PostgreSQL per maggiori performance
3. **Sicurezza**: HTTPS, autenticazione, validazione input
4. **Monitoring**: Logging applicativo e metriche performance
5. **Scalabilità**: Load balancer e cache (Redis)

## **Troubleshooting**

### **Problemi Comuni**

**Error: Modulo non trovato**
```bash
pip install -r requirements.txt
```

**Database locked**
```bash
# Rimuovi database e riavvia
rm database.db
python run.py
```

**Porta occupata**
```bash
# Cambia porta nel run.py o usa variabile ambiente
export FLASK_PORT=5001
python run.py
```

**Errori AI/OpenCV (Windows)**
```bash
# Se problemi con percorsi non-ASCII
FLASK_USE_RELOADER=0 FLASK_THREADED=1 python run.py

# Reinstalla dipendenze AI se necessario
pip uninstall opencv-python tensorflow
pip install opencv-python tensorflow
```

**Haar Cascade non trovata**
- Il sistema usa automaticamente fallback a OpenCV built-in
- Controlla log per conferma: "Haar Cascade built-in caricata con successo (fallback)"

## **Contributi e Sviluppo**

Il progetto segue le best practice di sviluppo Python:
- **Documentazione**: Docstrings per tutte le funzioni
- **Type Hints**: Annotazioni tipo quando appropriato  
- **Error Handling**: Gestione eccezioni robusta
- **Testing**: Struttura predisposta per unit test

## **Licenza e Informazioni**

**© 2024 Schumi Project**  
Sviluppato con Flask e tecnologie moderne per la gestione intelligente degli autisti.

---

Per ulteriori informazioni tecniche e architetturali, consultare la documentazione nel codice sorgente o contattare il team di sviluppo.
