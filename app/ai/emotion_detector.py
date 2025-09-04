"""
Modulo per il rilevamento delle emozioni tramite analisi del volto

Questo modulo implementa l'analisi delle emozioni in tempo reale utilizzando
il modello Frank di emotion detection su frame catturati dalla webcam.

Features:
- Lazy loading del modello Keras e Haar Cascade
- Rilevamento del volto più grande nell'immagine  
- Preprocessing dell'immagine (BGR→RGB, resize 224x224, normalizzazione)
- Classificazione delle emozioni in 7 categorie
- Mappatura delle emozioni a metriche stress/focus/calm
- Gestione robusti degli errori con fallback

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
        # Verifica nuovamente dopo aver acquisito il lock
        if _model is not None and _cascade is not None:
            return _model, _cascade
            
        try:
            # Import qui per evitare errori se TensorFlow non è disponibile
            import tensorflow as tf
            from flask import current_app
            
            # Limita i thread di OpenCV per stabilità su Windows
            cv2.setNumThreads(1)
            
            # Carica i path dalla configurazione
            model_path = Path(current_app.config['EMOTION_MODEL_PATH'])
            cascade_path = Path(current_app.config['HAAR_CASCADE_PATH'])
            
            # Verifica che il modello esista
            if not model_path.exists():
                current_app.logger.warning(f"Modello di emotion detection non trovato: {model_path}")
                return None, None
            
            # Carica il modello Keras
            current_app.logger.info(f"Caricamento modello emotion detection: {model_path}")
            _model = tf.keras.models.load_model(str(model_path))
            current_app.logger.info("Modello caricato con successo")
            
            # Carica la Haar Cascade con fallback
            cascade_loaded = False
            
            # Prova prima il path custom
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
            
            # Fallback alla cascade built-in di OpenCV
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
    
    Args:
        image_data_url (str): Data URL nel formato "data:image/jpeg;base64,..."
        
    Returns:
        Optional[np.ndarray]: Immagine BGR o None se decodifica fallisce
    """
    try:
        # Rimuovi il prefisso data URL
        if image_data_url.startswith('data:image'):
            header, encoded = image_data_url.split(',', 1)
        else:
            encoded = image_data_url
            
        # Decodifica base64
        image_bytes = base64.b64decode(encoded)
        
        # Converte a array NumPy e decodifica con OpenCV
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
    
    Args:
        image_bgr (np.ndarray): Immagine in formato BGR
        cascade: Haar Cascade classificatore caricato
        
    Returns:
        Optional[Tuple[int, int, int, int]]: (x, y, w, h) del volto più grande o None
    """
    try:
        # Converti in grayscale per il face detection
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        
        # Rileva i volti
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return None
            
        # Trova il volto con area maggiore
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        return tuple(largest_face)
        
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Errore nel face detection: {e}")
        except:
            print(f"Errore nel face detection: {e}")
        return None

def _preprocess_face_image(image_bgr: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
    """
    Preprocessa l'immagine del volto per l'inferenza del modello.
    
    Args:
        image_bgr (np.ndarray): Immagine BGR originale
        bbox (Tuple[int, int, int, int]): Bounding box del volto (x, y, w, h)
        
    Returns:
        Optional[np.ndarray]: Immagine preprocessata (1, 224, 224, 3) o None
    """
    try:
        x, y, w, h = bbox
        
        # Estrai il volto
        face_bgr = image_bgr[y:y+h, x:x+w]
        
        # Converti BGR a RGB
        face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
        
        # Resize a 224x224 (dimensione attesa dal modello)
        face_resized = cv2.resize(face_rgb, (224, 224))
        
        # Normalizzazione a [0, 1]
        face_normalized = face_resized.astype(np.float32) / 255.0
        
        # Aggiungi batch dimension
        face_batch = np.expand_dims(face_normalized, axis=0)
        
        return face_batch
        
    except Exception as e:
        try:
            from flask import current_app
            current_app.logger.error(f"Errore nel preprocessing del volto: {e}")
        except:
            print(f"Errore nel preprocessing del volto: {e}")
        return None

def _map_emotions_to_metrics(emotion_probs: Dict[str, float]) -> Dict[str, float]:
    """
    Mappa le probabilità delle emozioni alle metriche stress/focus/calm.
    
    Args:
        emotion_probs (Dict[str, float]): Probabilità per ogni emozione
        
    Returns:
        Dict[str, float]: Metriche stress, focus, calm in percentuale 0-100
    """
    try:
        # Heuristica per mappare emozioni a metriche
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
    
    Returns:
        Dict[str, Any]: Dati emotivi neutri
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
    
    Args:
        image_data_url (str): Data URL base64 dell'immagine da analizzare
        
    Returns:
        Optional[Dict[str, Any]]: Dati dell'analisi emotiva o None se fallisce
        
    Example Return:
        {
            'emotion': 'Neutralita'',
            'probs': {'Rabbia': 0.01, 'Disgusto': 0.02, ...},
            'inferenceMs': 65,
            'bbox': {'x': 120, 'y': 80, 'w': 160, 'h': 160}
        }
    """
    start_time = time.time()
    
    try:
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
                
            # Preprocessa l'immagine del volto
            face_input = _preprocess_face_image(image_bgr, face_bbox)
            if face_input is None:
                return None
                
            # Esegui l'inferenza
            inference_start = time.time()
            predictions = model.predict(face_input, verbose=0)
            inference_time = (time.time() - inference_start) * 1000
        
        # Estrai le probabilità
        if predictions.shape[1] != len(EMOTION_LABELS):
            try:
                from flask import current_app
                current_app.logger.error(f"Dimensione output modello non valida: {predictions.shape}")
            except:
                print(f"Dimensione output modello non valida: {predictions.shape}")
            return None
            
        probs_array = predictions[0]
        
        # Assicurati che sia un softmax valido (normalizza se necessario)
        if np.sum(probs_array) > 0:
            probs_array = probs_array / np.sum(probs_array)
        else:
            # Fallback a distribuzione uniforme
            probs_array = np.ones(len(EMOTION_LABELS)) / len(EMOTION_LABELS)
            
        # Converti in dizionario
        emotion_probs = {
            label: float(prob) for label, prob in zip(EMOTION_LABELS, probs_array)
        }
        
        # Trova l'emozione dominante
        top_emotion = max(emotion_probs, key=emotion_probs.get)
        
        # Prepara il bounding box
        x, y, w, h = face_bbox
        bbox = {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}
        
        # Calcola tempo totale di inferenza
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
    
    Args:
        emotion_data (Dict[str, Any]): Dati dell'analisi emotiva
        
    Returns:
        Dict[str, float]: Metriche stress, focus, calm
    """
    if not emotion_data or 'probs' not in emotion_data:
        return {'stress': 25.0, 'calm': 50.0, 'focus': 50.0}
        
    return _map_emotions_to_metrics(emotion_data['probs'])