import React, { useEffect, useState } from "react";
import { fetchDashboardStats, fetchFeedbackList } from "../api/dashboard";
import { deleteFeedback, triggerRetrain } from "../api/dashboard";
import FeedbackTable from "../components/FeedbackTable";



/* ---------------- Dashboard ---------------- */

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState("all");
  const [modelFilter, setModelFilter] = useState("all");
  const [retrainStatus, setRetrainStatus] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [s, r] = await Promise.all([
          fetchDashboardStats(),
          fetchFeedbackList(200),
        ]);
        setStats(s);
        setRows(r);
      } catch {
        console.error("Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filteredRows = rows.filter((r) => {
    const isError =
      r.correct_label && r.correct_label !== r.model_label;

    if (filterType === "correct" && isError) return false;
    if (filterType === "incorrect" && !isError) return false;
    if (modelFilter !== "all" && r.model_version !== modelFilter)
      return false;

    return true;
  });

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this feedback entry?")) return;
    await deleteFeedback(id);
    setRows((prev) => prev.filter((r) => r.id !== id));
  };

  const handleRetrain = async () => {
    if (
      !window.confirm(
        "This will start retraining using feedback data.\nContinue?"
      )
    )
      return;

    const res = await triggerRetrain();
    setRetrainStatus(
      `Retraining started. New model: ${res.new_version}`
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading dashboard...
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">

      <main className="flex-1 p-10">
        {/* Header */}
        <h1 className="text-3xl font-bold mb-1">Overview</h1>
        <p className="text-muted mb-6">
          Thursday, October 24, 2023
        </p>

        {/* Retrain */}
        <button
          onClick={handleRetrain}
          className="mb-4 bg-warning px-6 py-3 rounded-xl font-semibold shadow-lg"
        >
          Start Retraining
        </button>

        {retrainStatus && (
          <p className="mb-6 text-success">{retrainStatus}</p>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          <div className="bg-glass p-6 rounded-xl shadow-lg">
            <p className="text-muted text-sm mb-1">
              Total Feedback
            </p>
            <p className="text-3xl font-bold">
              {stats.total_feedback}
            </p>
          </div>

          <div className="bg-glass p-6 rounded-xl shadow-lg">
            <p className="text-muted text-sm mb-1">
              Model Errors
            </p>
            <p className="text-3xl font-bold text-danger">
              {stats.model_errors}
            </p>
          </div>

          <div className="bg-glass p-6 rounded-xl shadow-lg">
            <p className="text-muted text-sm mb-1">
              Overrides
            </p>
            <p className="text-3xl font-bold">
              {stats.overrides}
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-4 mb-4">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-glass px-4 py-2 rounded-lg"
          >
            <option value="all">All</option>
            <option value="correct">Correct</option>
            <option value="incorrect">Incorrect</option>
          </select>

          <select
            value={modelFilter}
            onChange={(e) => setModelFilter(e.target.value)}
            className="bg-glass px-4 py-2 rounded-lg"
          >
            <option value="all">All Models</option>
            {[...new Set(rows.map((r) => r.model_version))]
              .filter(Boolean)
              .map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
          </select>
        </div>

        {/* Table */}
        <FeedbackTable
          rows={filteredRows}
          onDelete={handleDelete}
        />
      </main>
    </div>
  );
}
