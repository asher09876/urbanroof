import os
import sys
import fitz  
import easyocr

OCR_TRIGGER_THRESHOLD = 300


def validate_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"[ERROR] File not found: {path}")
    if not path.lower().endswith(".pdf"):
        raise ValueError("[ERROR] Input must be PDF.")


def extract_pdf_text(path):
    doc = fitz.open(path)

    text = ""
    pages = doc.page_count

    for i in range(pages):
        page = doc.load_page(i)
        page_text = page.get_text()

        if page_text and page_text.strip():
            text += f"\n\n--- PAGE {i+1} ---\n\n"
            text += page_text

    doc.close()
    return text, pages


def run_easyocr(path):
    print("[INFO] Starting EasyOCR fallback...")

    reader = easyocr.Reader(['en'], gpu=False)
    doc = fitz.open(path)

    ocr_text = ""

    for i in range(doc.page_count):
        print(f"[OCR] Page {i+1}")

        page = doc.load_page(i)

        # Render page to image (NO poppler)
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")

        results = reader.readtext(img_bytes, detail=0)

        if results:
            ocr_text += f"\n\n--- OCR PAGE {i+1} ---\n\n"
            for line in results:
                ocr_text += line + "\n"

    doc.close()
    return ocr_text


def save(text, out):
    if not text.strip():
        raise ValueError("[ERROR] No text extracted.")

    with open(out, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"[SUCCESS] Saved → {out}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python extract_text_easyocr_fitz.py <input_pdf> <output_txt>")
        sys.exit(1)

    pdf = sys.argv[1]
    out = sys.argv[2]

    validate_file(pdf)

    print("[INFO] Running PyMuPDF extraction...")
    text, pages = extract_pdf_text(pdf)

    base_chars = len(text.strip())

    print(f"[INFO] Pages: {pages}")
    print(f"[INFO] Characters (primary): {base_chars}")

    if base_chars < OCR_TRIGGER_THRESHOLD:
        print("[WARNING] Low text detected → triggering EasyOCR")
        ocr = run_easyocr(pdf)
        text += "\n\n--- OCR MERGED CONTENT ---\n\n"
        text += ocr

    final_chars = len(text.strip())
    print(f"[INFO] Final character count: {final_chars}")

    save(text, out)
    print("[DONE] Extraction complete.")


if __name__ == "__main__":
    main()
