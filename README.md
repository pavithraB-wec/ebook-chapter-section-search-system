# E-Book Chapter and Section Search System

## Project Description
The E-Book Chapter and Section Search System is a Flask-based Information Retrieval (IR) application that allows users to upload PDF books and perform intelligent search at the chapter and section level.

The system processes uploaded books, extracts textual content, and applies Information Retrieval techniques to find the most relevant sections for a given user query.

The system implements:
- Vector Space Model (VSM)
- TF-IDF Weighting
- Cosine Similarity Ranking

to retrieve highly relevant sections from uploaded books.

This project demonstrates a real-world implementation of Information Retrieval techniques using Flask, TF-IDF, and Cosine Similarity to perform efficient chapter and section-level search in e-books.

## Session-Based Architecture
This system uses session-based isolation, meaning:
- Each user can only see books uploaded in their session.
- Uploaded books are not shared between users.
- Session data and uploaded files are cleaned when the session is cleared.

Example:
- User A uploads: `Python.pdf`
- User B uploads: `DataScience.pdf`
- User A sees only `Python.pdf`, while User B sees only `DataScience.pdf`.

## Key Project Features
- Upload PDF books
- Automatic chapter detection
- Section-level text extraction
- TF-IDF vector creation
- Cosine similarity ranking
- Intelligent search results
- Query highlighting
- Page number display
- Session-based book isolation
- Library view for uploaded books
- Delete uploaded books
- Session cleanup support

## Tools and Technologies
- Python
- Flask
- PyPDF2
- Scikit-learn
- HTML
- CSS
- JSON

## How to Run
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run the app:
```bash
py -3.12 app.py
```
3. Open:
```text
http://127.0.0.1:5000
```

## Search Pipeline
1. Upload PDF
2. Extract text
3. Detect chapter/section structure
4. Build TF-IDF vectors
5. Compute cosine similarity
6. Rank relevant sections
7. Display results with page mapping
