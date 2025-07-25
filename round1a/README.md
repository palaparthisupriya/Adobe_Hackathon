#  Adobe Hackathon – Round 1A Submission

##  Track: Connecting the Dots (Round 1A)
This submission solves the PDF parsing challenge by extracting a structured representation of a PDF document. The solution is implemented in **Python** using **PyMuPDF**, **pdfplumber**, and **PyPDF2** for precise extraction of:
- Title
- Headings (H1, H2, H3)
- Subheadings and nested structures

##  Problem Understanding

> Given a PDF document, generate a structured output that shows the hierarchy of text content (e.g., Title, H1, H2, H3, etc.) based on visual and semantic cues like font size, boldness, indentation, and position.


##  Key Features

-  **Title Detection**: Based on largest font size and centered text.
-  **Heading Hierarchy Extraction**:
  - H1: Bold & large text
  - H2: Medium size, aligned left
  - H3: Smaller, nested or indented
-  **Library Stack**:
  - `PyMuPDF` (fitz): Visual structure analysis
  - `pdfplumber`: Text position, font size, and line height
  - `PyPDF2`: Metadata handling (if required)
-  **Performance Optimized**: Handles PDFs quickly and efficiently
-  Input & Output folders handled dynamically

##  Folder Structure
round1a/
|--input
   |--sample pdfs
|--output
   |--sample output
|--dockerfile
|--main.py
|--requirements.txt


## Docker Instructions

To build and run the project using Docker:

# Step 1: Build the image
docker build -t adobe-round1a .

# Step 2: Run the container
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output adobe-round1a
