from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.core.logging import get_logger
from app.services.parsing.base_parser import DocumentParser
from app.services.parsing.base_parser import DocumentParsingError
from app.services.parsing.base_parser import ParsedPage


logger = get_logger("parsing.pdf")


class PyPdfDocumentParser(DocumentParser):
    """Page-aware PDF parser backed by `pypdf`."""

    SUPPORTED_MIME_TYPES = {"application/pdf"}
    SUPPORTED_EXTENSIONS = (".pdf",)

    def supports(self, mime_type: str, filename: str) -> bool:
        return (
            mime_type in self.SUPPORTED_MIME_TYPES
            or filename.lower().endswith(self.SUPPORTED_EXTENSIONS)
        )

    def parse(self, file_path: str) -> list[ParsedPage]:
        try:
            reader = PdfReader(file_path)
        except (PdfReadError, OSError) as exc:
            raise DocumentParsingError(
                f"Unable to read PDF file: {exc}"
            ) from exc

        if reader.is_encrypted:
            raise DocumentParsingError(
                "Encrypted PDF files are not supported."
            )

        pages: list[ParsedPage] = []

        for index, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception as exc:  # pypdf can raise various parse errors
                logger.warning(
                    "Failed to extract text from page %s: %s",
                    index + 1,
                    exc,
                )
                text = ""

            pages.append(
                ParsedPage(
                    page_number=index + 1,
                    text=text.strip(),
                )
            )

        if not pages:
            raise DocumentParsingError(
                "PDF file contains no pages."
            )

        return pages
