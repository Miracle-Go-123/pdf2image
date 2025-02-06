#!/usr/bin/env python
import warnings
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth import APIKeyMiddleware
from pdf2image import convert_from_bytes
from io import BytesIO
import base64

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = FastAPI()
app.add_middleware(APIKeyMiddleware)

templates = Jinja2Templates(directory=".")

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/convert_pdf")
async def convert_pdf_to_images(
    file: UploadFile = File(...),
    pages: str = Form(...)
):
    try:
        page_numbers = list(map(int, pages.split(',')))

        pdf_content = await file.read()
        images = convert_from_bytes(pdf_content, fmt="png")

        selected_images = {}
        for i, img in enumerate(images, start=1):
            if i in page_numbers:
                img_io = BytesIO()
                img.save(img_io, format="PNG")
                img_io.seek(0)
                
                # Convert image to Base64
                img_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")
                selected_images[f"page_{i}"] = img_base64

        return selected_images
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))