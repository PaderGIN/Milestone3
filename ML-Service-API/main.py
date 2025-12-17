from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from service.ml_service import qa_service

app = FastAPI(title="Axiomus QA API")

class QARequest(BaseModel):
    question: str

class QAResponse(BaseModel):
    answer: str
    score: float

@app.on_event("startup")
def startup_event():
    qa_service.load_model()

@app.post("/predict", response_model=QAResponse)
def predict_endpoint(request: QARequest):
    try:
        result = qa_service.predict(question=request.question)

        if isinstance(result, dict) and "score" in result:
            return QAResponse(answer=result['answer'], score=result['score'])

        return QAResponse(
            answer=result['answer'],
            score=result['score']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}