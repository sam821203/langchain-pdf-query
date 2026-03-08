<template>
  <div class="answer-box" v-html="html"></div>
</template>

<script setup>
defineProps({
  html: {
    type: String,
    default: "",
  },
});
</script>

<style scoped>
.answer-box {
  width: 100%;
  padding: 20px;
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  text-align: left;
  line-height: 1.6;
  word-break: break-word;
}

.answer-box :deep(p) {
  margin: 0 0 0.75em;
}

.answer-box :deep(p:last-child) {
  margin-bottom: 0;
}

.answer-box :deep(strong),
.answer-box :deep(b) {
  font-weight: 700;
}

.answer-box :deep(h1),
.answer-box :deep(h2),
.answer-box :deep(h3) {
  margin: 1em 0 0.5em;
  font-weight: 600;
  line-height: 1.3;
}

.answer-box :deep(h1) {
  font-size: 1.35rem;
}

.answer-box :deep(h2) {
  font-size: 1.2rem;
}

.answer-box :deep(h3) {
  font-size: 1.05rem;
}

.answer-box :deep(ul),
.answer-box :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.answer-box :deep(li) {
  margin: 0.25em 0;
}

.answer-box :deep(code) {
  padding: 0.15em 0.4em;
  font-size: 0.9em;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 4px;
}

.answer-box :deep(pre) {
  margin: 0.75em 0;
  padding: 12px;
  overflow-x: auto;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 6px;
}

.answer-box :deep(pre code) {
  padding: 0;
  background: none;
}

.answer-box :deep(a) {
  color: #e74c3c;
  text-decoration: underline;
}

.answer-box :deep(a:hover) {
  text-decoration: none;
}
</style>
