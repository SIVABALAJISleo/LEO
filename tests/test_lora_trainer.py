"""Smoke test: real training must reduce loss. No mocks allowed."""
import tempfile
from backend.training.lora_trainer import LoRATrainer

PAIRS = [
    ("What is LEO AI?", "LEO is a local-first AI that runs on your own laptop iGPU."),
    ("Does LEO need the cloud?", "No. LEO answers offline, privately, at zero cost per query."),
    ("What is the crystallizer?", "A semantic cache that answers repeat questions in 20 ms with zero FLOPs."),
    ("How does LEO train?", "On-device LoRA adapters — under 1 MB, trained in seconds on CPU."),
]

def test_training_reduces_loss():
    trainer = LoRATrainer()
    with tempfile.TemporaryDirectory() as d:
        m = trainer.train(PAIRS, output_dir=d, epochs=4)
        assert m["loss_last"] < m["loss_first"], "training must reduce loss"
        assert m["trainable_pct"] < 1.0, "LoRA must train <1% of params"
        assert m["adapter_size_kb"] < 2048, "adapter must stay tiny"
