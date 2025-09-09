#!/usr/bin/env python3
"""
Convert a local PDF to Markdown using Mistral's OCR via the official SDK.

Inputs:
  ./dndbeyond-pdf-test/ceej10_110736250.pdf
Outputs:
  ./knowledge_base/ceej10_110736250.md

Requires:
  pip install mistralai python-dotenv
  .env with MISTRAL_API_KEY=...
"""

import os
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mistralai import Mistral, models  # typed responses & exceptions


class MistralOCRConverter:
    def __init__(self) -> None:
        load_dotenv()
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment/.env")
        self.client = Mistral(api_key=api_key)

    @staticmethod
    def _pdf_to_data_url(pdf_path: Path) -> str:
        with open(pdf_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:application/pdf;base64,{b64}"

    def _ocr_via_data_url(self, pdf_path: Path, include_images: bool) -> Any:
        """Small/medium PDFs: inline data URL."""
        data_url = self._pdf_to_data_url(pdf_path)
        return self.client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "document_url", "document_url": data_url},
            include_image_base64=bool(include_images),
        )

    def _ocr_via_upload(self, pdf_path: Path, include_images: bool) -> Any:
        """
        Larger PDFs: upload -> signed URL -> OCR.
        IMPORTANT: purpose='ocr' is required per docs.
        """
        with open(pdf_path, "rb") as fh:
            uploaded = self.client.files.upload(
                file={"file_name": pdf_path.name, "content": fh},
                purpose="ocr",  # <-- critical
            )
        signed = self.client.files.get_signed_url(file_id=uploaded.id)

        return self.client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "document_url", "document_url": signed.url},
            include_image_base64=bool(include_images),
        )

    @staticmethod
    def _as_dict(maybe_model: Any) -> Dict[str, Any]:
        """Handle Pydantic v2/v1 or dict."""
        if isinstance(maybe_model, dict):
            return maybe_model
        if hasattr(maybe_model, "model_dump"):
            return maybe_model.model_dump()
        if hasattr(maybe_model, "dict"):
            return maybe_model.dict()
        d: Dict[str, Any] = {}
        if hasattr(maybe_model, "pages"):
            d["pages"] = getattr(maybe_model, "pages")
        return d

    @staticmethod
    def extract_markdown(ocr_result: Any) -> str:
        """Concatenate pages[].markdown (fallback to text/content)."""
        pages_obj = getattr(ocr_result, "pages", None)
        if pages_obj is None:
            pages_obj = MistralOCRConverter._as_dict(ocr_result).get("pages", [])
        pages: List[Any] = pages_obj or []
        if not pages:
            return "# (No pages returned)\n"

        parts: List[str] = []
        for i, page in enumerate(pages):
            md: Optional[str] = (
                getattr(page, "markdown", None)
                if hasattr(page, "markdown")
                else (page.get("markdown") if isinstance(page, dict) else None)
            )
            if md is None:
                md = (
                    getattr(page, "text", "")
                    if hasattr(page, "text")
                    else (page.get("text", "") if isinstance(page, dict) else "")
                ) or (
                    getattr(page, "content", "")
                    if hasattr(page, "content")
                    else (page.get("content", "") if isinstance(page, dict) else "")
                )

            header = f"## Page {i+1}\n"
            parts.append((f"\n---\n\n{header}{md}") if i > 0 else (header + md))
        return "".join(parts)

    def to_markdown_file(self, ocr_result: Any, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        md = self.extract_markdown(ocr_result)
        out_path.write_text(md, encoding="utf-8")
        print(f"Markdown saved to: {out_path}  (chars: {len(md)})")

    def run(self, pdf_path: Path, out_path: Path, use_upload: bool = True, include_images: bool = False) -> None:
        try:
            if use_upload:
                print("Using upload + signed URL path...")
                ocr_result = self._ocr_via_upload(pdf_path, include_images)
            else:
                print("Using inline data URL path...")
                ocr_result = self._ocr_via_data_url(pdf_path, include_images)

            self.to_markdown_file(ocr_result, out_path)
            print("✅ Conversion completed successfully!")
        except models.HTTPValidationError as e:
            raise RuntimeError(f"OCR validation error: {getattr(e, 'data', e)}") from e
        except models.SDKError as e:
            raise RuntimeError(f"SDK error: {e}") from e


def main() -> int:
    project_root = Path(__file__).parent.parent
    pdf_path = project_root / "dndbeyond-pdf-test" / "ceej10_125292496.pdf"
    out_path = project_root / "knowledge_base" / "ceej10_125292496.md"

    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        return 1

    converter = MistralOCRConverter()
    converter.run(pdf_path, out_path, use_upload=True, include_images=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
