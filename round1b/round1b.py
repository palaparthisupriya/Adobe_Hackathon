import os
import json
import fitz  # PyMuPDF
import string
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

stp = set([
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "to", "with",
    "for", "of", "at", "by", "is", "was", "are", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did", "will", "would", "shall", "can",
    "could", "should", "may", "might", "must", "not", "from", "this", "that"
])

def cln(txt):
    txt = txt.lower().translate(str.maketrans("", "", string.punctuation))
    return " ".join([w for w in txt.split() if w not in stp])

def ext_sec(pdf):
    doc = fitz.open(pdf)
    sec = []

    for pno in range(len(doc)):
        pg = doc[pno]
        blks = pg.get_text("dict")["blocks"]
        for blk in blks:
            if "lines" in blk:
                for ln in blk["lines"]:
                    ltxt = "".join(sp["text"] for sp in ln["spans"]).strip()
                    if len(ltxt) > 3 and not ltxt.isdigit() and ltxt[-1] not in [":", "."]:
                        sec.append({
                            "document": os.path.basename(pdf),
                            "page_number": pno + 1,
                            "section_title": ltxt,
                            "text": ltxt
                        })
    doc.close()
    return sec

def ext_sub(pdf):
    doc = fitz.open(pdf)
    sub = []

    for pno in range(len(doc)):
        pg = doc[pno]
        txt = pg.get_text().strip()
        if txt:
            sub.append({
                "document": os.path.basename(pdf),
                "page_number": pno + 1,
                "refined_text": txt
            })
    doc.close()
    return sub

def scr_sec(sec, qry):
    vec = TfidfVectorizer()
    txts = [cln(s["section_title"]) for s in sec] + [cln(qry)]
    tfidf = vec.fit_transform(txts)
    qvec = tfidf[-1]
    scs = cosine_similarity(tfidf[:-1], qvec).flatten()

    for i, s in enumerate(scs):
        sec[i]["score"] = float(s)
    return sorted(sec, key=lambda x: x["score"], reverse=True)

def scr_sub(sub, qry):
    vec = TfidfVectorizer()
    txts = [cln(s["refined_text"]) for s in sub] + [cln(qry)]
    tfidf = vec.fit_transform(txts)
    qvec = tfidf[-1]
    scs = cosine_similarity(tfidf[:-1], qvec).flatten()

    for i, s in enumerate(scs):
        sub[i]["importance_score"] = float(s)
    return sorted(sub, key=lambda x: x["importance_score"], reverse=True)

def main():
    inp = "input"
    out = "output"
    pth = "persona.json"
    ofl = os.path.join(out, "output.json")

    os.makedirs(out, exist_ok=True)

    with open(pth, "r", encoding="utf-8") as f:
        dat = json.load(f)

    per = dat["persona"]
    job = dat["job_to_be_done"]
    qry = f"{per} {job}"

    sec_all = []
    sub_all = []

    for fn in os.listdir(inp):
        if fn.endswith(".pdf"):
            pdf = os.path.join(inp, fn)
            sec_all.extend(ext_sec(pdf))
            sub_all.extend(ext_sub(pdf))

    top_sec = scr_sec(sec_all, qry)[:5]
    top_sub = scr_sub(sub_all, qry)[:5]

    out_data = {
        "metadata": {
            "persona": per,
            "job_to_be_done": job,
            "input_documents": list({s["document"] for s in sec_all}),
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [
            {
                "document": s["document"],
                "page_number": s["page_number"],
                "section_title": s["section_title"],
                "importance_rank": i + 1
            } for i, s in enumerate(top_sec)
        ],
        "subsection_analysis": [
            {
                "document": s["document"],
                "page_number": s["page_number"],
                "refined_text": s["refined_text"]
            } for s in top_sub
        ]
    }

    with open(ofl, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    print(f"Results written to {ofl}")

if __name__ == "__main__":
    main()
