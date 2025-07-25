import os
import json
import re
import fitz  # PyMuPDF
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
lgr = logging.getLogger(__name__)

class PDFOutlineExtractor:
    def __init__(self):
        self.h1p = [
            r'^(Chapter|CHAPTER)\s+\d+',
            r'^第\d+章',
            r'^[IVX]+\.\s+[A-Z]',
            r'^\d+\.\s+[A-Z][a-z]',
            r'^[A-Z][A-Z\s]{5,}$',
            r'^PART\s+[IVX]+',
            r'^SECTION\s+[A-Z]',
            r'^[A-Z][a-zA-Z\s]{3,50}$',  # NEW - General capital headings
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$'  # NEW - Title case
        ]
        self.h2p = [
            r'^\d+\.\d+\s+[A-Z]',
            r'^[A-Z]\.\s+[A-Z]',
            r'^(Section|SECTION)\s+\d+',
            r'^第\d+節',
            r'^\d+\.\s+[a-z]',
        ]
        self.h3p = [
            r'^\d+\.\d+\.\d+\s+',
            r'^[a-z]\)\s+[A-Z]',
            r'^\([a-z]\)\s+[A-Z]',
            r'^•\s+[A-Z]',
            r'^-\s+[A-Z]',
        ]
        self.cmp = {
            'h1': [re.compile(pat) for pat in self.h1p],
            'h2': [re.compile(pat) for pat in self.h2p],
            'h3': [re.compile(pat) for pat in self.h3p]
        }
        self.skc = re.compile(r'^\d+$|^page\s+\d+|^figure\s+\d+|^table\s+\d+|^www\.|^http|^\s*$', re.IGNORECASE)

    def extract_title_from_first_page(self, doc) -> str:
        try:
            lines = doc[0].get_text().split('\n')
            for line in lines[:8]:
                line = line.strip()
                if 5 < len(line) <= 150 and not line.isdigit() and len(line.split()) <= 15:
                    return line
        except:
            pass
        return "Untitled Document"

    def extract_outline_from_pdf(self, path: str) -> dict:
        try:
            doc = fitz.open(path)
            total_pages = len(doc)
            title = self.extract_title_from_first_page(doc)

            # Estimate average font size
            font_sizes = []
            for pno in range(min(total_pages, 5)):
                blocks = doc[pno].get_text("dict")["blocks"]
                for block in blocks[:3]:
                    if "lines" in block:
                        for line in block["lines"][:2]:
                            for span in line["spans"][:2]:
                                if span["size"] > 6:
                                    font_sizes.append(span["size"])
            avg_font = sum(font_sizes) / len(font_sizes) if font_sizes else 12

            headings = []
            seen = set()

            for pno in range(total_pages):
                try:
                    blocks = doc[pno].get_text("dict")["blocks"]
                    for block in blocks:
                        if "lines" in block:
                            for line in block["lines"]:
                                text = ''.join([span["text"] for span in line["spans"]]).strip()
                                max_size = max([span["size"] for span in line["spans"]], default=0)

                                if len(text) < 3 or len(text) > 200 or max_size == 0 or self.skc.match(text):
                                    continue

                                level = None
                                for k, patterns in self.cmp.items():
                                    if any(p.match(text) for p in patterns):
                                        level = k.upper()
                                        break

                                if not level:
                                    ratio = max_size / avg_font
                                    if ratio >= 1.4:
                                        level = 'H1'
                                    elif ratio >= 1.25:
                                        level = 'H2'
                                    elif ratio >= 1.15:
                                        level = 'H3'
                                    elif text.istitle() and len(text.split()) <= 10:
                                        level = 'H2'
                                    elif text.isupper() and len(text.split()) <= 8:
                                        level = 'H1'

                                if level:
                                    clean_text = re.sub(r'\s+', ' ', text)
                                    key = (clean_text, pno + 1)
                                    if key not in seen:
                                        seen.add(key)
                                        headings.append({
                                            "level": level,
                                            "text": clean_text,
                                            "page": pno + 1
                                        })
                except Exception as e:
                    lgr.warning(f"Page {pno + 1} error: {e}")
                    continue

            doc.close()
            headings.sort(key=lambda x: (x["page"], {"H1": 1, "H2": 2, "H3": 3}.get(x["level"], 4)))
            return {"title": title, "outline": headings}

        except Exception as e:
            lgr.error(f"Processing error in {path}: {e}")
            return {"title": "Error Processing Document", "outline": []}


# MAIN EXECUTION
if __name__ == "__main__":
    print(" Adobe Hackathon Round 1A - Batch PDF Outline Extractor (Docker Ready)")

    input_dir = "/app/input"
    output_dir = "/app/output"

    extractor = PDFOutlineExtractor()
    total = 0
    success = 0
    failed = []

    start = time.time()

    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            total += 1
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file.replace(".pdf", ".json"))
            print(f"\n Processing: {file}")
            try:
                result = extractor.extract_outline_from_pdf(input_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f" Done! Output saved to: {output_path}")
                print(f" Headings found: {len(result['outline'])}")
                print(f" Title: {result['title']}")
                success += 1
            except Exception as e:
                print(f" Failed: {e}")
                failed.append(file)
    print("\n Batch Processing Complete!")
    print(f" Total PDFs processed: {total}")
    print(f" Successfully processed: {success}")
    print(f" Failed files: {failed if failed else 'None'}")
