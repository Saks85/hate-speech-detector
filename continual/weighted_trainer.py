import torch
from transformers import Trainer

class FeedbackWeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        # HF Trainer ALWAYS passes labels separately in inputs for training
        labels = inputs["labels"]

        # remove only non-model fields
        sample_weight = inputs.pop("sample_weight", None)

        outputs = model(**inputs)
        logits = outputs.logits

        loss_fct = torch.nn.CrossEntropyLoss(reduction="none")
        loss = loss_fct(logits, labels)

        if sample_weight is not None:
            loss = loss * sample_weight

        loss = loss.mean()
        return (loss, outputs) if return_outputs else loss
