from fastapi import APIRouter, Request
import joblib
import pandas as pd
import os

router = APIRouter()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "notebooks", "model.joblib")

@router.post("/predict")
async def predict(request: Request):
    data = await request.json()
    # Expecting a list of dicts (records)
    df = pd.DataFrame(data)
    if not os.path.exists(MODEL_PATH):
        return {"error": "Model not found. Train it first."}
    model = joblib.load(MODEL_PATH)
    preds = model.predict(df)
    return {"predictions": preds.tolist()}
