import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL, // 這是 FastAPI 伺服器地址
  // timeout: 10000,
});

// 上傳 PDF
export const uploadPDFFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return api.post("/upload-pdf", formData);
};

export const queryPDF = (question) => {
  return api.post("/query", { question });
};
