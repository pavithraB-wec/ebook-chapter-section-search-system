from flask import Flask, request, render_template, redirect, url_for, session
from datetime import timedelta
import os, json, re, time
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# =================================
# SESSION CONFIG
# =================================
app.secret_key = "supersecretkey"
app.permanent_session_lifetime = timedelta(minutes=30)

# =================================
# CONFIG (Render Safe)
# =================================
UPLOAD_FOLDER = "/tmp/uploads"
DATA_FOLDER = "/tmp/data"
DATA_FILE = os.path.join(DATA_FOLDER, "processed_data.json")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# =================================
# HOME
# =================================
@app.route("/")
def home():
    return redirect(url_for("search_page"))

# =================================
# SEARCH PAGE
# =================================
@app.route("/search")
def search_page():
    return render_template("search.html", results=None)

# =================================
# LIBRARY (SESSION BASED)
# =================================
@app.route("/library")
def library_page():
    user_files = session.get("uploaded_files", [])
    return render_template("library.html", books=user_files)

# =================================
# DELETE BOOK (SESSION SAFE)
# =================================
@app.route("/delete/<filename>", methods=["POST"])
def delete_book(filename):

    user_files = session.get("uploaded_files", [])

    if filename not in user_files:
        return redirect(url_for("library_page"))

    # Remove PDF file
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Remove from JSON
    with open(DATA_FILE, "r", encoding="utf8") as f:
        all_books = json.load(f)

    updated_books = [
        book for book in all_books
        if book["book"] + ".pdf" != filename
    ]

    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(updated_books, f, indent=4)

    # Remove from session
    user_files.remove(filename)
    session["uploaded_files"] = user_files
    session.modified = True

    return redirect(url_for("library_page"))

# =================================
# UPLOAD (GET + POST)
# =================================
@app.route("/upload", methods=["GET", "POST"])
def upload_page():

    if request.method == "POST":

        file = request.files.get("file")

        if not file or file.filename == "":
            return render_template("upload.html", message="No file selected")

        try:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            reader = PyPDF2.PdfReader(filepath)

            structured_data = {
                "book": file.filename.replace(".pdf", ""),
                "chapters": []
            }

            current_chapter = None

            for page_no, page in enumerate(reader.pages, start=1):

                text = page.extract_text()
                if not text:
                    continue

                lines = text.split("\n")

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    if re.match(r"(?i)^(chapter\s+\d+|\d+\.\s+)", line):

                        current_chapter = {
                            "chapter_title": line,
                            "sections": []
                        }

                        structured_data["chapters"].append(current_chapter)

                    elif current_chapter:
                        current_chapter["sections"].append({
                            "text": line,
                            "page": page_no
                        })

            # Save structured data
            with open(DATA_FILE, "r", encoding="utf8") as f:
                all_books = json.load(f)

            all_books.append(structured_data)

            with open(DATA_FILE, "w", encoding="utf8") as f:
                json.dump(all_books, f, indent=4)

            # Track uploaded files in session
            if "uploaded_files" not in session:
                session["uploaded_files"] = []

            session["uploaded_files"].append(file.filename)
            session.modified = True

            return render_template("upload.html", message="Book uploaded successfully")

        except Exception as e:
            return render_template("upload.html", message=f"Error: {str(e)}")

    return render_template("upload.html")

# =================================
# SEARCH QUERY (SESSION FILTERED)
# =================================
@app.route("/search_query")
def search_query():

    query = request.args.get("q")

    if query:
        query = re.sub(r"[^a-zA-Z0-9\s]", " ", query)

    if not query:
        return render_template("search.html", results=None)

    start = time.time()

    with open(DATA_FILE, "r", encoding="utf8") as f:
        all_books = json.load(f)

    user_files = session.get("uploaded_files", [])

    documents = []
    section_map = []

    for data in all_books:

        if data["book"] + ".pdf" not in user_files:
            continue

        for chapter in data["chapters"]:
            for sec in chapter["sections"]:
                documents.append(sec["text"])
                section_map.append({
                    "book": data["book"],
                    "chapter": chapter["chapter_title"],
                    "text": sec["text"],
                    "page": sec["page"]
                })

    if not documents:
        return render_template("search.html", results=[], query=query, message="No data available")

    vectorizer = TfidfVectorizer(stop_words="english", lowercase=True)
    tfidf_matrix = vectorizer.fit_transform(documents)
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix)[0]

    ranked = sorted(
        list(zip(section_map, scores)),
        key=lambda x: x[1],
        reverse=True
    )

    ranked = [r for r in ranked if r[1] > 0]

    if not ranked:
        return render_template("search.html", results=[], query=query, message="No matches found")

    results = []

    for item, score in ranked[:10]:

        snippet = item["text"]

        snippet = re.sub(
            rf"\b({re.escape(query)})\b",
            r"<mark>\1</mark>",
            snippet,
            flags=re.IGNORECASE
        )

        results.append({
            "book": item["book"],
            "chapter": item["chapter"],
            "snippet": snippet,
            "page": item["page"],
            "score": round(float(score), 4)
        })

    end = time.time()

    return render_template(
        "search.html",
        results=results,
        count=len(results),
        time_ms=round((end-start)*1000, 2),
        query=query
    )

# =================================
# CLEAR SESSION (AUTO CLEAN)
# =================================
@app.route("/clear_session")
def clear_session():

    user_files = session.get("uploaded_files", [])

    if user_files:

        with open(DATA_FILE, "r", encoding="utf8") as f:
            all_books = json.load(f)

        updated_books = []

        for book in all_books:

            if book["book"] + ".pdf" in user_files:

                file_path = os.path.join(UPLOAD_FOLDER, book["book"] + ".pdf")
                if os.path.exists(file_path):
                    os.remove(file_path)

            else:
                updated_books.append(book)

        with open(DATA_FILE, "w", encoding="utf8") as f:
            json.dump(updated_books, f, indent=4)

    session.clear()

    return redirect(url_for("upload_page"))

# =================================
# RUN
# =================================
if __name__ == "__main__":
    app.run(debug=True)