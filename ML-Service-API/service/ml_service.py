import json
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline

print(">>> ML SERVICE MODULE IMPORTED")

class QAInference:
    def __init__(self, model_path="./DNN_Model", kb_path="./knowledge_base.json"):
        self.pipeline = None
        self.model_path = model_path
        self.kb_path = kb_path
        self.documents = None
        self.vectorizer = None
        self.doc_vectors = None

    def load_model(self):
        print(">>> STARTING LOAD_MODEL...")
        try:

            print(">>> Loading JSON Knowledge Base...")
            if not os.path.exists(self.kb_path):
                print(f"!!! ERROR: Knowledge base file not found at {self.kb_path}")
            else:
                with open(self.kb_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    self.documents = [item["text"].replace("Agent:", "").strip() for item in data]

                if self.documents:
                    self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
                    self.doc_vectors = self.vectorizer.fit_transform(self.documents)
                    print(f">>> SUCCESS: Loaded {len(self.documents)} clean facts into memory.")
                else:
                    print("!!! WARNING: Documents list is empty!")

            print(f">>> Loading Model from: {self.model_path}...")

            device = -1

            tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            model = AutoModelForQuestionAnswering.from_pretrained(self.model_path)

            self.pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer, device=device)
            print(">>> Model loaded successfully!")

        except Exception as e:
            print(f"!!! CRITICAL STARTUP ERROR: {e}")
            pass

    def retrieve_context(self, question: str):
        if not self.documents or self.vectorizer is None:
            return None

        question_vec = self.vectorizer.transform([question])
        similarities = cosine_similarity(question_vec, self.doc_vectors).flatten()
        best_idx = similarities.argmax()
        score = similarities[best_idx]

        print(f">>> Best match score: {score:.4f}")

        if score <= 0.05:
            return None

        return self.documents[best_idx]

    def predict(self, question: str):
        if not self.pipeline:
            self.load_model()
            if not self.pipeline:
                return {"answer": "System Error: Model not loaded.", "score": 0.0, "context": None}

        context = self.retrieve_context(question)
        if not context:
            return {
                "answer": "I don't have information about this in my UPM database.",
                "score": 0.0,
                "context": None
            }

        result = self.pipeline(
            question=question,
            context=context,
            handle_impossible_answer=False
        )

        result['context'] = context

        return result

qa_service = QAInference()