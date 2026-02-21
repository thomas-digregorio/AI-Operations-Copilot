from sklearn.metrics import classification_report, confusion_matrix, f1_score


def multiclass_metrics(y_true, y_pred, labels):
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "report": classification_report(
            y_true, y_pred, labels=labels, output_dict=True, zero_division=0
        ),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }
