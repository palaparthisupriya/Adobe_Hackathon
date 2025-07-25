# Adobe Hackathon – Round 1B Submission

##  Overview
This solution compares the structural similarity between two PDF documents based on their headings and layout structure. It uses font size patterns and cosine similarity to determine if the documents share a similar format.

---

## Tech Stack
- Python
- PyMuPDF (`fitz`)
- scikit-learn (`TfidfVectorizer`, `cosine_similarity`)
- Docker

---

##  Folder Structure

round1b/
|--input
   |--sample pdfs
|--output
   |--output.json
|--dockerfile
|--persona.json
|--requirements.txt
|--round1b.py //main script


## Docker Instructions

###  Step 1: Build the Docker image
docker build -t adobe-round1b .
###  Step 2: Run
docker run -v $(pwd)/input:/app/input adobe-round1b
