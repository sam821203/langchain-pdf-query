"""Custom exceptions for unified HTTP error handling."""


class AppException(Exception):
    """Base for app-specific exceptions with HTTP status and message."""
    status_code: int = 500
    detail: str = "Internal server error"
    type_name: str = "AppException"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.detail)


class PDFParseError(AppException):
    """PDF 解析失敗、損壞或非 PDF 格式。"""
    status_code = 422
    detail = "PDF 解析失敗，請確認檔案為有效 PDF。"
    type_name = "PDFParseError"


class OpenAITimeoutError(AppException):
    """OpenAI API 逾時。"""
    status_code = 504
    detail = "OpenAI API 逾時，請稍後再試。"
    type_name = "OpenAITimeoutError"


class VectorStoreError(AppException):
    """Chroma 寫入或讀取失敗。"""
    status_code = 503
    detail = "向量儲存操作失敗。"
    type_name = "VectorStoreError"


class NoPDFLoadedError(AppException):
    """尚未上傳 PDF 就進行查詢。"""
    status_code = 400
    detail = "尚未上傳 PDF。"
    type_name = "NoPDFLoadedError"
