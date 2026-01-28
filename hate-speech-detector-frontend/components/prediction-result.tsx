"use client";

import { useState } from "react";
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  Flag,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { FeedbackModal } from "@/components/feedback-modal";
import type { PredictionResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

interface PredictionResultProps {
  result: PredictionResponse;
  originalText: string;
}

const getLabelConfig = (label: string) => {
  const normalized = label.toLowerCase()

  switch (normalized) {
    case "hate":
      return {
        icon: XCircle,
        color: "text-destructive",
        bgColor: "bg-destructive/10",
        borderColor: "border-destructive/30",
        progressColor: "bg-destructive",
      }

    case "offensive":
      return {
        icon: AlertTriangle,
        color: "text-warning",
        bgColor: "bg-warning/10",
        borderColor: "border-warning/30",
        progressColor: "bg-warning",
      }

    case "not_hate":
    case "normal":
      return {
        icon: CheckCircle,
        color: "text-success",
        bgColor: "bg-success/10",
        borderColor: "border-success/30",
        progressColor: "bg-success",
      }

    default:
      return {
        icon: CheckCircle,
        color: "text-muted-foreground",
        bgColor: "bg-muted/10",
        borderColor: "border-muted",
        progressColor: "bg-muted",
      }
  }
}

export function PredictionResult({
  result,
  originalText,
}: PredictionResultProps) {
  const [showProbabilities, setShowProbabilities] = useState(false);
  const [feedbackOpen, setFeedbackOpen] = useState(false);

  const config = getLabelConfig(result.label);
  const Icon = config.icon;
  const confidencePercent = Math.round(result.confidence * 100);

  return (
    <>
      <Card className={cn("border-2", config.borderColor)}>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Icon className={cn("h-5 w-5", config.color)} />
            Classification Result
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Main Result */}
          <div
            className={cn(
              "flex flex-col items-center gap-4 rounded-lg p-6",
              config.bgColor
            )}
          >
            <span
              className={cn(
                "text-2xl font-bold tracking-tight md:text-3xl",
                config.color
              )}
            >
              {result.label}
            </span>

            <div className="w-full max-w-xs space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Confidence</span>
                <span className="font-medium">{confidencePercent}%</span>
              </div>
              <Progress
                value={confidencePercent}
                className={cn("h-2", config.progressColor)}
              />
            </div>
          </div>

          {/* Raw Probabilities */}
          {result.probabilities &&
            Object.keys(result.probabilities).length > 0 && (
              <Collapsible
                open={showProbabilities}
                onOpenChange={setShowProbabilities}
              >
                <CollapsibleTrigger asChild>
                  <Button
                    variant="ghost"
                    className="w-full justify-between text-muted-foreground"
                  >
                    Raw Probabilities
                    {showProbabilities ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="space-y-3 pt-2">
                  {Object.entries(result.probabilities).map(([label, prob]) => {
                    const probPercent = Math.round((prob as number) * 100);
                    const labelConfig = getLabelConfig(label);
                    return (
                      <div key={label} className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className={labelConfig.color}>{label}</span>
                          <span className="text-muted-foreground">
                            {probPercent}%
                          </span>
                        </div>
                        <Progress
                          value={probPercent}
                          className={cn("h-1.5", labelConfig.progressColor)}
                        />
                      </div>
                    );
                  })}
                </CollapsibleContent>
              </Collapsible>
            )}

          {/* Feedback Button */}
          <div className="border-t border-border pt-4">
            <Button
              variant="outline"
              onClick={() => setFeedbackOpen(true)}
              className="w-full"
            >
              <Flag className="mr-2 h-4 w-4" />
              Is this incorrect?
            </Button>
          </div>
        </CardContent>
      </Card>

      <FeedbackModal
        open={feedbackOpen}
        onOpenChange={setFeedbackOpen}
        originalText={originalText}
        predictedLabel={result.label}
        predictedConfidence={result.confidence}
      />
    </>
  );
}
