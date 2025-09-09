"""
Modulo per il rilevamento delle emozioni tramite analisi del volto

Questo modulo implementa l'analisi delle emozioni in tempo reale utilizzando
il modello Frank di emotion detection su frame catturati dalla webcam.

Features:
- Lazy loading del modello Keras e Haar Cascade
- Rilevamento del volto più grande nell'immagine
- Preprocessing adattivo (RGB/GRAY, input_shape, opzionale raw BGR come nel notebook)
- Classificazione delle emozioni in 7 categorie
- Mappatura delle emozioni a metriche stress/focus/calm
- Gestione robusta degli errori con fallback

Author: Schumi Development Team  
Date: 2024
"""

import base64
import time
import threading
from typing import Dict, Optional, Tuple, Any
import numpy as np
import cv2
from pathlib import Path

# Import TensorFlow with error handling per lazy loading
_model = None
_cascade = None
_model_lock = threading.Lock()
_infer_lock = threading.Lock()  # Lock per serializzare face detection + inferenza

# Etichette delle emozioni nell'ordine del training del modello
EMOTION_LABELS = [
    "Rabbia", "Disgusto", "Paura", "Felicita'",
    "Neutralita'", "Tristezza", "Sorpresa"
]

def _load_model_and_cascade():
    """
    Carica lazy il modello Keras e la Haar Cascade per il face detection.
    Con fallback automatico alla cascade built-in di OpenCV se il path custom fallisce.
    
    Returns:
        Tuple[Any, Any]: (model, cascade) o (None, None) se il caricamento fallisce
    """
    global _model, _cascade
    
    # Doppio controllo con lock per thread safety
    if _model is not None and _cascade is not None:
        return _model, _cascade
        
    with _model_lock:
        if _model is not None and _cascade is not None:
            return _model, _cascade
            
        try:
            import tensorflow as tf
            from flask import current_app
            
            cv2.setNumThreads(1)
            
            # Carica i path dalla configurazione
            model_path = Path(current_app.config['EMOTION_MODEL_PATH'])
            cascade_path = Path(current_app.config['HAAR_CASCADE_PATH'])
            
            # Verifica modello
            if not model_path.exists():
                current_app.logger.warning(f"Modello di emotion detection non trovato: {model_path}")
                return None, None
            
            # Carica Keras model
            current_app.logger.info(f"Caricamento modello emotion detection: {model_path}")
            _model = tf.keras.models.load_model(str(model_path))
            current_app.logger.info("Modello caricato con successo")
            
            # Carica Haar Cascade con fallback
            cascade_loaded = False
            if cascade_path.exists():
                current_app.logger.info(f"Tentativo caricamento Haar Cascade custom: {cascade_path}")
                temp_cascade = cv2.CascadeClassifier(str(cascade_path))
                if not temp_cascade.empty():
                    _cascade = temp_cascade
                    cascade_loaded = True
                    current_app.logger.info("Haar Cascade custom caricata con successo")
                else:
                    current_app.logger.warning("Haar Cascade custom vuota, tentativo fallback")
            else:
                current_app.logger.warning(f"Haar Cascade custom non trovata: {cascade_path}")
            
            if not cascade_loaded:
                fallback_path = Path(cv2.data.haarcascades) / 'haarcascade_frontalface_default.xml'
                current_app.logger.info(f"Tentativo fallback Haar Cascade built-in: {fallback_path}")
                temp_cascade = cv2.CascadeClassifier(str(fallback_path))
                if not temp_cascade.empty():
                    _cascade = temp_cascade
                    cascade_loaded = True
                    current_app.logger.info("Haar Cascade built-in caricata con successo (fallback)")
                else:
                    current_app.logger.error("Anche la Haar Cascade built-in è vuota")
            
            if not cascade_loaded:
                current_app.logger.error("Errore nel caricamento di qualsiasi Haar Cascade")
                return None, None
                
            return _model, _cascade
            
        except ImportError as e:
            try:
                from flask import current_app
                current_app.logger.error(f"TensorFlow non disponibile: {e}")
            except:
                print(f"TensorFlow non disponibile: {e}")
            return None, None
        except Exception as e:
            try:
                from flask import current_app
                current_app.logger.error(f"Errore nel caricamento del modello AI: {e}")
            except:
                print(f"Errore nel caricamento del modello AI: {e}")
            return None, None

def _decode_base64_image(image_data_url: str) -> Optional[np.ndarray]:
    """
    Decodifica un'immagine da data URL base64 a array NumPy BGR.
    """
    try:
        if image_data_url.startswith('data:image'):
            _, encoded = image_data_url.split(',', 1)
        else:
            encoded = image_data_url
            
        image_bytes = base64.b64decode(encoded)
        image_array = np.frombuffer(image_bytes, np.uint8)
        image_bgr = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return image_bgr
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Errore nella decodifica dell'immagine base64: {e}")
        except:
            print(f"Errore nella decodifica dell'immagine base64: {e}")
        return None

