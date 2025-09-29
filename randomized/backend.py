from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List
from analytics import get_prediction_safe
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictPayload(BaseModel):
    week: int
    month: int
    feature_toggle: bool
    price_decrease_magnitude: float
    competitor_feature_list: List[bool]
    competitor_price_list: List[float]

@app.get("/", response_class=FileResponse)
async def serve_index():
    return FileResponse("frontend/frontend.html")

@app.post("/predict")
async def predict(payload: PredictPayload):
    avg_competitor_feature = sum(payload.competitor_feature_list) > 0
    avg_price_decrease = sum(payload.competitor_price_list) / len(payload.competitor_price_list) if payload.competitor_price_list else 0.0
    result = get_prediction_safe(
        feature_toggle=payload.feature_toggle,
        price_decrease_magnitude=payload.price_decrease_magnitude,
        week=payload.week,
        month=payload.month,
        competitor_feature_toggle=avg_competitor_feature,
        competitor_price_decrease_magnitude=avg_price_decrease
    )
    return {"units": result[0], "revenue": result[1]}

if __name__ == "__main__":
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
