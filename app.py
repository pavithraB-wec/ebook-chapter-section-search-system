from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify
import os, json, re, time, csv
import PyPDF2

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ---------------- INIT ----------------

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DATA_FILE = "data/processed_data.json"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ✅ IMPORTANT FOR RENDER
os.makedirs("uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)

# create empty file if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect(url_for("search_page"))


# ---------------- SEARCH PAGE ----------------

@app.route("/search")
def search_page():
    return render_template("search.html", results=None)


# ---------------- LIBRARY ----------------

@app.route("/library")
def library_page():

    books = []

    if os.path.exists(UPLOAD_FOLDER):

        for f in os.listdir(UPLOAD_FOLDER):

            if f.endswith(".pdf"):
                books.append(f.replace(".pdf", ""))

    return render_template("library.html", books=books)


# ---------------- UPLOAD PAGE ----------------

@app.route("/upload")
def upload_page():
    return render_template("upload.html")


# ---------------- UPLOAD FILE ----------------

@app.route("/upload_file", methods=["POST"])
def upload_file():

    file = request.files["file"]

    if file.filename == "":
        return render_template("upload.html", message="No file selected")

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


            # detect chapter
            if re.match(r"(?i)^chapter\s+\d+", line):

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


    # LOAD EXISTING DATA
    with open(DATA_FILE, "r", encoding="utf8") as f:
        all_books = json.load(f)

    all_books.append(structured_data)

    # SAVE
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(all_books, f, indent=4)


    return render_template("upload.html", message="Book uploaded & indexed successfully")


# ---------------- SEARCH QUERY ----------------

@app.route("/search_query")
def search_query():

    query = request.args.get("q")

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

        return render_template("search.html", results=[], message="No data")


    vectorizer = TfidfVectorizer(stop_words="english")

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

        return render_template(

            "search.html",
            results=[],
            query=query,
            message="No matches found"

        )


    results = []

    query_terms = query.split()


    for item, score in ranked[:10]:

        snippet = item["text"]

        for term in query_terms:

            snippet = re.sub(

                rf"\b({re.escape(term)})\b",
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
        time_ms=round((end-start)*1000,2),
        query=query

    )


# ---------------- DOWNLOAD EXCEL ----------------

@app.route("/download_excel")
def download_excel():

    with open(DATA_FILE,"r",encoding="utf8") as f:

        data=json.load(f)


    file="results.csv"

    with open(file,"w",newline="",encoding="utf8") as f:

        writer=csv.writer(f)

        writer.writerow(["Book","Chapter","Text","Page"])


        for book in data:

            for chapter in book["chapters"]:

                for sec in chapter["sections"]:

                    writer.writerow([

                        book["book"],
                        chapter["chapter_title"],
                        sec["text"],
                        sec["page"]

                    ])


    return send_file(file,as_attachment=True)


# ---------------- DOWNLOAD PDF ----------------

@app.route("/download_pdf")
def download_pdf():

    with open(DATA_FILE,"r",encoding="utf8") as f:

        data=json.load(f)


    file="results.pdf"

    c=canvas.Canvas(file,pagesize=A4)

    y=800


    for book in data:

        c.drawString(50,y,book["book"])

        y-=20


        for chapter in book["chapters"]:

            c.drawString(60,y,chapter["chapter_title"])

            y-=20


            if y<50:

                c.showPage()
                y=800


    c.save()

    return send_file(file,as_attachment=True)


# ---------------- PRODUCTION RUN ----------------

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)