# 📚 E-Book Chapter and Section Search System

The **E-Book Chapter and Section Search System** is a Flask-based Information Retrieval (IR) application that allows users to upload PDF books and perform intelligent search at the **chapter and section level**.

The system processes uploaded books, extracts textual content, and applies Information Retrieval techniques to find the most relevant sections for a given user query.

Each user session is **isolated**, meaning users can search only within the books uploaded during their own session.

The system implements:

• **Vector Space Model (VSM)**  
• **TF-IDF Weighting**  
• **Cosine Similarity Ranking**

to retrieve highly relevant sections from uploaded books.

## 🎯 Objective of the Application

The main objective of this system is to create an intelligent search platform that can:

• Upload and process PDF books  
• Automatically detect chapters and sections  
• Convert extracted text into TF-IDF vectors  
• Compare user queries with book content  
• Retrieve the most relevant sections  
• Rank results based on similarity score  
• Highlight query terms inside results  
• Display corresponding page numbers  

## 🛠 Tools and Technologies Used

### Backend
| Technology | Purpose | Version |
|------------|---------|---------|
| ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) | Core Language | 3.12+ |
| ![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white) | Web Framework | 2.0+ |
| ![PyPDF2](https://img.shields.io/badge/PyPDF2-FF6B6B?logo=adobeacrobatreader&logoColor=white) | PDF Text Extraction | Latest |
| ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white) | TF-IDF & Similarity | Latest |

