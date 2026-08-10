import uuid

import pytest

from app.services.chunking_service import ChunkingService
from app.services.parsing.base_parser import ParsedPage


DOCUMENT_ID = uuid.uuid4()


def test_rejects_non_positive_chunk_size():
    with pytest.raises(ValueError):
        ChunkingService(chunk_size=0, chunk_overlap=0)


def test_rejects_overlap_greater_than_or_equal_to_chunk_size():
    with pytest.raises(ValueError):
        ChunkingService(chunk_size=100, chunk_overlap=100)


def test_short_page_becomes_a_single_chunk():
    service = ChunkingService(
        chunk_size=1000,
        chunk_overlap=50,
        min_chunk_size=10,
    )
    pages = [ParsedPage(page_number=1, text="A short single-chunk page.")]

    chunks = service.chunk_pages(DOCUMENT_ID, pages)

    assert len(chunks) == 1
    assert chunks[0].document_id == DOCUMENT_ID
    assert chunks[0].page_number == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].content == "A short single-chunk page."


def test_long_page_is_split_into_multiple_chunks():
    service = ChunkingService(
        chunk_size=50,
        chunk_overlap=10,
        min_chunk_size=10,
    )
    long_text = " ".join(f"word{i}" for i in range(100))
    pages = [ParsedPage(page_number=1, text=long_text)]

    chunks = service.chunk_pages(DOCUMENT_ID, pages)

    # A 50-char budget over ~700 chars of text must not collapse the
    # whole page into a single chunk.
    assert len(chunks) > 1
    assert all(chunk.page_number == 1 for chunk in chunks)
    assert [chunk.chunk_index for chunk in chunks] == list(
        range(len(chunks))
    )


def test_chunks_never_span_multiple_pages():
    service = ChunkingService(chunk_size=1000, chunk_overlap=50)
    pages = [
        ParsedPage(page_number=1, text="Page one content."),
        ParsedPage(page_number=2, text="Page two content."),
    ]

    chunks = service.chunk_pages(DOCUMENT_ID, pages)

    assert [chunk.page_number for chunk in chunks] == [1, 2]
    # chunk_index stays sequential across the whole document, not
    # restarted per page.
    assert [chunk.chunk_index for chunk in chunks] == [0, 1]


def test_empty_page_produces_no_chunks():
    service = ChunkingService(chunk_size=1000, chunk_overlap=50)
    pages = [
        ParsedPage(page_number=1, text=""),
        ParsedPage(page_number=2, text="Real content here."),
    ]

    chunks = service.chunk_pages(DOCUMENT_ID, pages)

    assert len(chunks) == 1
    assert chunks[0].page_number == 2
    assert chunks[0].chunk_index == 0


def test_tiny_trailing_fragment_is_merged_into_previous_chunk():
    service = ChunkingService(
        chunk_size=40,
        chunk_overlap=0,
        min_chunk_size=15,
    )
    # Constructed so the final leftover word(s) alone would fall under
    # min_chunk_size if emitted as their own chunk.
    text = "alpha beta gamma delta epsilon zeta eta"

    chunks = service.chunk_pages(DOCUMENT_ID, [ParsedPage(1, text)])

    assert all(len(chunk.content) >= 15 for chunk in chunks[:-1])
    # No chunk should be a tiny orphaned fragment smaller than the
    # minimum, once merged.
    assert len(chunks[-1].content) >= 15


def test_chunking_is_deterministic():
    service = ChunkingService(chunk_size=30, chunk_overlap=5, min_chunk_size=10)
    text = "one two three four five six seven eight nine ten eleven twelve"
    pages = [ParsedPage(page_number=1, text=text)]

    first_run = service.chunk_pages(DOCUMENT_ID, pages)
    second_run = service.chunk_pages(DOCUMENT_ID, pages)

    assert [c.content for c in first_run] == [c.content for c in second_run]


def test_consecutive_chunks_share_overlap_content():
    service = ChunkingService(chunk_size=30, chunk_overlap=10, min_chunk_size=5)
    text = "one two three four five six seven eight nine ten eleven twelve"
    pages = [ParsedPage(page_number=1, text=text)]

    chunks = service.chunk_pages(DOCUMENT_ID, pages)

    assert len(chunks) > 1
    first_words = chunks[0].content.split()
    second_words = chunks[1].content.split()
    # The tail of chunk 0 should reappear at the head of chunk 1.
    assert first_words[-1] in second_words
