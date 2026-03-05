from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
excel_path = os.path.join(BASE_DIR, "chatbot_dataset.xlsx")

df = pd.read_excel(excel_path)
df = df[["Question", "Answer"]].dropna()

questions = df["Question"].astype(str).tolist()
answers = df["Answer"].astype(str).tolist()

vectorizer = TfidfVectorizer(stop_words="english")
question_vectors = vectorizer.fit_transform(questions)

def get_best_answer(user_question: str, threshold: float = 0.2):
    if not user_question.strip():
        return "Please type or speak a question.", 0.0

    user_vec = vectorizer.transform([user_question])
    sims = cosine_similarity(user_vec, question_vectors)[0]
    best_idx = sims.argmax()
    best_score = float(sims[best_idx])

    if best_score < threshold:
        return "Sorry, contact KL University helpdesk.", best_score

    return answers[best_idx], best_score

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "KLU Voice Chatbot"}

@app.post("/chat")
def chat(query: Query):
    answer, score = get_best_answer(query.question)
    return {"answer": answer, "confidence": score}
