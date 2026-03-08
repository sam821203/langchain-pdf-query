<template>
  <div class="home-container">
    <h1 class="title">Smart PDF Query</h1>
    <h3 class="description">{{ uploadStatus }}</h3>

    <!-- 步驟一：上傳 PDF -->
    <div class="upload-section">
      <h4 class="step-title">1. 上傳 PDF</h4>
      <input
        type="file"
        ref="fileInput"
        @change="handleFileUpload"
        accept="application/pdf"
        class="file-input-hidden"
      />
      <div v-if="!selectedFile" class="upload-trigger" @click="triggerFileUpload">
        <font-awesome-icon icon="cloud-upload-alt" class="upload-trigger-icon" />
        <span>選擇 PDF 檔案</span>
      </div>
      <div v-else class="upload-selected">
        <span class="upload-filename">{{ selectedFile.name }}</span>
        <div class="upload-actions">
          <button
            type="button"
            class="btn-analyze"
            :disabled="isPDFUploaded"
            @click="analyzePDF"
          >
            分析 PDF
          </button>
          <button type="button" class="btn-clear" @click="removePDF">
            清除
          </button>
        </div>
      </div>
    </div>

    <!-- 步驟二：輸入問題 -->
    <div class="query-box">
      <h4 class="step-title">2. 輸入問題</h4>
      <textarea
        v-model="question"
        placeholder="輸入想問 PDF 的內容…"
        class="input-field textarea-field"
        :disabled="!isPDFUploaded"
        rows="6"
      ></textarea>
      <div class="query-button__wrapper">
        <button
          @click="queryAPI"
          class="query-button"
          :disabled="!isPDFUploaded || !question"
        >
          查詢
        </button>
      </div>
    </div>

    <!-- PDF 預覽區 -->
    <div
      v-if="isPDFUploaded && pdfObjectUrl"
      ref="pdfPreviewRef"
      class="pdf-preview-wrapper"
    >
      <h4 class="step-title">PDF 預覽</h4>
      <div class="pdf-preview-inner">
        <VuePdfEmbed :source="pdfObjectUrl" :page="currentPage" />
      </div>
    </div>

    <!-- 回答區 -->
    <div v-if="answer" class="answer-section">
      <AnswerContent :html="answerHtml" />
      <!-- 參考來源 -->
      <div v-if="sources.length > 0" class="sources-box">
        <h4 class="sources-title">參考來源</h4>
        <div class="sources-list">
          <button
            v-for="src in sources"
            :key="src.page"
            type="button"
            class="source-page-btn"
            @click="goToPage(src.page)"
          >
            頁 {{ src.page }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { marked } from "marked";
import DOMPurify from "dompurify";
import VuePdfEmbed from "vue-pdf-embed";
import { queryPDF, getApiErrorMessage } from "../services/apiService";
import { useLoading } from "vue-loading-overlay";
import AnswerContent from "../components/AnswerContent.vue";
import { usePdfUpload } from "../composables/usePdfUpload";

marked.use({ gfm: true });

const question = ref("");
const answer = ref("");
const answerHtml = computed(() =>
  DOMPurify.sanitize(marked.parse(answer.value || ""))
);
const sources = ref([]);
const currentPage = ref(1);

const {
  selectedFile,
  uploadStatus,
  isPDFUploaded,
  currentDocumentId,
  pdfObjectUrl,
  fileInput,
  pdfPreviewRef,
  triggerFileUpload,
  handleFileUpload,
  analyzePDF,
  removePDF,
} = usePdfUpload(() => {
  question.value = "";
  answer.value = "";
  sources.value = [];
});

const $loading = useLoading();
const loadingConfig = {
  color: "#e74c3c",
  loader: "dots",
  backgroundColor: "#000000",
  width: 56,
  height: 56,
  opacity: 0.75,
  zIndex: 999,
};

const queryAPI = async () => {
  if (!currentDocumentId.value) return;
  const loader = $loading.show(loadingConfig);
  try {
    const response = await queryPDF(question.value, currentDocumentId.value);
    answer.value = response.data.answer;
    sources.value = response.data.sources ?? [];
  } catch (error) {
    console.error("查詢失敗", error);
    answer.value = getApiErrorMessage(error, "query");
    sources.value = [];
  } finally {
    loader.hide();
  }
};

const goToPage = (page) => {
  currentPage.value = page;
  pdfPreviewRef.value?.scrollIntoView({ behavior: "smooth" });
};
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background:
    linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
    url("https://img.pikbest.com/back_our/20210415/bg/35f18e92435e3.png!w700wp")
      center/cover no-repeat;
  color: white;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 20px;
}

.description {
  font-size: 1.25rem;
  font-weight: 500;
  margin-bottom: 40px;
}

.step-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 12px;
  width: 100%;
}

.file-input-hidden {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  overflow: hidden;
}

.upload-section {
  width: 100%;
  max-width: 700px;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.upload-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.12);
  border: 2px dashed rgba(255, 255, 255, 0.4);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.upload-trigger:hover {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.6);
}

.upload-trigger-icon {
  font-size: 1.25rem;
}

.upload-selected {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.upload-filename {
  flex: 1;
  min-width: 0;
  font-size: 0.95rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-actions {
  display: flex;
  gap: 8px;
}

/* 按鈕統一高度 */
.btn-analyze,
.btn-clear,
.query-button,
.source-page-btn {
  min-height: 32px;
  padding: 6px 14px;
  font-size: 0.9rem;
  line-height: 1.25;
  box-sizing: border-box;
}

.btn-analyze {
  padding: 6px 20px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-analyze:hover:not(:disabled) {
  background-color: #c94334;
}

.btn-analyze:disabled {
  background-color: #d6bab8;
  cursor: not-allowed;
  user-select: none;
}

.btn-clear {
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-clear:hover {
  background: rgba(255, 255, 255, 0.3);
}

.query-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  max-width: 700px;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.input-field {
  display: block;
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-bottom: 4px;
}

.query-button__wrapper {
  display: flex;
  justify-content: flex-end;
}

.textarea-field {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  resize: none;
  outline: none;
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}

.textarea-field:focus {
  border-color: #e74c3c;
  box-shadow: 0 0 15px rgba(231, 76, 60, 0.5);
}

.textarea-field:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.query-button {
  padding: 6px 24px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.query-button:hover:not(:disabled) {
  background-color: #c94334;
}

.query-button:disabled {
  background-color: #d6bab8;
  cursor: not-allowed;
  user-select: none;
}

.pdf-preview-wrapper {
  width: 100%;
  max-width: 700px;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

.pdf-preview-inner {
  max-height: 60vh;
  overflow: auto;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
}

.pdf-preview-inner :deep(.vue-pdf-embed) {
  display: block;
}

.answer-section {
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sources-box {
  width: 100%;
  padding: 20px;
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.sources-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 12px;
}

.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.source-page-btn {
  padding: 6px 14px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.source-page-btn:hover {
  background-color: #c94334;
}
</style>
