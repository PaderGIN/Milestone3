from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from service.ml_service import qa_service

app = FastAPI(title="Axiomus QA API")

class QARequest(BaseModel):
    question: str

class QAResponse(BaseModel):
    answer: str
    score: float
    context: Optional[str] = None

@app.on_event("startup")
def startup_event():
    qa_service.load_model()

@app.post("/predict", response_model=QAResponse)
def predict_endpoint(request: QARequest):
    try:
        result = qa_service.predict(question=request.question)
        return QAResponse(
            answer=result['answer'],
            score=result['score'],
            context=result.get('context')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def get_stats():
    try:
        plot_buf = qa_service.generate_analytics_plot()
        if plot_buf:
            return Response(content=plot_buf.getvalue(), media_type="image/png")
        else:
            return {"error": "Not enough data yet. Ask some questions first!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}