### Frontend
| Technology | Purpose |
|------------|---------|
| ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) | Structure |
| ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white) | Styling (Glassmorphism) |
| ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) | Interactions |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| ![Render](https://img.shields.io/badge/Render-46E3B7?logo=render&logoColor=white) | Cloud Deployment |
| ![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white) | Version Control |
| ![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white) | Repository Hosting |

---

## 🙏 Acknowledgements

### Academic
This project is built upon the hard work, support, and encouragement of many individuals and institutions. We would like to express our sincere gratitude to:

- **Women's Engineering College, Lawspet** — For providing a supportive academic environment and the necessary resources to develop and complete this project.
- **Information Science Department** — For providing guidance and foundational knowledge in Information Retrieval concepts and methodologies.
- **Saravanan S** — For valuable mentorship, continuous encouragement, and technical guidance throughout the development of this project.
- **Teammates** — Monika, Ranjini, and Tanushri for their collaboration, ideas, discussions, and contributions during the project development.

### Open Source
This project also benefits from several excellent open-source tools and libraries:

- [Flask](https://flask.palletsprojects.com/) — Lightweight web framework used to build the application.
- [scikit-learn](https://scikit-learn.org/) — Used for implementing TF-IDF vectorization and similarity calculations.
- [PyPDF2](https://pypdf2.readthedocs.io/) — Used for extracting and processing text from PDF documents.

### Additional Thanks
We would also like to thank the open-source developer community for creating and maintaining powerful tools that make projects like this possible.

# 👩‍💻 Author

- [@pavithraB-wec](https://www.github.com/pavithraB-wec)

**Name:** Pavithra B  

**Course:** B.Tech – Information Science and Engineering  

**Year:** III Year  

**College:** Women’s Engineering College  

**Project Title:**  
E-Book Chapter and Section Search System  
(Flask-Based Information Retrieval System)

---

## 🎨 Color Reference

The UI follows a modern **dark gradient theme** with purple and blue accent colors to create a clean and focused reading/search experience.

| Color Role | Hex Code |
|------------|----------|
| Primary Gradient Start | #0F172A |
| Primary Gradient End | #4F46E5 |
| Sidebar Background | #111827 |
| Card / Panel Background | #1F2937 |
| Accent Purple | #8B5CF6 |
| Accent Pink | #EC4899 |
| Button Gradient | #6366F1 → #A855F7 |
| Success / Status | #10B981 |
| Text Primary | #F9FAFB |
| Text Secondary | #9CA3AF |

---

# 🌐 Live Demo

The project is deployed online using **Render**.

https://ebook-chapter-section-search-system.onrender.com

Users can upload books and search within their own session.

---

# 🚀 Project Preview

## 📤 Upload Document

![Upload](images/upload.png)

![Upload Book](images/upload-book.png)

![Book Uploaded](images/book-uploaded.png)

---

## 📚 Library View

![Library](images/library.png)

---

## 🔍 Search Query Result

![Query Result](images/query-result.png)

---

## 📖 Query Highlight Inside Book

![Query in Book](images/query-in-book.png)

---

## ❌ No Matches Found Case

![No Matches](images/no-matches-found-case.png)

---

## ⚙️ Automatic Chapter & Section Extraction

![Extraction](images/chapter-section-extraction.png)

---

## ✅ Book Indexed Successfully

![Book Indexed](images/book-indexed.png)

---

# 🗂 Project Structure

![Project Structure](images/project-structure.png)

---

# ⚙ Installation Steps

### Step 1: Clone Repository

```
git clone https://github.com/pavithraB-wec/ebook-chapter-section-search-system.git
```

---

### Step 2: Navigate to Project Folder

```
cd ebook-chapter-section-search-system
```

---

### Step 3: Install Required Dependencies

```
pip install -r requirements.txt
```

---

# ▶ How to Run the Application

Run the Flask application:

```
py -3.12 app.py
```

You will see:

```
Running on http://127.0.0.1:5000/
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

# 🚀 Key Project Features

✅ Upload PDF Books  

✅ Automatic Chapter Detection  

✅ Section-Level Text Extraction  

✅ TF-IDF Vector Creation  

✅ Cosine Similarity Ranking  

✅ Intelligent Search Results  

✅ Query Highlighting  

✅ Page Number Display  

✅ Session-Based Book Isolation  

✅ Library View for Uploaded Books  

✅ Delete Uploaded Books  

✅ Automatic Cleanup of Session Data  

---

# 🔐 Session-Based Architecture

This system uses **session-based isolation**, meaning:

• Each user can only see books uploaded in their session  
• Uploaded books are **not shared between users**  
• When a user session ends, their uploaded books are automatically cleaned  

Example:

User A uploads:

```
Python.pdf
```

User B uploads:

```
DataScience.pdf
```

User A will **only see Python.pdf**, while User B will **only see DataScience.pdf**.

---

# 🧠 Information Retrieval Algorithms Used

The system implements fundamental IR algorithms including:

### Vector Space Model (VSM)

Documents and queries are represented as vectors in a multi-dimensional space.

---

### TF-IDF (Term Frequency – Inverse Document Frequency)

TF-IDF assigns importance to words based on how frequently they appear in a document relative to the entire dataset.

Formula:

```
TF-IDF = TF × IDF
```

---

### Cosine Similarity

Cosine similarity measures the similarity between the query vector and document vectors.

Formula:

```
Cosine Similarity = (A · B) / (||A|| × ||B||)
```

The sections with the highest similarity scores are ranked as the most relevant results.

---

# 🔍 System Workflow

The system processes queries through the following pipeline:

```
Upload PDF
     ↓
Extract Text from Pages
     ↓
Detect Chapters & Sections
     ↓
Store Structured Data
     ↓
Generate TF-IDF Vectors
     ↓
User Query Processing
     ↓
Cosine Similarity Calculation
     ↓
Rank Results
     ↓
Display Relevant Sections
```
---

# 📌 GitHub Repository

```
https://github.com/pavithraB-wec/ebook-chapter-section-search-system
```

---

## ❓ FAQ

### 1. What is the E-Book Chapter & Section Search System?
It is a web-based application that allows users to upload PDF books and search for specific chapters, sections, or topics using Information Retrieval techniques.

### 2. What types of files can be uploaded?
Currently, the system supports **PDF files** for indexing and searching.

### 3. How does the search work?
The system extracts text from uploaded PDFs and applies **TF-IDF vectorization and cosine similarity** to match the user's query with the most relevant chapters or sections.

### 4. Can I upload multiple documents?
Yes, users can upload multiple PDF documents and manage them through the **Library section**.

### 5. Is the search fast?
Yes. The system uses optimized text indexing methods, allowing search results to be retrieved in **milliseconds**.

### 6. What technologies are used in this project?
The system is built using **Python, Flask, scikit-learn, PyPDF2, HTML, CSS, and JavaScript**.

### 7. Where is the project hosted?
The application is deployed on **Render**, allowing users to access it online.

### 8. Can this system be extended in the future?
Yes. Future improvements may include **semantic search, user authentication, and RAG-based ranking (like DeepRAG)** for better explanations of search results.

---
# ⭐ Conclusion

This project demonstrates a real-world implementation of **Information Retrieval techniques** using Flask, TF-IDF, and Cosine Similarity to perform efficient chapter and section-level search in E-Books.

The system provides fast, structured, and ranked search results while maintaining **session-based isolation and automatic cleanup**, making it scalable for multiple users.

---
