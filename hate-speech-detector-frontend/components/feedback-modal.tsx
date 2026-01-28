"use client";

import { useState, useEffect } from "react";
import { Loader2, AlertCircle, CheckCircle2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { submitFeedback } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface FeedbackModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  originalText: string;
  predictedLabel: string;
  predictedConfidence: number;
}

type FeedbackStep = "confirm" | "provide-label";

const LABEL_OPTIONS = [
  { value: "Hate Speech", description: "Contains hateful content targeting groups or individuals" },
  { value: "Offensive", description: "Contains offensive language but not hateful" },
  { value: "Normal", description: "Contains no offensive or hateful content" },
];

export function FeedbackModal({
  open,
  onOpenChange,
  originalText,
  predictedLabel,
   predictedConfidence,
}: FeedbackModalProps) {
  const [step, setStep] = useState<FeedbackStep>("confirm");
  const [correctLabel, setCorrectLabel] = useState("");
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  // Reset state when modal opens/closes
  useEffect(() => {
    if (!open) {
      setStep("confirm");
      setCorrectLabel("");
      setNotes("");
    }
  }, [open]);

  const handleConfirmIncorrect = () => {
    setStep("provide-label");
  };

  const handleBack = () => {
    setStep("confirm");
    setCorrectLabel("");
  };

  const handleSubmit = async () => {
    if (!correctLabel) {
      toast({
        title: "Required Field",
        description: "Please select the correct label to continue",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await submitFeedback({
        text: originalText,
        predicted_label: predictedLabel,
        predicted_confidence: predictedConfidence,
        correct_label: correctLabel,
        notes: notes || undefined,
        model_version: "v2",
      });

      toast({
        title: "Feedback Submitted",
        description: "Thank you for helping improve our model!",
      });

      onOpenChange(false);
    } catch {
      toast({
        title: "Error",
        description: "Failed to submit feedback. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        {step === "confirm" ? (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-warning" />
                Report Incorrect Classification
              </DialogTitle>
              <DialogDescription>
                You are about to report that our model made an incorrect prediction.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label className="text-muted-foreground text-xs uppercase tracking-wide">
                  Analyzed Text
                </Label>
                <p className="rounded-md bg-secondary p-3 text-sm leading-relaxed">
                  {originalText.length > 200 ? `${originalText.slice(0, 200)}...` : originalText}
                </p>
              </div>

              <div className="rounded-lg border border-border bg-secondary/50 p-4">
                <Label className="text-muted-foreground text-xs uppercase tracking-wide">
                  Current Model Prediction
                </Label>
                <p className="mt-1 text-lg font-semibold">{predictedLabel}</p>
              </div>

              <div className="rounded-lg border border-warning/30 bg-warning/10 p-4">
                <p className="text-sm text-foreground">
                  <strong>Please confirm:</strong> Was this classification incorrect? 
                  If yes, you will be asked to provide the correct label in the next step.
                </p>
              </div>
            </div>

            <DialogFooter className="flex-col gap-2 sm:flex-row">
              <Button
                variant="outline"
                onClick={handleClose}
                className="w-full sm:w-auto bg-transparent"
              >
                Cancel
              </Button>
              <Button
                onClick={handleConfirmIncorrect}
                className="w-full sm:w-auto"
              >
                Yes, this is incorrect
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </DialogFooter>
          </>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-success" />
                Provide Correct Label
              </DialogTitle>
              <DialogDescription>
                Please select the correct classification for this text. This is required to submit your feedback.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="flex items-center justify-between rounded-lg border border-border bg-secondary/50 p-3">
                <div>
                  <Label className="text-muted-foreground text-xs uppercase tracking-wide">
                    Model Said
                  </Label>
                  <p className="mt-0.5 font-medium line-through opacity-60">{predictedLabel}</p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground" />
                <div className="text-right">
                  <Label className="text-muted-foreground text-xs uppercase tracking-wide">
                    Correct Label
                  </Label>
                  <p className="mt-0.5 font-medium text-success">
                    {correctLabel || "Select below"}
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="correct-label" className="flex items-center gap-1">
                  What should the correct label be?
                  <span className="text-destructive">*</span>
                </Label>
                <Select value={correctLabel} onValueChange={setCorrectLabel}>
                  <SelectTrigger 
                    id="correct-label" 
                    className={!correctLabel ? "border-destructive/50" : ""}
                  >
                    <SelectValue placeholder="Select the correct label (required)" />
                  </SelectTrigger>
                  <SelectContent>
                    {LABEL_OPTIONS.map((option) => (
                      <SelectItem 
                        key={option.value} 
                        value={option.value}
                        disabled={option.value === predictedLabel}
                      >
                        <div className="flex flex-col">
                          <span className="font-medium">{option.value}</span>
                          <span className="text-xs text-muted-foreground">
                            {option.description}
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {!correctLabel && (
                  <p className="text-xs text-destructive">
                    A correct label is required to submit feedback
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Additional Context (Optional)</Label>
                <Textarea
                  id="notes"
                  placeholder="Why do you think this is the correct label? Any additional context helps us improve..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                />
              </div>
            </div>

            <DialogFooter className="flex-col gap-2 sm:flex-row">
              <Button
                variant="ghost"
                onClick={handleBack}
                disabled={isSubmitting}
                className="w-full sm:w-auto"
              >
                Back
              </Button>
              <Button
                variant="outline"
                onClick={handleClose}
                disabled={isSubmitting}
                className="w-full sm:w-auto bg-transparent"
              >
                Cancel
              </Button>
              <Button 
                onClick={handleSubmit} 
                disabled={isSubmitting || !correctLabel}
                className="w-full sm:w-auto"
              >
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Submit Feedback
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
