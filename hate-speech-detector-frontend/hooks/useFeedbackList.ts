"use client";
import { useEffect, useState } from "react";
import {
  getFeedbackList,
  deleteFeedback,
  FeedbackItem,
  ApiError,
} from "@/lib/api";

export function useFeedbackList(limit = 200) {
  const [data, setData] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    getFeedbackList(limit)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [limit]);

  const removeFeedback = async (id: number) => {
    // optimistic update
    const previous = data;
    setData((prev) => prev.filter((item) => item.id !== id));

    try {
      await deleteFeedback(id);
    } catch (err) {
      // rollback on failure
      setData(previous);
      throw err;
    }
  };

  return { data, loading, error, removeFeedback };
}