def _detect_largest_face(image_bgr: np.ndarray, cascade) -> Optional[Tuple[int, int, int, int]]:
    """
    Rileva il volto più grande nell'immagine usando Haar Cascade.
    """
    try:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        if len(faces) == 0:
            return None
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        return tuple(largest_face)
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Errore nel face detection: {e}")
        except:
            print(f"Errore nel face detection: {e}")
        return None

def _expand_bbox(image_shape, bbox, margin: float = 0.25, make_square: bool = True) -> Tuple[int, int, int, int]:
    """
    Espande il bbox con un margine e (opzionalmente) lo rende quadrato.
    Restituisce bbox clampato dentro l'immagine.
    """
    h_img, w_img = image_shape[:2]
    x, y, w, h = bbox
    cx = x + w / 2.0
    cy = y + h / 2.0

    w2 = w * (1.0 + margin)
    h2 = h * (1.0 + margin)

    if make_square:
        side = max(w2, h2)
        w2 = h2 = side

    x2 = int(round(cx - w2 / 2.0))
    y2 = int(round(cy - h2 / 2.0))
    w2 = int(round(w2))
    h2 = int(round(h2))

    x2 = max(0, x2)
    y2 = max(0, y2)
    if x2 + w2 > w_img:
        w2 = w_img - x2
    if y2 + h2 > h_img:
        h2 = h_img - y2

    return x2, y2, w2, h2

def _preprocess_face_image(image_bgr: np.ndarray, bbox: Tuple[int, int, int, int], input_shape: Tuple, mode: str = 'rgb01') -> Optional[np.ndarray]:
    """
    Preprocessa il volto in base alla input_shape del modello e alla modalità.
    mode:
      - 'rgb01'   -> BGR->RGB + normalizzazione [0,1]
      - 'raw_bgr' -> nessuna conversione colore, nessuna normalizzazione (BGR uint8)
    Supporta sia modelli RGB (HxWx3) sia grayscale (HxWx1).
    """
    try:
        # Determina H, W, C dall'input shape (gestisce (None, H, W, C) o (H, W, C))
        shape = input_shape
        if isinstance(shape, (list, tuple)) and len(shape) == 4:
            _, H, W, C = shape
        elif isinstance(shape, (list, tuple)) and len(shape) == 3:
            H, W, C = shape
        else:
            H, W, C = 224, 224, 3  # fallback

        x, y, w, h = bbox
        face_bgr = image_bgr[y:y+h, x:x+w]

        if C == 1:
            # Modello grayscale
            face_gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
            face_resized = cv2.resize(face_gray, (W, H))
            if mode == 'raw_bgr':
                # Mantieni uint8, aggiungi canale
                face_resized = np.expand_dims(face_resized, axis=-1)  # H, W, 1
            else:
                face_resized = face_resized.astype(np.float32) / 255.0
                face_resized = np.expand_dims(face_resized, axis=-1)
        else:
            # Modello a 3 canali
            if mode == 'raw_bgr':
                # Nessuna conversione, nessuna normalizzazione
                face_resized = cv2.resize(face_bgr, (W, H))  # BGR uint8
            else:
                # Pipeline standard: BGR->RGB + [0,1]
                face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
                face_resized = cv2.resize(face_rgb, (W, H))
                face_resized = face_resized.astype(np.float32) / 255.0

        face_batch = np.expand_dims(face_resized, axis=0)
        return face_batch
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Errore nel preprocessing del volto: {e}")
        except:
            print(f"Errore nel preprocessing del volto: {e}")
        return None

def _to_probabilities(predictions: np.ndarray) -> Optional[np.ndarray]:
    """
    Converte l'output del modello in probabilità.
    - Se già in [0..1] e somma ~1, lo restituisce.
    - Altrimenti applica softmax numericamente stabile.
    """
    try:
        arr = predictions[0] if predictions.ndim == 2 else predictions
        arr = np.asarray(arr).astype(np.float64)

        if np.all(np.isfinite(arr)) and np.all(arr >= -1e-6) and np.isclose(np.sum(arr), 1.0, atol=1e-3):
            return arr

        # Softmax stabile
        arr_shift = arr - np.max(arr)
        exp = np.exp(arr_shift)
        denom = np.sum(exp)
        if denom <= 0 or not np.isfinite(denom):
            return np.ones_like(arr) / max(1, arr.shape[0])
        return exp / denom
    except Exception:
        return None

