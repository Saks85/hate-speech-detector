import React, { useState } from "react";
import api from "../api/client";

export default function Analyzer() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCorrection, setShowCorrection] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const analyzeText = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.post("/api/v1/predict/", { text });

      setResult(res.data);
    } catch (err) {
      setError("Failed to analyze text");
    } finally {
      setLoading(false);
    }
  };
  const submitFeedback = async (correctLabel) => {
  try {
    await api.post("/api/v1/feedback/", {
      text,
      predicted_label: result.label,
      correct_label: correctLabel,
      predicted_confidence: result.confidence,
      model_version: "v2",
    });

    setFeedbackSent(true);
    setShowCorrection(false);
  } catch (err) {
    console.error("Feedback submission failed");
  }
};

  return (
    <div className="min-h-screen bg-bg p-6">
      <div className="max-w-3xl mx-auto bg-card p-6 rounded-xl shadow-lg">
        <h1 className="text-2xl font-bold mb-4">Analyze Text</h1>

        <textarea
          rows={6}
          className="w-full p-4 rounded-lg bg-bg border border-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-accent"
          placeholder="Paste text to analyze..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <button
          onClick={analyzeText}
          disabled={loading}
          className="mt-4 w-full bg-accent py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        {error && (
          <p className="mt-4 text-danger text-sm">{error}</p>
        )}

        {result && (
        <div className="mt-6 p-4 bg-bg rounded-lg border border-gray-700">
            <p>
                <span className="font-semibold">Prediction:</span>{" "}
                <span className="capitalize">{result.label}</span>
            </p>
            <p>
                <span className="font-semibold">Confidence:</span>{" "}
                {(result.confidence * 100).toFixed(2)}%
            </p>

        <div className="mt-4">
        <p className="mb-2 font-semibold">Is this prediction correct?</p>

        <div className="flex gap-3">
            <button
                onClick={() => submitFeedback(result.label)}
                className="bg-success px-4 py-2 rounded-lg font-semibold"
            >
            Yes
            </button>

        <button
          onClick={() => setShowCorrection(true)}
          className="bg-danger px-4 py-2 rounded-lg font-semibold"
        >
          No
        </button>
      </div>
    </div>

    {showCorrection && (
      <div className="mt-4">
        <p className="mb-2">Select correct label:</p>
        {["hate", "offensive", "normal"].map((lbl) => (
          <button
            key={lbl}
            onClick={() => submitFeedback(lbl)}
            className="mr-2 bg-warning px-3 py-1 rounded-lg"
          >
            {lbl}
          </button>
        ))}
      </div>
    )}

    {feedbackSent && (
      <p className="mt-4 text-success text-sm">
        Feedback recorded ✔
      </p>
    )}
  </div>
)}
      </div>
    </div>
  );
}
