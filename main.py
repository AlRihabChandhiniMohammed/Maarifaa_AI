from flask import Flask, request, jsonify, render_template
import chromadb
import uuid
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
USE_CLOUD = False  

if USE_CLOUD:
    client = chromadb.CloudClient(
        api_key=os.getenv("CHROMA_API_KEY"),
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DATABASE")
    )
else:
    client = chromadb.PersistentClient(path="./chromadb_data")

collection = client.get_or_create_collection(name="test_maarifaa")

with open("Maarifaa.txt", "r", encoding="utf-8") as f:
    content = f.read()
documents = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
if collection.count() == 0:
    collection.add(
        ids=[str(uuid.uuid4()) for _ in documents],
        documents=documents,
        metadatas=[{"chunk": i} for i in range(len(documents))]
    )
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_question = request.json.get("question", "").strip()
    if not user_question:
        return jsonify({"answer": "Please ask a valid question."})
    results = collection.query(
        query_texts=[user_question],
        n_results=8
    )
    docs = results["documents"][0] if results["documents"] else []
    answer = "\n\n".join(docs) if docs else "No relevant information found."

    return jsonify({"answer": answer})
if __name__ == "__main__":
    app.run(debug=True)
