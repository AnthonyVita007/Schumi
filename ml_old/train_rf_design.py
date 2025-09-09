# --- 1. Importazione delle librerie necessarie ---
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# --- 2. Caricamento e preparazione del dataset ---
df = pd.read_csv('dataset60_smote_240.csv')

features = df.drop(columns=['stile_guida'])
etichetta = df['stile_guida']

scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

X_train, X_test, y_train, y_test = train_test_split(features_scaled, etichetta, test_size=0.2, random_state=42)

# --- 3. Addestramento e Valutazione del Modello Random Forest ---
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

accuracy_rf = accuracy_score(y_test, y_pred_rf)
precision_rf = precision_score(y_test, y_pred_rf, average='weighted', zero_division=0)
recall_rf = recall_score(y_test, y_pred_rf, average='weighted', zero_division=0)
conf_matrix_rf = confusion_matrix(y_test, y_pred_rf)

# Stampa i risultati in formato testo
print("--- Risultati del Modello Random Forest ---")
print(f"Accuratezza (Accuracy): {accuracy_rf:.2f}")
print(f"Precisione (Precision): {precision_rf:.2f}")
print(f"Richiamo (Recall): {recall_rf:.2f}")
print("\nMatrice di Confusione:\n", conf_matrix_rf)

# --- 4. Analisi dell'Importanza delle Features ---
feature_importances = rf.feature_importances_
feature_names = features.columns
sorted_indices = np.argsort(feature_importances)[::-1]

print("\n--- Importanza delle Features ---")
for i in sorted_indices:
    print(f"{feature_names[i]}: {feature_importances[i]:.4f}")

# --- 5. Creazione delle visualizzazioni ---

# Genera l'immagine per la Matrice di Confusione
labels = sorted(y_test.unique())
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix_rf, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.title('Matrice di Confusione (Random Forest)')
plt.xlabel('Predetto')
plt.ylabel('Reale')
plt.show()

# Genera l'immagine per l'Importanza delle Features
sorted_importances = feature_importances[sorted_indices]
sorted_names = [feature_names[i] for i in sorted_indices]

plt.figure(figsize=(10, 7))
plt.barh(range(len(sorted_importances)), sorted_importances, align='center')
plt.yticks(range(len(sorted_importances)), sorted_names)
plt.xlabel('Importanza')
plt.title('Importanza delle Features (Random Forest)')
plt.show()

    
# --- 6. Salvataggio del Modello e dello Scaler ---

joblib.dump(rf, 'random_forest_model.pkl')
joblib.dump(scaler, 'scaler.pkl')