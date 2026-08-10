import pytest

from app.services.parsing.base_parser import DocumentParsingError
from app.services.parsing.pdf_parser import PyPdfDocumentParser
from tests.fakes import build_minimal_pdf


def test_supports_pdf_by_mime_type(tmp_path):
    parser = PyPdfDocumentParser()

    assert parser.supports("application/pdf", "anything.bin") is True


def test_supports_pdf_by_extension(tmp_path):
    parser = PyPdfDocumentParser()

    assert parser.supports("application/octet-stream", "report.PDF") is True


def test_does_not_support_non_pdf():
    parser = PyPdfDocumentParser()

    assert parser.supports("text/plain", "notes.txt") is False


def test_parse_preserves_page_numbers_and_text(tmp_path):
    pdf_bytes = build_minimal_pdf(
        [
            "Cold-chain SOP page one content.",
            "Temperature excursion handling on page two.",
            "Final page with sign-off details.",
        ]
    )
    pdf_path = tmp_path / "sop.pdf"
    pdf_path.write_bytes(pdf_bytes)

    parser = PyPdfDocumentParser()
    pages = parser.parse(str(pdf_path))

    assert [page.page_number for page in pages] == [1, 2, 3]
    assert "page one" in pages[0].text
    assert "excursion" in pages[1].text
    assert "sign-off" in pages[2].text


def test_parse_does_not_lose_blank_pages(tmp_path):
    pdf_bytes = build_minimal_pdf(["Has content.", ""])
    pdf_path = tmp_path / "mixed.pdf"
    pdf_path.write_bytes(pdf_bytes)

    parser = PyPdfDocumentParser()
    pages = parser.parse(str(pdf_path))

    # The blank page must still be present with correct numbering, not
    # silently dropped.
    assert len(pages) == 2
    assert pages[1].page_number == 2
    assert pages[1].text == ""


def test_parse_raises_on_invalid_pdf(tmp_path):
    bad_path = tmp_path / "not_a_pdf.pdf"
    bad_path.write_bytes(b"this is not a pdf file")

    parser = PyPdfDocumentParser()

    with pytest.raises(DocumentParsingError):
        parser.parse(str(bad_path))


def test_parse_raises_on_missing_file(tmp_path):
    parser = PyPdfDocumentParser()

    with pytest.raises(DocumentParsingError):
        parser.parse(str(tmp_path / "missing.pdf"))
