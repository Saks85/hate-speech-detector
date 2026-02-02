import axios, { AxiosError } from "axios";

/* ------------------ AXIOS INSTANCE ------------------ */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

/* ------------------ TYPES ------------------ */

export interface PredictionRequest {
  text: string;
  include_metadata?: boolean;
}

export interface PredictionResponse {
  label: string;
  confidence: number;
  probabilities?: Record<string, number>;
  preprocessing?: Record<string, unknown> | null;
  metadata_features?: Record<string, unknown> | null;
}

/* -------- Feedback -------- */

export interface FeedbackRequest {
  text: string;
  predicted_label: string;
  predicted_confidence: number;
  correct_label?: string | null;
  model_version?: string | null;
  notes?: string | null;
  preprocessing?: Record<string, unknown> | null;
  metadata_features?: Record<string, unknown> | null;
}

export interface FeedbackItem {
  id: number;
  text: string;
  model_label: string;
  correct_label: string | null;
  confidence: number;
  timestamp: string | null;
  model_version: string | null;
}

/* -------- Dashboard -------- */

export interface DashboardStats {
  total_feedback: number;
  model_errors: number;
  overrides: number;
}

/* -------- Error -------- */

export interface ApiError {
  message: string;
  status?: number;
}

/* ------------------ ERROR HANDLER ------------------ */

const handleApiError = (error: unknown): never => {
  if (error instanceof AxiosError) {
    const message =
      error.response?.data?.detail?.[0]?.msg ||
      error.response?.data?.detail ||
      error.message ||
      "Unexpected API error";

    throw {
      message,
      status: error.response?.status,
    } as ApiError;
  }

  throw { message: "Unexpected error occurred" } as ApiError;
};

/* ------------------ API FUNCTIONS ------------------ */

export const predictText = async (
  text: string,
  includeMetadata = true
): Promise<PredictionResponse> => {
  try {
    const res = await apiClient.post<PredictionResponse>("/predict/", {
      text,
      include_metadata: includeMetadata,
    });
    return res.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const submitFeedback = async (
  feedback: FeedbackRequest
): Promise<{ id: number }> => {
  try {
    const res = await apiClient.post("/feedback/", feedback);
    return res.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const getDashboardStats = async (): Promise<DashboardStats> => {
  try {
    const res = await apiClient.get<DashboardStats>("/dashboard/stats");
    return res.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const getFeedbackList = async (
  limit = 200
): Promise<FeedbackItem[]> => {
  try {
    const res = await apiClient.get<FeedbackItem[]>(
      `/dashboard/list?limit=${limit}`
    );
    return res.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const deleteFeedback = async (
  id: number
): Promise<{ success: boolean }> => {
  try {
    const res = await apiClient.delete(`/dashboard/delete/${id}`);
    return res.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export interface RetrainResponse {
  status: string;
  new_version: string;
}

export const triggerRetrain = async (): Promise<RetrainResponse> => {
  try {
    const res = await apiClient.post("/retrain/");
    return res.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export default apiClient;
