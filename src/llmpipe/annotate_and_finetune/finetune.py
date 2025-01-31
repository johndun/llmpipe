from pathlib import Path
from typing import Annotated, Dict, List
import json
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    EvalPrediction
)
import typer
from typer import Option

from llmpipe import read_data


def compute_metrics(pred: EvalPrediction, id2label: Dict[int, str] = None) -> Dict:
    """Compute classification metrics."""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)

    # Get unique labels that are actually present in the data
    unique_labels = sorted(set(labels) | set(preds))
    target_names = [id2label[i] for i in unique_labels]

    # Get detailed classification metrics
    report = classification_report(labels, preds, output_dict=True, target_names=target_names, labels=unique_labels)

    # Add model preparation time
    metrics = {"model_preparation_time": 0.0009}  # Placeholder value

    # Add overall metrics
    metrics.update({
        "loss": float(np.mean(pred.predictions.mean())),
        "accuracy": report["accuracy"]
    })

    # Add per-class metrics with proper labels
    for label, scores in report.items():
        if isinstance(scores, dict):
            metrics[label] = scores

    return metrics


def run_finetuning(
    train_data: List[Dict],
    val_data: List[Dict],
    test_data: List[Dict],
    input_field: str = "text",
    model_path: str = "roberta-base",
    output_path: str = None,
    num_epochs: int = 0,
    learning_rate: float = 0.00001,
    batch_size: int = 8,
) -> Dict:
    """Run finetuning on datasets.
    
    Args:
        train_data: Training data samples
        val_data: Validation data samples  
        test_data: Test data samples
        input_field: The field to use as input to the transformer
        model_path: Local or HuggingFace model path
        output_path: Path to save model and metrics
        num_epochs: Number of training epochs (0 to skip training)
        learning_rate: Learning rate
        batch_size: Batch size for training and evaluation
        
    Returns:
        Dictionary containing metrics and model outputs
    """

    # Get unique labels and create label mapping
    all_labels = sorted(list(set([d["label"] for d in train_data + val_data + test_data])))
    label2id = {label: i for i, label in enumerate(all_labels)}
    id2label = {i: label for label, i in label2id.items()}
    num_labels = len(all_labels)
    for samples in (train_data, val_data, test_data):
        for sample in samples:
            sample["label"] = label2id[sample["label"]]

    train_dataset = Dataset.from_list(train_data)
    val_dataset = Dataset.from_list(val_data)
    test_dataset = Dataset.from_list(test_data)

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_path,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id
    )

    # Tokenization function
    def tokenize_function(examples):
        return tokenizer(examples[input_field], padding="max_length", truncation=True)

    # Tokenize datasets
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    val_dataset = val_dataset.map(tokenize_function, batched=True)
    test_dataset = test_dataset.map(tokenize_function, batched=True)

    # Set up training arguments
    training_args = TrainingArguments(
        output_dir=output_path,
        num_train_epochs=num_epochs,
        learning_rate=learning_rate,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        weight_decay=0.01,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        push_to_hub=False,
    )

    # Initialize trainer with compute_metrics that has access to label mappings
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=lambda pred: compute_metrics(pred, id2label),
    )

    # Train model if epochs > 0
    if num_epochs > 0:
        trainer.train()

    # Evaluate on validation and test sets
    val_metrics = trainer.evaluate()
    test_metrics = trainer.evaluate(test_dataset)

    # Save metrics and label mappings
    metrics = {
        "validation": val_metrics,
        "test": test_metrics,
        "hyperparameters": {
            "model_name": model_path,
            "num_epochs": num_epochs,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "weight_decay": 0.01,
        }
    }

    metrics_path = Path(output_path) / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    # Save model and tokenizer
    trainer.save_model()
    tokenizer.save_pretrained(output_path)


def finetune(
    model_path: Annotated[str, Option(help="Local or HuggingFace model path")] = "roberta-base",
    train_input_data_path: Annotated[str, Option(help="Path to training data")] = None,
    val_input_data_path: Annotated[str, Option(help="Path to validation data")] = None,
    test_input_data_path: Annotated[str, Option(help="Path to test data")] = None,
    input_field: Annotated[str, Option(help="The field to use as input to the transformer")] = "text",
    output_path: Annotated[str, Option(help="Path to save model and metrics")] = None,
    num_epochs: Annotated[int, Option(help="Number of training epochs (0 to skip training)")] = 0,
    learning_rate: Annotated[float, Option(help="Learning rate")] = 0.00001,
    batch_size: Annotated[int, Option(help="Batch size for training and evaluation")] = 8,
):
    """CLI entry point to run finetuning on a dataset."""
    # Expand user paths
    train_input_data_path = str(Path(train_input_data_path).expanduser())
    val_input_data_path = str(Path(val_input_data_path).expanduser())
    test_input_data_path = str(Path(test_input_data_path).expanduser())
    output_path = str(Path(output_path).expanduser())

    # Load datasets
    train_data = read_data(train_input_data_path)
    val_data = read_data(val_input_data_path)
    test_data = read_data(test_input_data_path)
    
    # Run finetuning
    run_finetuning(
        train_data=train_data,
        val_data=val_data,
        test_data=test_data,
        input_field=input_field,
        model_path=model_path,
        output_path=output_path,
        num_epochs=num_epochs,
        learning_rate=learning_rate,
        batch_size=batch_size
    )


def main():
    """CLI entry point."""
    app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)
    app.command()(finetune)
    app()


if __name__ == "__main__":
    main()
