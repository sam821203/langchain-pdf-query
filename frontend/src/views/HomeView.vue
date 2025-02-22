<template>
  <div class="home-container">
    <h1 class="title">Smart PDF Query</h1>
    <h3 class="description">Ask any PDF-related questions to get started!</h3>
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
          :placeholder="animatedPlaceholder"
        ></textarea>

        <!-- upload PDF -->
        <button
          class="send-button"
          @click="uploadPDF"
          :disabled="!selectedFile"
        >
          <font-awesome-icon icon="arrow-up" />
        </button>
      </div>
    </div>
    <p v-if="uploadStatus" class="upload-status">{{ uploadStatus }}</p>

    <!-- PDF 上傳區 -->
    <!-- <div class="upload-box">
      <input type="file" @change="handleFileUpload" accept="application/pdf" />
      <button
        @click="uploadPDF"
        class="upload-button"
        :disabled="!selectedFile"
      >
        上傳 PDF
      </button>
      <p v-if="uploadStatus" class="upload-status">{{ uploadStatus }}</p>
    </div> -->

    <!-- 查詢區 -->
    <div class="query-box">
      <input
        v-model="question"
        placeholder="請輸入問題"
        class="input-field"
        :disabled="!isPDFUploaded"
      />
      <button
        @click="queryAPI"
        class="query-button"
        :disabled="!isPDFUploaded || !question"
      >
        查詢
      </button>
    </div>

    <!-- 回答區 -->
    <div v-if="answer" class="answer-box">{{ answer }}</div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from "vue";
import { queryPDF, uploadPDFFile } from "../services/apiService";

const question = ref("");
const answer = ref("");
const selectedFile = ref(null);
const uploadStatus = ref("");
const isPDFUploaded = ref(false); // 確保 PDF 上傳後才能查詢
const fileInput = ref(null);
const animatedPlaceholder = ref("Upload a PDF...");
const placeholderTexts = [
  "Uploading...",
  "Almost there...",
  "Processing PDF...",
  "Just a moment...",
];
let placeholderIndex = 0;
let animationInterval = null;

const triggerFileUpload = () => {
  fileInput.value.click(); // 觸發隱藏的 input 點擊事件
};

// 處理選擇的檔案
const handleFileUpload = (event) => {
  selectedFile.value = event.target.files[0];
  console.log("選擇的檔案：", selectedFile.value);
};

const startPlaceholderAnimation = () => {
  animationInterval = setInterval(() => {
    animatedPlaceholder.value =
      placeholderTexts[placeholderIndex % placeholderTexts.length];
    placeholderIndex++;
  }, 1000);
};

const stopPlaceholderAnimation = () => {
  if (animationInterval) {
    clearInterval(animationInterval);
    animationInterval = null;
    animatedPlaceholder.value = "Ask anything about your PDF...";
  }
};

// 上傳 PDF
const uploadPDF = async () => {
  console.log("上傳PDF");
  if (!selectedFile.value) return;

  uploadStatus.value = "Uploading...";
  startPlaceholderAnimation();

  try {
    await uploadPDFFile(selectedFile.value);
    uploadStatus.value = "✅ Upload successful! You can now ask questions.";
    isPDFUploaded.value = true;
    stopPlaceholderAnimation();
  } catch (error) {
    console.error("PDF upload failed", error);
    uploadStatus.value = "❌ Upload failed, please try again.";
    stopPlaceholderAnimation();
  }
};

const removePDF = () => {
  selectedFile.value = null;
  isPDFUploaded.value = false;
  uploadStatus.value = "";
  animatedPlaceholder.value = "Upload a PDF...";
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

// 確保離開元件時停止動畫
onUnmounted(() => {
  stopPlaceholderAnimation();
});
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f8f9fa;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 20px;
  color: #333;
}

.description {
  font-size: 1.25rem;
  font-weight: 500;
  margin-bottom: 40px;
}

/* 上傳 PDF */
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
  color: #555;
}

