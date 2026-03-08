import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/** Base URL for backend API (e.g. for sendBeacon on page unload). */
export const getApiBaseUrl = () => API_BASE_URL;

// 上傳/查詢逾時（ms），逾時時會顯示 UI 提示
const api = axios.create({
  baseURL: API_BASE_URL, // 這是 FastAPI 伺服器地址
  timeout: 24000,
});

/** 後端 exception type → 顯示用中文訊息 */
const ERROR_TYPE_MESSAGES = {
  PDFParseError: "PDF 解析失敗，請確認檔案為有效 PDF。",
  OpenAITimeoutError: "查詢逾時，請稍後再試。",
  VectorStoreError: "向量儲存操作失敗。",
  NoPDFLoadedError: "尚未上傳 PDF。",
};

const DEFAULT_MESSAGES = {
  upload: "分析失敗，請重試",
  query: "查詢失敗，請稍後再試",
};

/**
 * Fetch upload config from backend so frontend limits match (e.g. max_upload_size_mb).
 * Used to keep upload size limit in sync with backend MAX_UPLOAD_SIZE_MB.
 * @returns {Promise<{ max_upload_size_mb: number }>}
 */
export const getUploadConfig = () => api.get("/config").then((res) => res.data);

const TIMEOUT_MESSAGES = {
  upload: "請求逾時（超過 12 秒），請檢查網路或稍後再試",
  query: "查詢逾時（超過 12 秒），請稍後再試",
};

/**
 * 依後端回傳的 detail / type 與 context 回傳對應中文錯誤訊息。
 * @param {unknown} error - axios 錯誤（含 response.data.detail, response.data.type）
 * @param {'upload'|'query'} context
 * @returns {string}
 */
export function getApiErrorMessage(error, context) {
  if (error?.code === "ECONNABORTED") {
    return TIMEOUT_MESSAGES[context];
  }
  const data = error?.response?.data;
  const detail = typeof data?.detail === "string" ? data.detail : null;
  if (detail) {
    return detail;
  }
  const type = data?.type;
  if (type && ERROR_TYPE_MESSAGES[type]) {
    return ERROR_TYPE_MESSAGES[type];
  }
  const status = error?.response?.status;
  if (status === 413) {
    return "檔案過大，請縮小後再上傳";
  }
  if (context === "query" && status === 404) {
    return "無效的 document_id 或文件已過期";
  }
  return DEFAULT_MESSAGES[context];
}

// 上傳 PDF
export const analyzePDFFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return api.post("/upload-pdf", formData);
};

/**
 * @param {string} question
 * @param {string} documentId
 * @returns {Promise<{ data: { answer: string, sources: { page: number, content: string }[] } }>}
 */
export const queryPDF = (question, documentId) => {
  return api.post("/query", { question, document_id: documentId });
};

/**
 * Reset backend state and delete uploaded PDF for the given document (frees memory).
 * @param {string} documentId
 * @returns {Promise}
 */
export const resetDocument = (documentId) => {
  return api.post("/reset", { document_id: documentId });
};
