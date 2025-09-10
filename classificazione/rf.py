import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score
import joblib

# -----------------------------
# 1. Caricamento train e test
# -----------------------------
df_train_orig = pd.read_csv("classificazione/dataset2_train.csv")  # train originale
df_test = pd.read_csv("classificazione/dataset2_test.csv")         # test invariato

X_train_orig = df_train_orig.drop(columns=['stile_guida'])
y_train_orig = df_train_orig['stile_guida']

X_test = df_test.drop(columns=['stile_guida'])
y_test = df_test['stile_guida']

# -----------------------------
# 2. Augmentation sul train
# -----------------------------
X_train_aug = pd.read_csv("classificazione/X_train_augmented.csv")
y_train_aug = pd.read_csv("classificazione/y_train_augmented.csv").squeeze()

# -----------------------------
# 3. Scaling
# -----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_aug)
X_test_scaled = scaler.transform(X_test)

# -----------------------------
# 4. Creazione modello Random Forest
# -----------------------------
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=3,
    min_samples_split=8,
    min_samples_leaf=5,
    max_features='sqrt',
    random_state=42,
    class_weight='balanced',
    n_jobs=1
)

# -----------------------------
# 5. Cross-validation sul train aumentato
# -----------------------------
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(rf, X_train_scaled, y_train_aug, cv=cv, scoring='accuracy', n_jobs=1)
print(f"CV Accuracy media (train aumentato): {cv_scores.mean():.4f}")
print(f"CV Accuracy std: {cv_scores.std():.4f}")

# -----------------------------
# 6. Fit finale sul train aumentato
# -----------------------------
rf.fit(X_train_scaled, y_train_aug)

# -----------------------------
# 7. Predizioni
# -----------------------------
y_train_pred_aug = rf.predict(X_train_scaled)  # train aumentato
y_train_pred_orig = rf.predict(scaler.transform(X_train_orig))  # train originale
y_test_pred = rf.predict(X_test_scaled)  # test invariato

# -----------------------------
# 11. Salvataggio modello e scaler
# -----------------------------
joblib.dump(rf, 'random_forest_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