/* 查詢區 */
.query-box {
  display: flex;
  gap: 10px;
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.input-field {
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 250px;
}

.query-button {
  padding: 10px 20px;
  font-size: 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.query-button:hover {
  background-color: #0056b3;
}

.query-button:disabled {
  background-color: #ccc;
}

.answer-box {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  text-align: center;
}

/* Input Area Styling */
.input-area {
  width: 100%;
  max-width: 700px; /* Match ChatGPT's input width */
  display: flex;
  justify-content: center;
  margin-bottom: 20px; /* Space below input */
  position: relative; /* For positioning PDF upload circle */
}

/* Input Wrapper Styling */
.input-wrapper {
  display: flex;
  align-items: center;
  padding: 10px 15px; /* Padding inside the input */
  border: 1px solid #d7d3d3;
  border-radius: 8px; /* Border radius of 8px */
  width: 100%;
  background-color: #ffffff;
  position: relative; /* For positioning PDF upload circle */
}

/* Textarea Styling */
textarea {
  flex-grow: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 10px;
  font-size: 1rem;
  resize: none;
  min-height: 40px; /* Minimum height */
  max-height: 120px; /* Maximum height before scrollbar appears */
  overflow-y: auto; /* Show scrollbar when max-height is reached */
  transition: height 0.2s ease; /* Smooth transition */
}

/* Upload Icon Wrapper Styling */
.upload-icon-wrapper {
  width: 35px;
  height: 35px;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid #d7d3d3;
  border-radius: 8px; /* Rounded corners */
  background-color: #ffffff; /* White background */
  margin-right: 10px;
  cursor: pointer;
  transition: background-color 0.3s;
  outline: none; /* Remove default outline */
}

/* Hover Effect for Upload Icon */
.upload-icon-wrapper:hover {
  background-color: #e2e6ea;
}

/* Remove Blue Outline on Focus */
.upload-icon-wrapper:focus {
  outline: none;
}

/* Upload Icon Styling */
.upload-icon {
  font-size: 16px;
  color: #000000;
}

/* 
      
      
      Button Styling */
.send-button {
  background-color: #007bff;
  border: none;
  border-radius: 8px; /* Rounded corners to match upload icon */
  padding: 8px 12px; /* Increased padding for better size */
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-left: 10px;
  outline: none; /* Remove default outline */
}

/* Hover Effect for Send Button */
.send-button:hover {
  background-color: #0056b3;
}

/* Remove Blue Outline on Focus */
.send-button:focus {
  outline: none;
}

/* Cursor Styling for Interactive Elements */
.nav-link:hover,
.send-button:hover,
.upload-icon-wrapper:hover,
.toggle-button:hover,
#userEmailButton:hover {
  cursor: pointer;
}

/* Cursor Styling for Textarea */
textarea:hover,
textarea:focus {
  cursor: text;
}

/* Prevent Text Selection on Buttons */
.nav-link,
.toggle-button,
.send-button,
.upload-icon-wrapper,
#userEmailButton {
  user-select: none;
}

/* Focus Styles for Accessibility */
.nav-link:focus,
.toggle-button:focus,
.send-button:focus,
.upload-icon-wrapper:focus,
#userEmailButton:focus {
  outline: none; /* Remove default outline */
}

/* PDF Upload Circle Styling */
.pdf-upload-circle {
  display: none; /* Hidden by default */
  position: absolute;
  top: -20px; /* Position above the input field */
  left: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid yellow; /* Yellow stroke for upload progress */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ffffff;
  cursor: pointer;
  transition:
    border 0.3s ease,
    transform 0.3s ease;
}

/* PDF Icon within Circle */
.pdf-upload-circle i {
  font-size: 16px;
  color: red; /* Red color to indicate PDF */
}

/* 'X' Button to Delete Uploaded PDF */
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
  display: none; /* Hidden by default */
}

/* Show 'X' on Hover */
.pdf-upload-circle:hover .delete-pdf {
  display: flex;
}

/* PDF Upload Progress Styling */
.pdf-upload-circle.uploading {
  border: 3px solid orange; /* Change color during upload */
  animation: spin 2s linear infinite; /* Spinner animation */
}

/* Spinner Animation */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>
