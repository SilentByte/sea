# #
# # SEA / SMART ENGINEERING ASSISTANT
# # Copyright (c) 2024 SilentByte <https://silentbyte.com/>
# #


import re

from io import BytesIO
from dataclasses import dataclass
from typing import Iterator

from llama_index.core.schema import Document
from llama_index.core.utils import set_global_tokenizer
from llama_index.core.node_parser import SentenceSplitter
from unstructured.partition.auto import partition
from transformers import AutoTokenizer

set_global_tokenizer(AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer"))


@dataclass
class LocalizedText:
    text: str
    start_page_no: int
    end_page_no: int


def normalize_text(text: str) -> str | None:
    text = text.strip()

    if not text:
        return None

    for p in [
        # General garbage.
        r'^\s*$',
        r'^(\d+\s*)*$',
        r'^.$',

        # Commonly occurring document boilerplate.
        r'^Section$',
        r'^Issue Date:$',
        r'^Dated\s*:.*$',
        r'^Change\(s\):$',
        r'^Issue:?$',
        r'^Issued by:?.*$',
        r'^(Page:\s*)?\d+\s+of\s+\d+.*$',
        r'^.*Table of Contents.*$',
        r'^.*\.{4,}.*$',
    ]:
        if re.search(p, text, re.IGNORECASE):
            return None

    return text


def extract_document_pages(document_data: bytes) -> Iterator[LocalizedText]:
    elements = partition(
        file=BytesIO(document_data),
        include_page_breaks=True,
    )

    page_counter = 0
    page_text = ''

    for e in elements:
        if e.category == 'PageBreak':
            if page_text:
                yield LocalizedText(page_text, page_counter, page_counter)
                page_text = ''

            page_counter += 1
        else:
            if normalized_text := normalize_text(e.text):
                page_text += normalized_text + '\n'

    if page_text:
        yield LocalizedText(page_text, page_counter, page_counter)


def find_page_no_by_char_count(page_no_char_index: list[int], char_count: int) -> int:
    for page_no, index in enumerate(page_no_char_index):
        if index > char_count:
            return page_no

    return 0


def extract_document_sentence_chunks(
        document_data: bytes,
        chunk_size: int,
        chunk_overlap: int,
) -> Iterator[LocalizedText]:
    page_no_index = []
    document_text = ''

    for page in extract_document_pages(document_data):
        document_text += page.text + '\n'
        page_no_index.append(len(document_text))

    sentence_splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    for node in sentence_splitter.get_nodes_from_documents([Document(text=document_text)]):
        yield LocalizedText(
            node.text or '',
            find_page_no_by_char_count(page_no_index, node.start_char_idx or 0),
            find_page_no_by_char_count(page_no_index, node.end_char_idx or 0),
        )
