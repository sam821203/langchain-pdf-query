import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000', // 這是 FastAPI 伺服器地址
  timeout: 10000,
})

export const queryPDF = (question) => {
  return api.post('/query', { question })
}
