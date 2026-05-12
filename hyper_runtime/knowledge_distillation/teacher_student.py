import numpy as np

class KnowledgeDistillationEngine:
    """
    Implements Teacher-Student progressive distillation pipelines.
    Moves intelligence into smaller, compute-efficient student systems.
    """
    def __init__(self, teacher_model, student_model):
        self.teacher = teacher_model
        self.student = student_model
        
    def distillation_step(self, x, temperature=2.0):
        """
        x: input tensor
        Performs consistency distillation utilizing soft targets.
        """
        teacher_logits = self.teacher.forward(x)
        soft_targets = np.exp(teacher_logits / temperature) / np.sum(np.exp(teacher_logits / temperature), axis=-1, keepdims=True)
        
        student_logits = self.student.forward(x)
        soft_preds = np.exp(student_logits / temperature) / np.sum(np.exp(student_logits / temperature), axis=-1, keepdims=True)
        
        loss = np.sum(soft_targets * (np.log(soft_targets + 1e-9) - np.log(soft_preds + 1e-9)), axis=-1)
        return loss
