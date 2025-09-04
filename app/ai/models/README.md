# Frank Emotion Detection Model

Questo file dovrebbe contenere il modello Keras addestrato per il rilevamento delle emozioni.

Il modello si aspetta input di forma (None, 224, 224, 3) e restituisce probabilità per 7 classi di emozioni:
1. Rabbia
2. Disgusto 
3. Paura
4. Felicità
5. Neutralità
6. Tristezza
7. Sorpresa

## Istruzioni per l'installazione

1. Ottenere il file `frank_emotion_detector_model.keras` addestrato
2. Posizionarlo in questa directory: `app/ai/models/frank_emotion_detector_model.keras`
3. Il sistema caricherà automaticamente il modello al primo utilizzo

## Note

- Il modello deve essere compatibile con TensorFlow/Keras
- L'input deve essere preprocessato: BGR→RGB, resize 224x224, normalizzazione [0,1]
- Se il modello non è presente, il sistema userà automaticamente i dati mock

## Fallback

Se questo modello non è disponibile, l'applicazione continuerà a funzionare usando
i dati emotivi simulati dal MonitoringService.