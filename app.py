from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory, abort
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


def _normalize_text(value):
    return re.sub(r"\s+", " ", (value or "").strip()).lower()


def _highlight_query_in_text(text, query):
    tokens = re.findall(r"[A-Za-z0-9]+", query or "")
    if not tokens:
        return text

    # Match the full query phrase only, allowing whitespace/hyphen variations.
    pattern = r"(?<!\w)" + r"[\s\-]+".join(re.escape(token) for token in tokens) + r"(?!\w)"
    return re.sub(
        pattern,
        lambda match: f"<mark>{match.group(0)}</mark>",
        text,
        flags=re.IGNORECASE
    )


def _query_pattern(query):
    tokens = re.findall(r"[A-Za-z0-9]+", query or "")
    if not tokens:
        return None
    return r"(?<!\w)" + r"[\s\-]+".join(re.escape(token) for token in tokens) + r"(?!\w)"


def _lexical_boost(query, text):
    if not query or not text:
        return 0.0

    pattern = _query_pattern(query)
    if pattern and re.search(pattern, text, flags=re.IGNORECASE):
        return 1.0

    query_tokens = set(re.findall(r"[A-Za-z0-9]+", query.lower()))
    text_tokens = set(re.findall(r"[A-Za-z0-9]+", text.lower()))
    if not query_tokens:
        return 0.0

    overlap_ratio = len(query_tokens & text_tokens) / len(query_tokens)
    if overlap_ratio >= 1.0:
        return 0.25
    if overlap_ratio >= 0.6:
        return 0.12
    return 0.0

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


@app.route("/view/<filename>")
def view_book(filename):
    user_files = session.get("uploaded_files", [])
    if filename not in user_files:
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, filename)

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
                            "page": page_no,
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

            # Replace existing indexed data for the same file to avoid duplicate rankings.
            all_books = [b for b in all_books if b.get("book") != structured_data["book"]]
            all_books.append(structured_data)

            with open(DATA_FILE, "w", encoding="utf8") as f:
                json.dump(all_books, f, indent=4)

            # Track uploaded files in session
            if "uploaded_files" not in session:
                session["uploaded_files"] = []

            if file.filename not in session["uploaded_files"]:
                session["uploaded_files"].append(file.filename)
            session.modified = True

            return render_template("upload.html", message="the book is idexed successfully")

        except Exception as e:
            return render_template("upload.html", message=f"Error: {str(e)}")

    return render_template("upload.html")

# =================================
# SEARCH QUERY (SESSION FILTERED)
# =================================
@app.route("/search_query")
def search_query():

    raw_query = request.args.get("q", "")
    query = re.sub(r"[^a-zA-Z0-9\s\-]", " ", raw_query)
    query = re.sub(r"\s+", " ", query).strip()

    if not query:
        return render_template("search.html", results=None)

    start = time.time()

    with open(DATA_FILE, "r", encoding="utf8") as f:
        all_books = json.load(f)

    user_files = session.get("uploaded_files", [])

    documents = []
    section_map = []

    seen_sections = set()
    for data in all_books:

        if data["book"] + ".pdf" not in user_files:
            continue

        for chapter in data["chapters"]:
            chapter_page = chapter.get("page")
            if chapter_page is None and chapter.get("sections"):
                chapter_page = chapter["sections"][0].get("page")

            # Index chapter titles so heading queries are searchable.
            chapter_key = (
                data["book"],
                chapter["chapter_title"],
                chapter_page,
                _normalize_text(chapter.get("chapter_title", ""))
            )
            if chapter_key[3] and chapter_key not in seen_sections:
                seen_sections.add(chapter_key)
                documents.append(chapter["chapter_title"])
                section_map.append({
                    "book": data["book"],
                    "chapter": chapter["chapter_title"],
                    "text": chapter["chapter_title"],
                    "page": chapter_page or 1
                })

            for sec in chapter["sections"]:
                section_key = (
                    data["book"],
                    chapter["chapter_title"],
                    sec.get("page"),
                    _normalize_text(sec.get("text", ""))
                )
                if section_key in seen_sections or not section_key[3]:
                    continue
                seen_sections.add(section_key)
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

    scored = []
    for item, tfidf_score in zip(section_map, scores):
        boost = _lexical_boost(query, item["text"])
        final_score = float(tfidf_score) + boost
        if final_score > 0:
            scored.append((item, final_score))

    ranked = sorted(
        scored,
        key=lambda x: x[1],
        reverse=True
    )

    unique_ranked = []
    seen_ranked = set()
    for item, score in ranked:
        key = (
            item["book"],
            item["chapter"],
            item["page"],
            _normalize_text(item["text"])
        )
        if key in seen_ranked:
            continue
        seen_ranked.add(key)
        unique_ranked.append((item, score))
    ranked = unique_ranked

    if not ranked:
        return render_template("search.html", results=[], query=query, message="No matches found")

    results = []

    for item, score in ranked[:10]:

        snippet = item["text"]

        snippet = _highlight_query_in_text(snippet, query)

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
        query=raw_query
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
