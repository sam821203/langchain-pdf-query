<template>
  <div class="home">
    <h1>🦜 鳥類資訊查詢系統</h1>
    <input v-model="question" placeholder="請輸入問題" />
    <button @click="queryAPI">查詢</button>
    <p>{{ answer }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { queryPDF } from '../services/apiService'

const question = ref('')
const answer = ref('')

const queryAPI = async () => {
  try {
    const response = await queryPDF(question.value)
    answer.value = response.data.answer
  } catch (error) {
    console.log(error)
    answer.value = '查詢失敗，請稍後再試'
  }
}
</script>
