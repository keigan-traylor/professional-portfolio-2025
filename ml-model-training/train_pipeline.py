# train_pipeline.py - advanced ML training pipeline (synthetic data)
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, RandomizedSearchCV, train_test_split
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc
from sklearn.preprocessing import StandardScaler
import joblib
import matplotlib.pyplot as plt
from model_utils import save_experiment, evaluate_model

OUT = Path('artifacts'); OUT.mkdir(exist_ok=True)
DATA = Path('sample_data'); DATA.mkdir(exist_ok=True)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def synthesize_data(n=3000):
    X_num = np.random.randn(n, 6)
    X_num = np.hstack([X_num, (X_num[:,0]*X_num[:,1]).reshape(-1,1), (np.square(X_num[:,2])).reshape(-1,1)])
    cat = np.random.choice([0,1,2], size=(n,1), p=[0.6,0.3,0.1])
    df = pd.DataFrame(X_num, columns=[f'num_{i}' for i in range(X_num.shape[1])])
    df['cat'] = cat
    logits = 0.3*df['num_0'] - 0.2*df['num_1'] + 0.5*(df['cat']==1) + 0.1*np.random.randn(n)
    probs = 1/(1+np.exp(-logits))
    y = (probs > 0.7).astype(int)
    df['target'] = y
    return df

def build_pipeline(df):
    X = df.drop(columns=['target'])
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_SEED)
    scaler = StandardScaler()
    num_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    X_train_scaled = scaler.fit_transform(X_train[num_cols])
    X_test_scaled = scaler.transform(X_test[num_cols])
    X_train_proc = pd.DataFrame(X_train_scaled, index=X_train.index, columns=num_cols)
    X_test_proc = pd.DataFrame(X_test_scaled, index=X_test.index, columns=num_cols)
    if 'cat' in X_train.columns:
        X_train_proc['cat'] = X_train['cat'].values
        X_test_proc['cat'] = X_test['cat'].values
    return X_train_proc, X_test_proc, y_train, y_test, scaler

def train_and_tune(X_train, y_train):
    clf = RandomForestClassifier(random_state=RANDOM_SEED, n_jobs=-1)
    param_dist = {'n_estimators': [100,200], 'max_depth': [5,10,None], 'min_samples_split': [2,5]}
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_SEED)
    search = RandomizedSearchCV(clf, param_distributions=param_dist, n_iter=5, scoring='roc_auc', cv=cv, random_state=RANDOM_SEED, n_jobs=-1)
    search.fit(X_train, y_train)
    return search.best_estimator_, search.cv_results_

def main():
    df = synthesize_data()
    df.to_csv(DATA/'synthetic.csv', index=False)
    X_train, X_test, y_train, y_test, scaler = build_pipeline(df)
    model, cv_results = train_and_tune(X_train, y_train)
    y_pred_proba = model.predict_proba(X_test)[:,1]
    roc = roc_auc_score(y_test, y_pred_proba)
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    pr_auc = auc(recall, precision)
    joblib.dump(model, OUT/'model.pkl')
    joblib.dump(scaler, OUT/'scaler.pkl')
    save_experiment({'roc_auc':float(roc), 'pr_auc':float(pr_auc)}, OUT/'experiment.json')
    evaluate_model(y_test, y_pred_proba, OUT/'roc_pr_curve.png')
    print('Completed. Artifacts in', OUT)

if __name__ == '__main__':
    main()
