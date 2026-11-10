import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import argparse
import random
from pathlib import Path
from typing import Dict, List
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import ImageFolder
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_recall_fscore_support, accuracy_score,
    top_k_accuracy_score
)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Import model architecture จากไฟล์หลัก
from importlib.machinery import SourceFileLoader
train_module = SourceFileLoader("train_module", "Multi-CUDA-Train.py").load_module()
CUDAOptimizedCNN = train_module.CUDAOptimizedCNN


def set_seed(seed: int = 42):
    """Set random seed for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_checkpoint(ckpt_path: str, device: torch.device):
    """Load model checkpoint"""
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    num_classes = ckpt['num_classes']
    img_size = ckpt['img_size']
    class_names = ckpt['class_names']

    model = CUDAOptimizedCNN(num_classes=num_classes, img_size=img_size).to(device)
    model.load_state_dict(ckpt['model_state_dict'])
    model.eval()
    return model, class_names, img_size, ckpt


def build_test_loader(data_path: str, img_size: int, class_names: List[str], batch_size: int = 64):
    """Build test data loader with correct class mapping & folder filtering"""
    # Transform ต้องตรงกับ train (val_test_transform จาก Multi-CUDA-Train.py)
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size), interpolation=transforms.InterpolationMode.BILINEAR),
        transforms.CenterCrop(img_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    
    root = Path(data_path)
    test_dir = root / 'test'
    if not test_dir.exists():
        test_dir = root / 'val' if (root / 'val').exists() else root
    
    ds = ImageFolder(str(test_dir), transform=transform)
    
    # สร้าง mapping จาก class name ไปยัง index ตาม checkpoint
    class_to_idx_ckpt = {name: idx for idx, name in enumerate(class_names)}
    
    # ✅ Filter เฉพาะ samples ที่ folder name อยู่ใน class_to_idx_ckpt
    valid_samples = []
    skipped_folders = []
    for path, _ in ds.samples:
        folder_name = Path(path).parent.name
        if folder_name in class_to_idx_ckpt:
            valid_samples.append((path, class_to_idx_ckpt[folder_name]))
        else:
            skipped_folders.append(folder_name)
    
    # แจ้งเตือน folder ที่ถูก skip
    if skipped_folders:
        unique_skipped = sorted(set(skipped_folders))
        print(f"\n⚠️  WARNING: Skipped {len(skipped_folders)} samples from folders not in checkpoint classes:")
        print(f"   Missing folders: {unique_skipped}")
        print(f"   Checkpoint classes ({len(class_names)}): {class_names}\n")
    
    if not valid_samples:
        test_folders = sorted(set(Path(p).parent.name for p, _ in ds.samples))
        raise ValueError(
            f"No valid samples found! Test folder structure doesn't match checkpoint.\n"
            f"Checkpoint classes: {class_names}\n"
            f"Test folders: {test_folders}"
        )
    
    # อัปเดต dataset attributes
    ds.samples = valid_samples
    ds.imgs = valid_samples  # compatibility กับ torchvision version เก่า
    ds.targets = [idx for _, idx in valid_samples]
    ds.class_to_idx = class_to_idx_ckpt
    ds.classes = class_names
    
    loader = DataLoader(
        ds, 
        batch_size=batch_size, 
        shuffle=False, 
        num_workers=4, 
        pin_memory=True
    )
    return loader, ds


@torch.no_grad()
def run_inference(model, loader, device):
    """Run model inference on test set"""
    all_preds, all_labels, all_probs = [], [], []
    
    for imgs, lbls in loader:
        imgs = imgs.to(device, non_blocking=True)
        out = model(imgs)
        probs = F.softmax(out, dim=1)
        _, pred = out.max(1)
        
        all_preds.append(pred.cpu())
        all_labels.append(lbls)
        all_probs.append(probs.cpu())
    
    return torch.cat(all_preds), torch.cat(all_labels), torch.cat(all_probs)


def compute_metrics(preds, labels, probs, class_names):
    """Compute all evaluation metrics"""
    p, r, f1, _ = precision_recall_fscore_support(
        labels, preds, average='weighted', zero_division=0
    )
    acc = accuracy_score(labels, preds)
    top5 = top_k_accuracy_score(
        labels, probs.numpy(), 
        k=min(5, len(class_names))
    ) if len(class_names) >= 5 else acc
    
    cm = confusion_matrix(labels, preds)
    rpt = classification_report(
        labels, preds, 
        target_names=class_names, 
        output_dict=True, 
        zero_division=0
    )
    
    return {
        'acc': acc, 
        'prec': p, 
        'rec': r, 
        'f1': f1, 
        'top5': top5, 
        'cm': cm, 
        'report': rpt
    }


def plot_all(preds, labels, probs, class_names, metrics, ts: str):
    """Generate all evaluation plots"""
    Path("plots").mkdir(exist_ok=True)

    # 1) Confusion Matrix
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        metrics['cm'], annot=True, fmt='d', cmap='Blues',
        xticklabels=class_names, yticklabels=class_names, ax=ax
    )
    ax.set(title='Confusion Matrix', xlabel='Predicted', ylabel='True')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'plots/cm_{ts}.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 2) Per-class F1
    classes = [k for k in metrics['report'] if k not in ('accuracy', 'macro avg', 'weighted avg')]
    f1s = [metrics['report'][c]['f1-score'] for c in classes]
    fig, ax = plt.subplots(figsize=(10, max(4, len(classes) * 0.4)))
    bars = ax.barh(classes, f1s, color='steelblue')
    ax.set(xlim=(0, 1), xlabel='F1-Score', title='Per-Class F1-Score')
    for b, v in zip(bars, f1s):
        ax.text(v + 0.01, b.get_y() + b.get_height() / 2, f'{v:.3f}', va='center')
    plt.tight_layout()
    plt.savefig(f'plots/per_class_f1_{ts}.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 3) Prediction confidence distribution
    conf = probs.max(dim=1).values.numpy()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(conf, bins=30, color='teal', edgecolor='black', alpha=0.8)
    ax.axvline(conf.mean(), color='r', ls='--', label=f'Mean={conf.mean():.3f}')
    ax.set(xlabel='Max Softmax Probability', ylabel='Count', title='Prediction Confidence Distribution')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'plots/conf_dist_{ts}.png', dpi=150, bbox_inches='tight')
    plt.close()

    # 4) Wrong predictions by class
    wrong = (preds != labels).numpy()
    wrong_per_cls = [wrong[labels.numpy() == i].sum() for i in range(len(class_names))]
    fig, ax = plt.subplots(figsize=(10, max(4, len(classes) * 0.4)))
    ax.barh(class_names, wrong_per_cls, color='salmon')
    ax.set(xlabel='Number of Wrong Predictions', title='Misclassified Samples per Class')
    for i, v in enumerate(wrong_per_cls):
        ax.text(v + 0.1, i, str(v), va='center')
    plt.tight_layout()
    plt.savefig(f'plots/wrong_per_class_{ts}.png', dpi=150, bbox_inches='tight')
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--checkpoint', type=str, default='best_model.pt')
    ap.add_argument('--data_path', type=str, default='Dataset')
    ap.add_argument('--batch_size', type=int, default=384)
    args = ap.parse_args()

    set_seed()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[INFO] Device: {device}")

    print(f"[INFO] Loading checkpoint: {args.checkpoint}")
    model, class_names, img_size, ckpt = load_checkpoint(args.checkpoint, device)
    print(f"  Classes: {len(class_names)} | Img size: {img_size}")
    print(f"  Best val_acc (from ckpt): {ckpt.get('best_val_acc', 'N/A')}")

    print(f"[INFO] Loading test data from: {args.data_path}")
    loader, ds = build_test_loader(args.data_path, img_size, class_names, args.batch_size)
    print(f"  Test samples (after filter): {len(ds):,}")

    print("[INFO] Running inference...")
    preds, labels, probs = run_inference(model, loader, device)
    metrics = compute_metrics(preds, labels, probs, class_names)

    ts = ckpt.get('timestamp', 'eval')
    print("\n" + "=" * 60)
    print(f" TEST RESULTS  (checkpoint: {Path(args.checkpoint).name})")
    print("=" * 60)
    print(f"  Samples   : {len(ds):,}")
    print(f"  Accuracy  : {metrics['acc']:.4f}  ({metrics['acc'] * 100:.2f}%)")
    print(f"  Top-5 Acc : {metrics['top5']:.4f}")
    print(f"  Precision : {metrics['prec']:.4f}")
    print(f"  Recall    : {metrics['rec']:.4f}")
    print(f"  F1-Score  : {metrics['f1']:.4f}")
    print("=" * 60)
    print("\nPer-class report:")
    print(classification_report(labels, preds, target_names=class_names, zero_division=0))

    print("[INFO] Plotting graphs...")
    plot_all(preds, labels, probs, class_names, metrics, ts)
    print("[OK] Saved →")
    for p in sorted(Path("plots").glob(f"*_{ts}.png")):
        print(f"   • {p}")


if __name__ == '__main__':
    main()
