# RAG Prompts

可透過 YAML 檔調教 RAG 的 system 角色、user 模板與「無相關內容」指示。

- 在 `.env` 設定 `RAG_PROMPTS_FILE=backend/prompts/rag_default.yaml`（或你的副本路徑，可相對專案根或絕對路徑）。
- 若未設定，則使用程式內建預設；環境變數 `RAG_SYSTEM_PROMPT`、`RAG_USER_TEMPLATE`、`RAG_NO_MATCH_INSTRUCTION` 可個別覆寫。
- YAML 格式見 `rag_default.yaml`，`user_template` 須包含 `{context}` 與 `{input}`；`system` 內可使用 `{no_match_instruction}` 占位符。
