# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "httpx",
#     "python-multipart"
# ]
# ///
import httpx
from fastapi import FastAPI, File, UploadFile, Form
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI()

# Get the environment variable
api_url = os.getenv('API_URL')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=["*"],  # Allow any headers
)


@app.post("/api")
async def question_solver(
    question: str = Form(...),
    file: Optional[List[UploadFile]] = File(None)):

    files = {"file": []}
    for f in file:
        files["file"].append((f.filename, f.file, f.content_type))

    data = {"question": question}
    
    headers = {
        "user_name": os.getenv('user_name'),             
    }
    
    # Make the POST request to the external API using httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, data=data, files=files,headers=headers)

    # Handle the response from the external API
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)