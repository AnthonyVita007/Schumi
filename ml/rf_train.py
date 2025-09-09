import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
import joblib

# -----------------------------
# 1. Caricamento dataset
# -----------------------------
X_train = pd.read_csv("ml/X_train_augmented.csv")
y_train = pd.read_csv("ml/y_train_augmented.csv").squeeze()

df_test = pd.read_csv("ml/dataset_profilato.csv")
X_test = df_test.drop(columns=['stile_guida'])
y_test = df_test['stile_guida']

# -----------------------------
# 2. Scaling
# -----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------------
# 3. Random Forest
# -----------------------------
rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf.fit(X_train_scaled, y_train)
y_pred = rf.predict(X_test_scaled)

# -----------------------------
# 4. Metriche
# -----------------------------
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
conf_matrix = confusion_matrix(y_test, y_pred)

print("--- Risultati Random Forest ---")
print(f"Accuracy: {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print("Matrice di Confusione:\n", conf_matrix)

# -----------------------------
# 5. Salvataggio modello e scaler
# -----------------------------
joblib.dump(rf, 'random_forest_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
