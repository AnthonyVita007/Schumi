# Integrazione Frank Emotion Detection - Documentazione

## Panoramica

L'integrazione del modello Frank di emotion detection nel sistema Schumi permette l'analisi emotiva in tempo reale degli autisti tramite la webcam. Il sistema è progettato per essere robusto con fallback automatico ai dati mock quando il modello AI non è disponibile.

## Architettura

### 1. Modulo AI (`app/ai/emotion_detector.py`)

**Funzionalità principali:**
- Lazy loading del modello Keras e Haar Cascade
- Rilevamento del volto più grande nell'immagine
- Preprocessing: BGR→RGB, resize 224x224, normalizzazione [0,1]
- Classificazione in 7 emozioni: Rabbia, Disgusto, Paura, Felicità, Neutralità, Tristezza, Sorpresa
- Mappatura delle emozioni a metriche stress/focus/calm
- Gestione robusta degli errori con fallback

**Thread safety:** Il caricamento del modello è protetto da lock per evitare race conditions.

### 2. Nuovo Endpoint API

**POST `/api/drivers/<id>/monitor/frame`**

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

**Response (successo AI):**
```json
{
  "success": true,
  "data": {
    "time": "14:35:22",
    "stress": 42.5,
    "focus": 61.3,
    "calm": 37.0,
    "emotion": "Neutralita'",
    "probs": {
      "Rabbia": 0.01,
      "Disgusto": 0.02,
      "Paura": 0.03,
      "Felicita'": 0.10,
      "Neutralita'": 0.70,
      "Tristezza": 0.05,
      "Sorpresa": 0.09
    },
    "inferenceMs": 65,
    "bbox": { "x": 120, "y": 80, "w": 160, "h": 160 },
    "timestamp": 1725460522.123
  }
}
```

**Response (fallback mock):**
```json
{
  "success": true,
  "data": {
    "time": "14:35:22",
    "stress": 15.3,
    "focus": 78.9,
    "calm": 65.2,
    "timestamp": 1642689322.123
  }
}
```

### 3. Frontend Migliorato

**Nuove funzionalità JavaScript:**
- `captureAndAnalyzeFrame()`: Cattura frame dalla webcam e li invia per l'analisi
- Fallback automatico al metodo mock in caso di errori
- Frequenza aggiornata a 1 FPS (1000ms) per bilanciare prestazioni e accuratezza
- Compressione JPEG (qualità 0.6) per ridurre payload di rete

## Configurazione

### Variabili di configurazione (app/config.py)

```python
# Path del modello Keras (può essere override via env)
EMOTION_MODEL_PATH = os.environ.get('EMOTION_MODEL_PATH') or 
    (basedir / 'app' / 'ai' / 'models' / 'frank_emotion_detector_model.keras')

# Path della Haar Cascade (può essere override via env)  
HAAR_CASCADE_PATH = os.environ.get('HAAR_CASCADE_PATH') or
    (basedir / 'app' / 'ai' / 'haarcascades' / 'haarcascade_frontalface_default.xml')
```

### Override tramite variabili d'ambiente

```bash
export EMOTION_MODEL_PATH="/path/to/custom/model.keras"
export HAAR_CASCADE_PATH="/path/to/custom/cascade.xml"
```

## Installazione e Setup

### 1. Installazione dipendenze

```bash
pip install -r requirements.txt
```

**Nuove dipendenze aggiunte:**
- `tensorflow==2.18.0` - Per l'inferenza del modello
- `opencv-python==4.8.1.78` - Per face detection e image processing
- `numpy==1.24.3` - Per operazioni array

### 2. Posizionamento modello

Il modello Keras deve essere posizionato in:
```
app/ai/models/frank_emotion_detector_model.keras
```

**Note:**
- Il file è escluso dal git (.gitignore) per evitare di committare file pesanti
- Se il modello non è presente, il sistema funziona con dati mock
- La Haar Cascade è già inclusa nel repository

### 3. Verifica installazione

```bash
python3 test_standalone.py
```

Questo script verifica:
- ✓ Struttura file corretta
- ✓ Logica di mappatura emozioni
- ✓ Presenza Haar Cascade
- ⚠ Presenza modello (opzionale)

## Comportamento del Sistema

### 1. Con Modello AI Disponibile

1. L'utente avvia il monitoraggio
2. La webcam cattura frame a 1 FPS
3. I frame vengono inviati a `/api/drivers/<id>/monitor/frame`
4. Il sistema esegue:
   - Face detection con Haar Cascade
   - Preprocessing dell'immagine
   - Inferenza con modello Keras
   - Mappatura emozioni a metriche
5. I risultati aggiornano il grafico in tempo reale

### 2. Senza Modello AI (Fallback)

1. Il sistema rileva automaticamente l'assenza del modello
2. Fa fallback ai dati mock dal `MonitoringService`
3. L'utente non vede differenze nell'UI
4. I log indicano l'uso del fallback

### 3. Gestione Errori

- **Nessun volto rilevato:** Restituisce valori neutri
- **Errore inferenza:** Fallback a dati mock
- **TensorFlow non disponibile:** Fallback a dati mock
- **Errore rete/parsing:** Usa endpoint mock originale

## Mappatura Emozioni → Metriche

### Heuristica implementata:

**Stress:**
- Rabbia: 100% contributo
- Disgusto: 90% contributo  
- Paura: 90% contributo
- Tristezza: 50% contributo
- Sorpresa: 20% contributo

**Calm:**
- Neutralità: 100% contributo
- Felicità: 80% contributo

**Focus:**
- Neutralità: 80% contributo
- Sorpresa: 60% contributo
- Felicità: 50% contributo
- Paura: -50% contributo (riduce focus)
- Rabbia: -50% contributo (riduce focus)

Tutte le metriche sono normalizzate a 0-100%.

## Test Manuale

### Happy Path

1. Avvia l'applicazione: `python run.py`
2. Vai su `/drivers` e clicca "Monitora" su un autista
3. Consenti accesso webcam
4. Clicca "Avvia Monitoraggio"
5. Osserva:
   - Barre stress/focus/calm che si aggiornano ogni secondo
   - Grafico in tempo reale
   - Console logs con emozioni rilevate (se AI attivo)

### Test Fallback

1. Rinomina temporaneamente il modello: `mv app/ai/models/frank_emotion_detector_model.keras app/ai/models/frank_emotion_detector_model.keras.bak`
2. Riavvia l'app e ripeti il test
3. Verifica che il sistema funzioni con dati mock
4. Controlla i log per messaggi di fallback

## Logging

Il sistema registra:
- **INFO:** Caricamento modello/cascade riuscito
- **WARNING:** Modello/cascade non trovato, uso fallback
- **ERROR:** Errori durante inferenza o processing
- **DEBUG:** Dettagli analisi per ogni frame (emozione, timing)

## Performance

**Configurazione consigliata:**
- **Frequenza:** 1 FPS (regolabile modificando `1000` in `startDataCollection()`)
- **Compressione:** JPEG qualità 0.6
- **Dimensioni input:** 224x224 pixel per inferenza

**Ottimizzazioni implementate:**
- Lazy loading modello (caricato solo una volta)
- Bounding box cache per evitare riprocessing
- Compressione JPEG client-side

## Estensioni Future

- Canvas overlay per visualizzare bounding box del volto
- Display emozione corrente nell'UI
- Frequenza adattiva basata su performance dispositivo
- Conversione modello a TensorFlow Lite per mobile
- Analisi batch per migliorare throughput