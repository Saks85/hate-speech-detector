"use client";
import { useState } from "react";
import { triggerRetrain, ApiError } from "@/lib/api";

export function useRetrain() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [success, setSuccess] = useState(false);

  const retrain = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await triggerRetrain();
      setSuccess(true);
    } catch (err: any) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return { retrain, loading, error, success };
}
