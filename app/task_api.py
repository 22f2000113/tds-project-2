# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "httpx",
#     "python-multipart",
#     "requests"
# ]
# ///
import httpx
from fastapi import FastAPI, File, UploadFile, Form, Request,HTTPException
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import requests
import io

app = FastAPI()

# Get the environment variable
api_url = os.getenv('API_URL')
user_name = os.getenv('user_name')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=["*"],  # Allow any headers
)

    
@app.post("/api", response_class=JSONResponse)
async def run_tasks(
    question: str = Form(...), 
    file: Optional[List[UploadFile]] = File(None)
):
    try:
        # Prepare the data for forwarding
        data = {"question": question}

        # If there are files, ensure they are properly formatted for the request
        files = None
        if file:
            files = {
                f"file{i}": (file[i].filename, await file[i].read()) for i in range(len(file))
            }

        headers = {
            "user_name": os.getenv('user_name'),             
         }
        # Use httpx to forward the request to the external API
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, data=data, files=files,headers=headers)

        # Check if the external API's response is JSON serializable
        try:
            response_data = response.json()  # Parse the JSON response from the external API
        except ValueError as e:
            # If the external API does not return JSON, log or handle accordingly
            raise HTTPException(status_code=500, detail="External API did not return valid JSON")

        # If the external API responds with a successful status code
        if response.status_code == 200:
            # You can return the response from the external API directly
            return JSONResponse(content=response_data)

        # If there was an error response from the external API, handle accordingly
        else:
            raise HTTPException(status_code=response.status_code, detail=f"External API error: {response_data}")

    except Exception as e:
        # Catching errors and responding with an error message
        return JSONResponse(
            content={"message": "An error occurred", "detail": str(e)},
            status_code=500
        )