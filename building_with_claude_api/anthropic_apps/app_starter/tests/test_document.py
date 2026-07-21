import os
import stat
from pathlib import Path
from unittest.mock import patch

import pytest
from tools.document import binary_document_to_markdown, document_path_to_markdown


class TestBinaryDocumentToMarkdown:
    # Define fixture paths
    FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
    DOCX_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.docx")
    PDF_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.pdf")

    def test_fixture_files_exist(self):
        """Verify test fixtures exist."""
        assert os.path.exists(self.DOCX_FIXTURE), (
            f"DOCX fixture not found at {self.DOCX_FIXTURE}"
        )
        assert os.path.exists(self.PDF_FIXTURE), (
            f"PDF fixture not found at {self.PDF_FIXTURE}"
        )

    def test_binary_document_to_markdown_with_docx(self):
        """Test converting a DOCX document to markdown."""
        # Read binary content from the fixture
        with open(self.DOCX_FIXTURE, "rb") as f:
            docx_data = f.read()

        # Call function
        result = binary_document_to_markdown(docx_data, "docx")

        # Basic assertions to check the conversion was successful
        assert isinstance(result, str)
        assert len(result) > 0
        # Check for typical markdown formatting - this will depend on your actual test file
        assert "#" in result or "-" in result or "*" in result

    def test_binary_document_to_markdown_with_pdf(self):
        """Test converting a PDF document to markdown."""
        # Read binary content from the fixture
        with open(self.PDF_FIXTURE, "rb") as f:
            pdf_data = f.read()

        # Call function
        result = binary_document_to_markdown(pdf_data, "pdf")

        # Basic assertions to check the conversion was successful
        assert isinstance(result, str)
        assert len(result) > 0
        # Check for typical markdown formatting - this will depend on your actual test file
        assert "#" in result or "-" in result or "*" in result


class TestDocumentPathToMarkdown:
    # Define fixture paths
    FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
    DOCX_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.docx")
    PDF_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.pdf")

    # --- Happy path ---

    def test_document_path_to_markdown_with_docx(self):
        """Test converting a DOCX document to markdown from a path."""
        result = document_path_to_markdown(self.DOCX_FIXTURE)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "#" in result or "-" in result or "*" in result

    def test_document_path_to_markdown_with_pdf(self):
        """Test converting a PDF document to markdown from a path."""
        result = document_path_to_markdown(self.PDF_FIXTURE)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "#" in result or "-" in result or "*" in result

    @pytest.mark.parametrize("fixture_attr, extension", [("DOCX_FIXTURE", "docx"), ("PDF_FIXTURE", "pdf")])
    def test_matches_binary_document_to_markdown(self, fixture_attr, extension):
        """The path-based tool should be a thin wrapper: same output as reading
        the bytes directly and calling binary_document_to_markdown."""
        fixture_path = getattr(self, fixture_attr)
        with open(fixture_path, "rb") as f:
            expected = binary_document_to_markdown(f.read(), extension)

        result = document_path_to_markdown(fixture_path)

        assert result == expected

    # --- Path handling ---

    def test_accepts_pathlib_path(self):
        """Test that a pathlib.Path is accepted, not just a str."""
        result = document_path_to_markdown(Path(self.DOCX_FIXTURE))

        assert isinstance(result, str)
        assert len(result) > 0

    def test_accepts_relative_path(self, monkeypatch):
        """Test that a path relative to the current working directory works."""
        monkeypatch.chdir(self.FIXTURES_DIR)

        result = document_path_to_markdown("mcp_docs.pdf")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_path_with_spaces_and_unicode(self, tmp_path):
        """Test a filename containing spaces and unicode characters."""
        tricky_path = tmp_path / "mcp docs — café ☕.docx"
        tricky_path.write_bytes(Path(self.DOCX_FIXTURE).read_bytes())

        result = document_path_to_markdown(str(tricky_path))

        assert isinstance(result, str)
        assert len(result) > 0

    # --- Error handling ---

    def test_nonexistent_path_raises(self, tmp_path):
        """Test that a missing file raises FileNotFoundError."""
        missing_path = tmp_path / "does_not_exist.pdf"

        with pytest.raises(FileNotFoundError):
            document_path_to_markdown(str(missing_path))

    def test_directory_path_raises(self, tmp_path):
        """Test that passing a directory instead of a file raises an error."""
        directory = tmp_path / "some_dir.pdf"
        directory.mkdir()

        with pytest.raises((IsADirectoryError, OSError)):
            document_path_to_markdown(str(directory))

    def test_unsupported_extension_raises(self, tmp_path):
        """Test that a file type outside PDF/DOCX raises ValueError."""
        text_path = tmp_path / "notes.txt"
        text_path.write_text("just some plain text")

        with pytest.raises(ValueError):
            document_path_to_markdown(str(text_path))

    def test_empty_file_raises(self, tmp_path):
        """Test that a zero-byte file with a valid extension fails clearly
        rather than returning an empty/garbage result silently."""
        empty_path = tmp_path / "empty.docx"
        empty_path.write_bytes(b"")

        with pytest.raises(Exception):
            document_path_to_markdown(str(empty_path))

    def test_corrupted_file_raises(self, tmp_path):
        """Test that a file with a valid extension but garbage binary content
        fails clearly rather than returning a bogus result. Note: MarkItDown
        falls back to a plain-text converter for content that happens to
        decode as text, so this uses non-decodable binary bytes to force a
        genuine parse failure."""
        corrupted_path = tmp_path / "corrupted.pdf"
        corrupted_path.write_bytes(os.urandom(256))

        with pytest.raises(Exception):
            document_path_to_markdown(str(corrupted_path))

    @pytest.mark.skipif(
        os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
        reason="file permission bits don't restrict access for root or on Windows",
    )
    def test_no_read_permission_raises(self, tmp_path):
        """Test that a file without read permission raises PermissionError."""
        restricted_path = tmp_path / "restricted.pdf"
        restricted_path.write_bytes(Path(self.PDF_FIXTURE).read_bytes())
        restricted_path.chmod(0)

        try:
            with pytest.raises(PermissionError):
                document_path_to_markdown(str(restricted_path))
        finally:
            # Restore permissions so tmp_path cleanup can remove the file
            restricted_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    # --- File-type inference ---

    def test_extension_case_insensitive(self, tmp_path):
        """Test that an uppercase extension (.PDF/.DOCX) still works."""
        upper_path = tmp_path / "mcp_docs.PDF"
        upper_path.write_bytes(Path(self.PDF_FIXTURE).read_bytes())

        result = document_path_to_markdown(str(upper_path))

        assert isinstance(result, str)
        assert len(result) > 0

    def test_file_type_correctly_inferred_per_extension(self):
        """Test that the extension actually drives which file_type is passed
        through to binary_document_to_markdown, so a .docx isn't silently
        treated as a .pdf or vice versa."""
        with patch(
            "tools.document.binary_document_to_markdown",
            wraps=binary_document_to_markdown,
        ) as spy:
            document_path_to_markdown(self.DOCX_FIXTURE)
            document_path_to_markdown(self.PDF_FIXTURE)

        docx_call, pdf_call = spy.call_args_list
        assert docx_call.args[1] == ".docx"
        assert pdf_call.args[1] == ".pdf"
