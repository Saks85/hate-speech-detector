import React from "react";
import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center">
      <div className="bg-card p-10 rounded-2xl shadow-xl w-[420px] text-center">
        <h1 className="text-3xl font-bold mb-2">Hate Speech Detection System</h1>
        <p className="text-muted mb-6">
          AI-powered hate speech detection with human-in-the-loop learning
        </p>

        <button
          onClick={() => navigate("/analyze")}
          className="w-full bg-accent py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
        >
          Analyze Text
        </button>

        <button
          onClick={() => navigate("/admin")}
          className="w-full bg-accent py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
        >
          Admin Dashboard →
        </button>

        <p className="mt-6 text-xs text-muted">Model v2 (Local)</p>
      </div>
    </div>
  );
}
