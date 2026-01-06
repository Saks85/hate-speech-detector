import React from "react";

export default function FeedbackTable({ rows, onDelete }) {
  return (
    <div className="bg-glass rounded-xl overflow-hidden shadow-xl">
      <table className="w-full text-sm border border-gray-700">
        <thead className="bg-white/5 text-muted text-xs uppercase">
          <tr className="hover:bg-white/5 transition">
            <th className="p-2 border border-gray-700">Text</th>
            <th className="p-2 border border-gray-700">Predicted</th>
            <th className="p-2 border border-gray-700">Correct</th>
            <th className="p-2 border border-gray-700">Confidence</th>
            <th className="p-2 border border-gray-700">Model</th>
            <th className="p-2 border border-gray-700">Actions</th>

          </tr>
        </thead>
        <tbody>
          {rows.map((r) => {
            const isError =
              r.correct_label && r.correct_label !== r.model_label;

            return (
              <tr
                key={r.id}
                className={isError ? "bg-danger/20" : "bg-card"}
              >
                <td className="p-2 border border-gray-700 max-w-md truncate">
                  {r.text}
                </td>
                <td className="p-2 border border-gray-700">
                  {r.model_label}
                </td>
                <td className="p-2 border border-gray-700">
                  {r.correct_label || "✓"}
                </td>
                <td className="p-2 border border-gray-700">
                  {r.confidence !== null
                    ? `${(r.confidence * 100).toFixed(1)}%`
                    : "-"}
                </td>
                <td className="p-2 border border-gray-700">
                  {r.model_version}
                </td>
                <td className="p-2 border border-gray-700 text-center">
  <button
    onClick={() => onDelete(r.id)}
    className="text-danger hover:underline"
  >
    Delete
  </button>
</td>

              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
