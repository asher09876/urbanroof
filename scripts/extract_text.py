import os
import sys
import pdfplumber
from datetime import datetime


def validate_file(path: str) -> None:
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ERROR] File does not exist: {path}")

    if not os.path.isfile(path):
        raise ValueError(f"[ERROR] Path is not a file: {path}")

    if not path.lower().endswith(".pdf"):
        raise ValueError(f"[ERROR] File is not a PDF: {path}")


def extract_text_from_pdf(path: str) -> dict:
   
    validate_file(path)

    extraction_report = {
        "file_path": path,
        "pages_total": 0,
        "pages_with_text": 0,
        "pages_empty": 0,
        "characters_extracted": 0,
        "extraction_timestamp": datetime.now().isoformat(),
        "text": ""
    }

    try:
        with pdfplumber.open(path) as pdf:
            extraction_report["pages_total"] = len(pdf.pages)

            if len(pdf.pages) == 0:
                raise ValueError("[ERROR] PDF contains zero pages.")

            for i, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()

                if page_text and page_text.strip():
                    extraction_report["pages_with_text"] += 1
                    extraction_report["characters_extracted"] += len(page_text)
                    extraction_report["text"] += f"\n\n--- PAGE {i} ---\n\n"
                    extraction_report["text"] += page_text
                else:
                    extraction_report["pages_empty"] += 1

    except Exception as e:
        raise RuntimeError(f"[ERROR] Failed during PDF parsing: {str(e)}")

    return extraction_report


def sanity_check(report: dict) -> None:
    
    if report["pages_with_text"] == 0:
        raise ValueError("[ERROR] No text extracted from pdf. Could be only imaages")

    if report["characters_extracted"] < 100:
        raise ValueError(
            "[WARNING] Very low text extracted. Check if pdf mostly contains images."
        )

    print(f"Total Pages: {report['pages_total']}")
    print(f"Pages With Text: {report['pages_with_text']}")
    print(f"Empty Pages: {report['pages_empty']}")
    print(f"Characters Extracted: {report['characters_extracted']}")
    


def save_text_output(report: dict, output_path: str) -> None:
    """Saving extracted text."""

    if not report["text"]:
        raise ValueError("[ERROR] No text available to save.")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report["text"])
    except Exception as e:
        raise RuntimeError(f"[ERROR] Failed to write output file: {str(e)}")

    print(f"[SUCCESS] Extracted text saved to: {output_path}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_text.py <input_pdf_path> <output_txt_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_txt = sys.argv[2]

    print(f"[INFO] Starting extraction for: {input_pdf}")

    report = extract_text_from_pdf(input_pdf)

    sanity_check(report)

    save_text_output(report, output_txt)

    print("[DONE] Extraction complete.\n")


if __name__ == "__main__":
    main()
