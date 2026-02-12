# urbanroof
Absolutely — here’s a **complete, professional README.md** you can drop directly into your repo.

This is written to sound **engineer-level**, align with the assignment rubric, and clearly explain your design decisions.

Just copy this into:

```
README.md
```

---

# AI DDR Generator — Applied AI Builder Assignment

## Overview

This project implements an end-to-end AI workflow that converts raw building inspection and thermal imaging PDFs into a structured diagnostic output (`diagnostic.json`).

The system is designed as a **hybrid AI + deterministic pipeline**:

* LLMs are used strictly for structured information extraction.
* All reasoning (root causes, severity, validation) is handled via Python rules.

This separation ensures accuracy, reliability, and explainability while avoiding hallucinated conclusions.

The focus of this assignment is **system design and reliability**, not UI.

---

## Problem Statement

Given:

* A visual site inspection report (PDF)
* A thermal imaging report (PDF)

Build a system that:

* Extracts relevant observations
* Merges inspection and thermal data logically
* Handles missing or conflicting information
* Produces a structured diagnostic output
* Avoids inventing facts
* Generalizes to similar reports

---

## High-Level Architecture

```
Inspection PDF + Thermal PDF
            ↓
      Text Extraction
  (PyMuPDF + EasyOCR fallback)
            ↓
   Structured LLM Extraction
  (Areas, Systems, Thermal Data)
            ↓
   Python Merge + Validation
 (Root Causes + Severity Logic)
            ↓
        diagnostic.json
```

---

## Key Design Principle

**LLMs extract. Python decides.**

LLMs are used only to convert unstructured text into structured JSON.

All diagnostic reasoning — including root cause inference, severity assessment, and missing data detection — is implemented deterministically in Python.

This prevents hallucinations and ensures repeatable outputs.

---

## Folder Structure

```
urbanroof-ai-ddr/
│
├── run_pipeline.py
├── README.md
│
├── scripts/
│   ├── extract_text_easyocr_fitz.py
│   ├── extract_areas.py
│   ├── extract_systems.py
│   ├── extract_thermal.py
│   └── merge.py
│
└── data/
    ├── Sample Report.pdf
    ├── Thermal Images.pdf
    └── diagnostic.json
```

Intermediate files (`inspection.txt`, `thermal.txt`, `areas.json`, etc.) are generated automatically during execution.

---

## Pipeline Stages

### 1. Text Extraction + OCR

* PyMuPDF attempts native text extraction.
* If extracted text is below a threshold, EasyOCR is automatically triggered.
* OCR output is merged with native text.

This ensures thermal PDFs (which are image-heavy) are still fully processed.

---

### 2. Area-Level Extraction (LLM)

Extracts room-wise observations:

* Area name
* Negative observation (damage)
* Positive source (suspected cause)
* Confidence

Output: `areas.json`

---

### 3. System-Level Extraction (LLM)

Extracts building-wide systems:

* Bathroom issues
* Terrace condition
* External wall condition
* Parking leakage

Output: `systems.json`

These represent root-cause systems rather than localized symptoms.

---

### 4. Thermal Extraction (LLM + Validation)

Extracts:

* Image names
* Hotspot / coldspot temperatures
* Temperature delta
* Moisture indicator

Numeric values are validated in Python to prevent incorrect calculations.

Output: `thermal.json`

---

### 5. Merge + Reasoning (Pure Python)

The merge stage performs:

* Thermal-to-area attachment
* Root cause inference
* Severity calculation
* Missing data detection
* Final validation

Severity is computed deterministically based on:

* Number of impacted areas
* Presence of bathroom failures
* Terrace deterioration
* External wall cracks
* Parking ceiling leakage

Final output:

```
data/diagnostic.json
```

This file acts as the system’s “truth layer”.

---

## Running the Pipeline

### Install dependencies

```bash
pip install pymupdf easyocr pillow openai python-dotenv
```

Set your OpenAI key:

```
OPENAI_API_KEY=your_key_here
```

---

### Run everything

From project root:

```bash
python run_pipeline.py
```

On success, you will see:

```
data/diagnostic.json
```

---

## Accuracy & Reliability

Accuracy and reliability are achieved through:

* LLM usage limited to structured extraction only
* Strict JSON schema validation at every stage
* Numeric validation for thermal readings
* OCR fallback for image-heavy PDFs
* Deterministic Python-based root cause and severity logic
* Explicit missing-data tracking
* Fail-loud pipeline design (execution stops on invalid output)

This prevents hallucinated conclusions and ensures repeatable results.

---

## Known Limitations

* OCR accuracy depends on scan quality.
* Thermal images do not explicitly label rooms; area mapping is heuristic.
* Severity logic is intentionally simplified for transparency.
* No historical inspection data is used.

---

## Improvements With More Time

* Weighted severity scoring model
* Confidence scores per observation
* Better spatial alignment of thermal images to rooms
* Automated DDR PDF generation
* Audit logging for traceability
* Unit tests for reasoning logic
* Historical trend analysis

---

## Notes

This project intentionally avoids frontend development to focus on the AI workflow, validation, and diagnostic reasoning layers, as required by the assignment.

---

## Final Output

The primary deliverable is:

```
data/diagnostic.json
```

This structured diagnostic data can be rendered into a client-facing DDR using any downstream formatting layer (Markdown, PDF, web).

---

If you’d like next, I can help you with:

✅ `requirements.txt`
✅ Loom speaking outline
✅ final DDR generator
✅ interview prep

Just tell me 👍
