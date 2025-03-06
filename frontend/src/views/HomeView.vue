<template>
  <div class="home-container">
    <h1 class="title">Smart PDF Query</h1>
    <h3 class="description">{{ uploadStatus }}</h3>
    <!-- Input Area -->
    <div class="input-area">
      <div class="input-wrapper">
        <!-- PDF Upload Circle (Hidden by Default) -->
        <div
          class="pdf-upload-circle"
          id="pdfUploadCircle"
          tabindex="0"
          aria-label="Uploaded PDF"
        >
          <font-awesome-icon icon="file-pdf" style="color: red" />
          <div class="delete-pdf" @click="removePDF">×</div>
        </div>

        <!-- Upload Icon -->
        <input
          type="file"
          ref="fileInput"
          @change="handleFileUpload"
          accept="application/pdf"
          style="display: none"
        />
        <div
          class="upload-icon-wrapper"
          aria-label="Upload File"
          tabindex="0"
          @click="triggerFileUpload"
        >
          <font-awesome-icon icon="cloud-upload-alt" class="upload-icon" />
        </div>

        <textarea
          id="messageInput"
          rows="1"
          placeholder="Analyze a PDF..."
          readonly
          class="mock-textarea"
        ></textarea>

        <!-- upload PDF -->
        <button
          class="send-button"
          @click="analyzePDF"
          :disabled="!selectedFile"
        >
          <font-awesome-icon icon="arrow-up" />
        </button>
      </div>
    </div>

    <!-- 查詢區 -->
    <div class="query-box">
      <textarea
        v-model="question"
        placeholder="請輸入問題"
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

    <!-- 回答區 -->
    <div v-if="answer" class="answer-box">{{ answer }}</div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { queryPDF, analyzePDFFile } from "../services/apiService";
import { useLoading } from "vue-loading-overlay";

const question = ref("");
const answer = ref("");
const selectedFile = ref(null);
const uploadStatus = ref("Upload PDF to get started!");
const isPDFUploaded = ref(false); // 確保 PDF 上傳後才能查詢
const fileInput = ref(null);
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

const triggerFileUpload = () => {
  // 觸發隱藏的 input 點擊事件
  fileInput.value.click();
};

// 處理選擇的檔案
const handleFileUpload = (event) => {
  selectedFile.value = event.target.files[0];
};

// 上傳 PDF
const analyzePDF = async () => {
  if (!selectedFile.value) return;
  uploadStatus.value = "Analyzing...";
  const loader = $loading.show(loadingConfig);
  try {
    await analyzePDFFile(selectedFile.value);
    uploadStatus.value =
      "✅ Successful! You can now ask any PDF-related questions~";
    isPDFUploaded.value = true;
  } catch (error) {
    console.error("PDF upload failed", error);
    uploadStatus.value = "❌ Analyze failed, please try again.";
  } finally {
    loader.hide();
  }
};

const removePDF = () => {
  selectedFile.value = null;
  isPDFUploaded.value = false;
  uploadStatus.value = "";
};

const queryAPI = async () => {
  try {
    const response = await queryPDF(question.value);
    answer.value = response.data.answer;
  } catch (error) {
    console.error("查詢失敗", error);
    answer.value = "查詢失敗，請稍後再試";
  }
};
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
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

.upload-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.upload-button {
  margin-top: 10px;
  padding: 10px 20px;
  font-size: 1rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.upload-button:disabled {
  background-color: #ccc;
}

.upload-status {
  margin-top: 5px;
  margin-bottom: 48px;
}

.query-box {
  gap: 10px;
  width: 100%;
  max-width: 700px;
  margin-bottom: 24px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.input-field {
  display: block;
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-bottom: 12px;
}

.query-button__wrapper {
  display: flex;
  justify-content: end;
}

.textarea-field {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px;
  font-size: 16px;
  resize: none;
  outline: none;
  transition:
    box-shadow 0.3s ease,
    color 0.3s ease;
}

.textarea-field:focus {
  border-color: #e74c3c;
  border-width: 1.5px;
  box-shadow: 0 0 15px rgba(231, 76, 60, 0.5);
}

.query-button {
  padding: 10px 32px;
  font-size: 1rem;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.query-button:hover {
  background-color: #c94334;
}

.query-button:disabled {
  background-color: #d6bab8;
  cursor: not-allowed;
  user-select: none;
}

.answer-box {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  text-align: center;
}

.input-area {
  width: 100%;
  max-width: 700px;
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
  position: relative;
}

.input-wrapper {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  border: 1px solid #d7d3d3;
  border-radius: 8px;
  width: 100%;
  background-color: #ffffff;
  position: relative;
}

textarea {
  flex-grow: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 10px;
  font-size: 1rem;
  resize: none;
  min-height: 40px;
  max-height: 120px;
  overflow-y: auto;
  transition: height 0.2s ease;
}

.upload-icon-wrapper {
  width: 35px;
  height: 35px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid #d7d3d3;
  border-radius: 8px;
  background-color: #ffffff;
  margin-right: 10px;
  cursor: pointer;
  transition: background-color 0.3s;
  outline: none;
}

.upload-icon-wrapper:hover {
  background-color: #e2e6ea;
}

.upload-icon-wrapper:focus {
  outline: none;
}

.upload-icon {
  font-size: 16px;
  color: #000000;
}

.send-button {
  background-color: #e74c3c;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-left: 10px;
  outline: none;
}

.send-button:hover {
  background-color: #c94334;
}

.send-button:focus {
  outline: none;
}

.nav-link:hover,
.send-button:hover,
.upload-icon-wrapper:hover,
.toggle-button:hover,
#userEmailButton:hover {
  cursor: pointer;
}

textarea:hover,
textarea:focus {
  cursor: text;
}

.nav-link,
.toggle-button,
.send-button,
.upload-icon-wrapper,
#userEmailButton {
  user-select: none;
}

.nav-link:focus,
.toggle-button:focus,
.send-button:focus,
.upload-icon-wrapper:focus,
#userEmailButton:focus {
  outline: none;
}

.pdf-upload-circle {
  display: none;
  position: absolute;
  top: -20px;
  left: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid yellow;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ffffff;
  cursor: pointer;
  transition:
    border 0.3s ease,
    transform 0.3s ease;
}

.pdf-upload-circle i {
  font-size: 16px;
  color: red;
}

.pdf-upload-circle .delete-pdf {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #ffffff;
  border: 1px solid #d7d3d3;
  border-radius: 50%;
  width: 15px;
  height: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 10px;
  color: #ff0000;
  cursor: pointer;
  display: none;
}

.pdf-upload-circle:hover .delete-pdf {
  display: flex;
}

.pdf-upload-circle.uploading {
  border: 3px solid orange;
  animation: spin 2s linear infinite;
}

.mock-textarea {
  pointer-events: none;
  caret-color: transparent;
  user-select: none;
  cursor: not-allowed;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
