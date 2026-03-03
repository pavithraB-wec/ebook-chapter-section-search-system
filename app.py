from flask import Flask, request, render_template, redirect, url_for
import os, json, re, time, shutil
import PyPDF2

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "processed_data.json")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ===============================
# AUTO CLEAN ON LOCAL STARTUP
# ===============================
if not os.environ.get("RENDER"):  
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    if os.path.exists(DATA_FOLDER):
        shutil.rmtree(DATA_FOLDER)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


# ===============================
# HOME
# ===============================
@app.route("/")
def home():
    return redirect(url_for("search_page"))


# ===============================
# SEARCH PAGE
# ===============================
@app.route("/search")
def search_page():
    return render_template("search.html", results=None)


# ===============================
# LIBRARY
# ===============================
@app.route("/library")
def library_page():
    books = []
    for f in os.listdir(UPLOAD_FOLDER):
        if f.endswith(".pdf"):
            books.append(f.replace(".pdf", ""))
    return render_template("library.html", books=books)


# ===============================
# UPLOAD (GET + POST)
# ===============================
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

                    # FLEXIBLE CHAPTER DETECTION
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

            with open(DATA_FILE, "r", encoding="utf8") as f:
                all_books = json.load(f)

            all_books.append(structured_data)

            with open(DATA_FILE, "w", encoding="utf8") as f:
                json.dump(all_books, f, indent=4)

            return render_template("upload.html", message="Book uploaded successfully")

        except Exception as e:
            return render_template("upload.html", message=f"Error: {str(e)}")

    return render_template("upload.html")


# ===============================
# SEARCH QUERY (GET ONLY)
# ===============================
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

    documents = []
    section_map = []

    for data in all_books:
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

if __name__ == "__main__":
    app.run(debug=True)