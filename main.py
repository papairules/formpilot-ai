from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extractor import extract_fields_from_transcript

app = FastAPI()

class TranscriptInput(BaseModel):
    transcript: str

@app.post("/extract-fields")
def extract_fields(input_data: TranscriptInput):
    try:
        fields = extract_fields_from_transcript(input_data.transcript)
        return fields  # ✅ Already a parsed Python list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
