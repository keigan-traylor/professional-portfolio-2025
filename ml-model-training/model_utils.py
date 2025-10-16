# model_utils.py - helpers for saving experiments and plotting evaluation curves
from pathlib import Path
import json, matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, precision_recall_curve

def save_experiment(metrics: dict, path):
    Path(path).write_text(json.dumps(metrics, indent=2))

def evaluate_model(y_true, y_score, outpath):
    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)
    precision, recall, _ = precision_recall_curve(y_true, y_score)
    pr_auc = auc(recall, precision)
    fig, ax = plt.subplots(1,2, figsize=(10,4))
    ax[0].plot(fpr, tpr, label=f'AUC={roc_auc:.3f}'); ax[0].set_title('ROC Curve'); ax[0].legend()
    ax[1].plot(recall, precision, label=f'PR AUC={pr_auc:.3f}'); ax[1].set_title('Precision-Recall'); ax[1].legend()
    fig.tight_layout(); fig.savefig(outpath)
