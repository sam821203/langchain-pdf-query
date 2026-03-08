import { ref, computed } from "vue";
import {
  analyzePDFFile,
  resetDocument,
  getApiErrorMessage,
  getUploadConfig,
  getApiBaseUrl,
} from "../services/apiService";
import { useLoading } from "vue-loading-overlay";

/** Fallback when backend config not yet loaded; must match backend default MAX_UPLOAD_SIZE_MB (50). */
const DEFAULT_MAX_UPLOAD_MB = 50;

const loadingConfig = {
  color: "#e74c3c",
  loader: "dots",
  backgroundColor: "#000000",
  width: 56,
  height: 56,
  opacity: 0.75,
  zIndex: 999,
};

export function usePdfUpload(onLocalClear = () => {}) {
  const selectedFile = ref(null);
  const uploadStatus = ref("請先上傳 PDF");
  const isPDFUploaded = ref(false);
  const currentDocumentId = ref(null);
  const pdfObjectUrl = ref(null);
  const fileInput = ref(null);
  const pdfPreviewRef = ref(null);
  const $loading = useLoading();

  // 與後端 MAX_UPLOAD_SIZE_MB 一致：由 /config 取得，未取得前用預設
  const maxUploadSizeMb = ref(DEFAULT_MAX_UPLOAD_MB);
  const maxUploadBytes = computed(() =>
    Math.floor(maxUploadSizeMb.value * 1024 * 1024)
  );

  getUploadConfig()
    .then((data) => {
      if (typeof data?.max_upload_size_mb === "number" && data.max_upload_size_mb > 0) {
        maxUploadSizeMb.value = data.max_upload_size_mb;
      }
    })
    .catch(() => {});

  // On page unload (refresh, close tab, navigate away), clear backend state via sendBeacon
  const handlePageUnload = () => {
    const docId = currentDocumentId.value;
    if (docId && typeof navigator.sendBeacon === "function") {
      const url = `${getApiBaseUrl()}/reset`;
      const body = new Blob(
        [JSON.stringify({ document_id: docId })],
        { type: "application/json" }
      );
      navigator.sendBeacon(url, body);
    }
  };
  window.addEventListener("pagehide", handlePageUnload);
  window.addEventListener("beforeunload", handlePageUnload);

  const triggerFileUpload = () => {
    fileInput.value?.click();
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    if (file.size > maxUploadBytes.value) {
      event.target.value = "";
      const mb = Math.floor(maxUploadSizeMb.value);
      uploadStatus.value = `檔案過大，最大允許 ${mb} MB，請縮小後再上傳`;
      selectedFile.value = null;
      return;
    }
    selectedFile.value = file;
    uploadStatus.value = `已選擇 ${file.name}，請點擊「分析 PDF」`;
  };

  const analyzePDF = async () => {
    if (!selectedFile.value) return;
    uploadStatus.value = "分析中…";
    const loader = $loading.show(loadingConfig);
    try {
      const response = await analyzePDFFile(selectedFile.value);
      const previousDocId = currentDocumentId.value;
      if (previousDocId) {
        try {
          await resetDocument(previousDocId);
        } catch (err) {
          console.error("清除前一次檔案失敗", err);
        }
      }
      currentDocumentId.value = response.data?.document_id ?? null;
      if (pdfObjectUrl.value) {
        URL.revokeObjectURL(pdfObjectUrl.value);
      }
      pdfObjectUrl.value = URL.createObjectURL(selectedFile.value);
      uploadStatus.value = "分析完成，可以開始提問";
      isPDFUploaded.value = true;
    } catch (error) {
      console.error("PDF upload failed", error);
      uploadStatus.value = getApiErrorMessage(error, "upload");
    } finally {
      loader.hide();
    }
  };

  const removePDF = async () => {
    const docId = currentDocumentId.value;
    if (pdfObjectUrl.value) {
      URL.revokeObjectURL(pdfObjectUrl.value);
      pdfObjectUrl.value = null;
    }
    selectedFile.value = null;
    currentDocumentId.value = null;
    isPDFUploaded.value = false;
    uploadStatus.value = "請先上傳 PDF";
    if (fileInput.value) fileInput.value.value = "";
    if (docId) {
      try {
        await resetDocument(docId);
      } catch (err) {
        console.error("後端重置失敗", err);
      }
    }
    onLocalClear();
  };

  return {
    selectedFile,
    uploadStatus,
    isPDFUploaded,
    currentDocumentId,
    pdfObjectUrl,
    fileInput,
    pdfPreviewRef,
    maxUploadSizeMb,
    triggerFileUpload,
    handleFileUpload,
    analyzePDF,
    removePDF,
  };
}
