import api from "./client";

export const fetchDashboardStats = async () => {
  const res = await api.get("/api/v1/dashboard/stats");
  return res.data;
};

export const fetchFeedbackList = async (limit = 200) => {
  const res = await api.get("/api/v1/dashboard/list", {
    params: { limit },
  });
  return res.data;
};

export const deleteFeedback = async (id) => {
  await api.delete(`/api/v1/dashboard/delete/${id}`);
};
export const triggerRetrain = async () => {
  const res = await api.post("/api/v1/retrain/");
  return res.data;
};