def _map_emotions_to_metrics(emotion_probs: Dict[str, float]) -> Dict[str, float]:
    """
    Mappa le probabilità delle emozioni alle metriche stress/focus/calm.
    """
    try:
        stress = (
            emotion_probs.get("Rabbia", 0) * 1.0 +
            emotion_probs.get("Disgusto", 0) * 0.9 +
            emotion_probs.get("Paura", 0) * 0.9 +
            emotion_probs.get("Tristezza", 0) * 0.5 +
            emotion_probs.get("Sorpresa", 0) * 0.2
        )
        
        calm = (
            emotion_probs.get("Neutralita'", 0) * 1.0 +
            emotion_probs.get("Felicita'", 0) * 0.8
        )
        
        focus = (
            emotion_probs.get("Neutralita'", 0) * 0.8 +
            emotion_probs.get("Sorpresa", 0) * 0.6 +
            emotion_probs.get("Felicita'", 0) * 0.5 -
            emotion_probs.get("Paura", 0) * 0.5 -
            emotion_probs.get("Rabbia", 0) * 0.5
        )
        
        # Clamp ai valori 0-100 e arrotonda a 0.1
        stress = max(0.0, min(100.0, stress * 100))
        calm = max(0.0, min(100.0, calm * 100))
        focus = max(0.0, min(100.0, focus * 100))
        
        return {
            'stress': round(stress, 1),
            'calm': round(calm, 1),
            'focus': round(focus, 1)
        }
        
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Errore nella mappatura delle metriche: {e}")
        except:
            print(f"Errore nella mappatura delle metriche: {e}")
        # Valori neutrali di fallback
        return {'stress': 25.0, 'calm': 50.0, 'focus': 50.0}

def _get_neutral_emotion_data() -> Dict[str, Any]:
    """
    Restituisce dati emotivi neutrali quando nessun volto è rilevato.
    """
    neutral_probs = {label: 0.0 for label in EMOTION_LABELS}
    neutral_probs["Neutralita'"] = 1.0
    
    return {
        'emotion': "Neutralita'",
        'probs': neutral_probs,
        'inferenceMs': 0,
        'bbox': None
    }

def analyze_frame(image_data_url: str) -> Optional[Dict[str, Any]]:
    """
    Analizza un frame dall'immagine base64 e restituisce i dati emotivi.
    """
    start_time = time.time()
    
    try:
        from flask import current_app

        # Carica modello e cascade
        model, cascade = _load_model_and_cascade()
        if model is None or cascade is None:
            return None
            
        # Decodifica l'immagine base64
        image_bgr = _decode_base64_image(image_data_url)
        if image_bgr is None:
            return None
            
        # Serializza face detection + inferenza con lock per evitare race conditions
        with _infer_lock:
            # Rileva il volto più grande
            face_bbox = _detect_largest_face(image_bgr, cascade)
            if face_bbox is None:
                # Nessun volto rilevato, restituisci valori neutrali
                neutral_data = _get_neutral_emotion_data()
                neutral_data['inferenceMs'] = round((time.time() - start_time) * 1000, 1)
                return neutral_data

            # Espandi bbox per maggiore stabilità e contesto
            x2, y2, w2, h2 = _expand_bbox(image_bgr.shape, face_bbox, margin=0.25, make_square=True)

            # Preprocess: leggi la modalità dalla config e adatta a input_shape
            mode = current_app.config.get('EMOTION_PREPROCESS_MODE', 'rgb01')
            input_shape = getattr(model, 'input_shape', (None, 224, 224, 3))
            face_input = _preprocess_face_image(image_bgr, (x2, y2, w2, h2), input_shape, mode=mode)
            if face_input is None:
                return None
                
            # Inferenza
            predictions = model.predict(face_input, verbose=0)
        
        # Probabilità robuste
        probs_array = _to_probabilities(predictions)
        if probs_array is None or probs_array.shape[0] != len(EMOTION_LABELS):
            try:
                current_app.logger.error(f"Dimensione output modello non valida: {predictions.shape}")
            except:
                print(f"Dimensione output modello non valida: {predictions.shape}")
            return None
            
        # Converti in dizionario
        emotion_probs = {label: float(prob) for label, prob in zip(EMOTION_LABELS, probs_array)}
        
        # Trova l'emozione dominante
        top_emotion = max(emotion_probs, key=emotion_probs.get)
        
        # Prepara il bounding box (quello espanso)
        bbox = {'x': int(x2), 'y': int(y2), 'w': int(w2), 'h': int(h2)}
        
        # Tempo totale
        total_inference_time = round((time.time() - start_time) * 1000, 1)
        
        return {
            'emotion': top_emotion,
            'probs': emotion_probs,
            'inferenceMs': total_inference_time,
            'bbox': bbox
        }
        
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Errore nell'analisi del frame: {e}")
        except:
            print(f"Errore nell'analisi del frame: {e}")
        return None

def get_emotion_metrics(emotion_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calcola le metriche stress/focus/calm dai dati emotivi.
    """
    if not emotion_data or 'probs' not in emotion_data:
        return {'stress': 25.0, 'calm': 50.0, 'focus': 50.0}
        
    return _map_emotions_to_metrics(emotion_data['probs'])