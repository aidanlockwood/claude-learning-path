from markitdown import MarkItDown, StreamInfo
from io import BytesIO
from pathlib import Path

from pydantic import Field

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    path: str = Field(description="Filesystem path to a PDF or DOCX file to convert to markdown"),
) -> str:
    """Reads a PDF or DOCX file from disk and converts it to markdown-formatted text.

    Given a path to a file on disk, reads its binary contents and converts
    them to markdown. The file type is inferred from the path's extension.

    When to use:
    - When you have a filesystem path to a PDF or DOCX document and need its
      contents as markdown
    - When you do not already have the document's bytes in memory (if you do,
      use `binary_document_to_markdown` directly instead)

    When not to use:
    - For file types other than PDF or DOCX

    Examples:
    >>> document_path_to_markdown("/path/to/report.pdf")
    '# Report\\n\\n...'
    >>> document_path_to_markdown("/path/to/notes.docx")
    '# Notes\\n\\n...'2
    """
    file_path = Path(path)
    extension = file_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{file_path.suffix}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    binary_data = file_path.read_bytes()
    return binary_document_to_markdown(binary_data, extension)
