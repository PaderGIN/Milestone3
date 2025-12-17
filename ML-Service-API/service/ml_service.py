import json
import logging
import os
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print(">>> ML SERVICE MODULE IMPORTED")

class QAInference:
    def __init__(self, model_path="./DNN_Model", kb_path="./knowledge_base.json"):
        self.pipeline = None
        self.model_path = model_path
        self.kb_path = kb_path
        self.documents = []
        self.vectorizer = None
        self.doc_vectors = None
        self.history = []

    def load_model(self):
        print(">>> STARTING LOAD_MODEL...")
        try:
            if not os.path.exists(self.kb_path):
                print(f"!!! ERROR: Knowledge base file not found at {self.kb_path}")
            else:
                print(f"v Knowledge base file found at {self.kb_path}")

            print(">>> Loading Transformers...")
            device = -1
            tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            model = AutoModelForQuestionAnswering.from_pretrained(self.model_path)
            self.pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer, device=device)

            print(">>> Loading JSON...")
            with open(self.kb_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.documents = [item["text"] for item in data]

            if self.documents:
                self.vectorizer = TfidfVectorizer(stop_words='english')
                self.doc_vectors = self.vectorizer.fit_transform(self.documents)
                print(f">>> SUCCESS: Loaded {len(self.documents)} documents into memory.")
            else:
                print("!!! WARNING: Documents list is empty!")

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

        print(f">>> Best match score: {score}")

        if score <= 0.0:
            return None

        original_text = self.documents[best_idx]
        return f"Agent: {original_text}"

    def predict(self, question: str):
        if not self.pipeline:
            self.load_model()
            if not self.pipeline:
                return {"answer": "System Error: Model not loaded.", "score": 0.0, "context": None}

        context_with_prefix = self.retrieve_context(question)

        if not context_with_prefix:
            return {
                "answer": "I don't have information about this in my UPM database.",
                "score": 0.0,
                "context": None
            }

        results = self.pipeline(
            question=question,
            context=context_with_prefix,
            top_k=3,
            max_answer_len=60,
            handle_impossible_answer=False
        )

        final_result = None
        if isinstance(results, list):
            sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)

            for res in sorted_results:
                clean_ans = res['answer'].replace("Agent", "").strip(": ").strip()
                if len(clean_ans) > 3:
                    final_result = res
                    break

            if not final_result:
                final_result = sorted_results[0]
        else:
            final_result = results

        if "answer" in final_result:
            final_result["answer"] = final_result["answer"].replace("Agent", "").strip(": ").strip()

        final_result['context'] = context_with_prefix.replace("Agent: ", "")

        if 'score' in final_result:
            self.history.append(final_result['score'])

        return final_result

    def generate_analytics_plot(self):
        if not self.history:
            return None

        sns.set_theme(style="whitegrid")

        fig = plt.figure(figsize=(12, 8))
        gs = fig.add_gridspec(2, 2)

        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.history, marker='o', linestyle='-', color='#2c3e50', linewidth=2, markersize=8)
        ax1.set_title('Confidence Trend (Real-time)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Confidence Score')
        ax1.set_xlabel('Request Sequence ID')
        ax1.set_ylim(0, 1.05)
        ax1.set_xticks(range(len(self.history)))

        ax2 = fig.add_subplot(gs[1, 0])
        sns.histplot(self.history, bins=np.linspace(0, 1, 11), color='#3498db', edgecolor='black', ax=ax2)
        ax2.set_title('Confidence Distribution', fontsize=12)
        ax2.set_xlabel('Score Bucket')
        ax2.set_xlim(0, 1.0)

        ax3 = fig.add_subplot(gs[1, 1])
        ax3.axis('off')

        total_req = len(self.history)
        avg_conf = np.mean(self.history)
        max_conf = np.max(self.history)
        min_conf = np.min(self.history)

        text_str = (
            f"📊 SESSION STATS\n\n"
            f"Total Requests:  {total_req}\n"
            f"Avg Confidence:  {avg_conf:.2%}\n"
            f"Max Confidence:  {max_conf:.2%}\n"
            f"Min Confidence:  {min_conf:.2%}"
        )

        ax3.text(0.5, 0.5, text_str,
                 fontsize=16,
                 fontfamily='monospace',
                 ha='center', va='center',
                 bbox=dict(boxstyle="round,pad=1", facecolor="#ecf0f1", edgecolor="#bdc3c7"))

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        return buf

qa_service = QAInference()