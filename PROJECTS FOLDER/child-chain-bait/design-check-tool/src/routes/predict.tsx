import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Page } from "@/components/Layout";
import { GaitInputForm } from "@/components/GaitInputForm";
import { PredictionResult } from "@/components/PredictionResult";
import {
  predictGait,
  saveStoredAssessment,
  type GaitInput,
  type PredictionResponse,
  type AssessmentRecord,
} from "@/services/api";

export const Route = createFileRoute("/predict")({
  head: () => ({
    meta: [
      { title: "Child Gait Assessment — Child Gait AI" },
      {
        name: "description",
        content:
          "Enter child gait biomechanical parameters to generate a machine learning prediction for Normal, Diplegic, or Hemiplegic classifications.",
      },
    ],
  }),
  component: PredictPage,
});

function PredictPage() {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<{
    res: PredictionResponse;
    input: GaitInput;
  } | null>(null);
  const [isSaved, setIsSaved] = useState(false);

  const handlePredict = async (input: GaitInput) => {
    setLoading(true);
    setErrorMessage(null);
    setResult(null);
    setIsSaved(false);

    try {
      // Call the API service layer
      const predictionResponse = await predictGait(input);
      setResult({ res: predictionResponse, input });
    } catch (err: unknown) {
      console.warn("Backend prediction call failed:", err);
      // Clean, non-technical user friendly error adhering to Section 14
      setErrorMessage(
        "Unable to complete the assessment. Please verify the Spring Boot backend server is running and try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAssessment = () => {
    if (!result) return;
    const record: AssessmentRecord = {
      id: result.res.assessmentId || `gait-${Date.now()}-${result.input.childId}`,
      date: new Date().toISOString(),
      childId: result.input.childId,
      age: result.input.age,
      gender: result.input.gender,
      heelPressure: result.input.heelPressure,
      toePressure: result.input.toePressure,
      tiltAngle: result.input.tiltAngle,
      stepDuration: result.input.stepDuration,
      strideLength: result.input.strideLength,
      walkingSpeed: result.input.walkingSpeed,
      prediction: result.res.prediction,
      confidence: result.res.confidence,
      recommendations: result.res.recommendations,
    };

    saveStoredAssessment(record);
    setIsSaved(true);
  };

  const handleReset = () => {
    setResult(null);
    setErrorMessage(null);
    setIsSaved(false);
  };

  return (
    <Page>
      <div className="mx-auto max-w-4xl space-y-8">
        {/* Page Header */}
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              Gait Prediction
            </h1>
            <p className="mt-1 text-xs sm:text-sm text-muted-foreground">
              Primary ML assessment module for pediatric gait biomechanics analysis.
            </p>
          </div>

          {result && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleReset}
              className="self-start gap-1.5 text-xs sm:self-auto"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              New Assessment
            </Button>
          )}
        </div>

        {/* Backend / Network Error State */}
        {errorMessage && (
          <div className="fade-in rounded-xl border border-destructive/30 bg-destructive/10 p-5 text-sm text-destructive shadow-xs">
            <div className="flex items-start gap-3">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
              <div>
                <h3 className="font-semibold text-foreground">Assessment Connection Notice</h3>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">{errorMessage}</p>
                <div className="mt-3 text-xs text-muted-foreground">
                  Expected service endpoint:{" "}
                  <code className="font-mono bg-muted px-1.5 py-0.5 rounded">
                    POST /api/predict
                  </code>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Core Form (Hidden when result is present to focus evaluator on output, or switchable) */}
        {!result ? (
          <GaitInputForm onSubmit={handlePredict} loading={loading} />
        ) : (
          <PredictionResult
            result={result.res}
            input={result.input}
            onSave={handleSaveAssessment}
            isSaved={isSaved}
          />
        )}
      </div>
    </Page>
  );
}
