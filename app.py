import warnings
import logging
import asyncio
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from auth import APIKeyMiddleware
from pdf2image import convert_from_bytes
from io import BytesIO
import base64

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(APIKeyMiddleware)

async def convert_whole_pdf(pdf_content: bytes, page_numbers: list[int]):
    """
    Convert the entire PDF and extract selected pages as Base64 images.
    """
    try:
        logger.info("Starting full PDF conversion...")
        images = convert_from_bytes(pdf_content, fmt="png", grayscale=True)
        logger.info("PDF conversion complete.")

        selected_images = {
            f"page_{i}": base64.b64encode(BytesIO().write(img.save(BytesIO(), format="PNG"))).decode("utf-8")
            for i, img in enumerate(images, start=1) if i in page_numbers
        }

        return selected_images

    except Exception as e:
        logger.error(f"Error in convert_whole_pdf: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def convert_single_page(pdf_content: bytes, page: int):
    """
    Convert a single PDF page to an image and return it as a Base64 string.
    """
    try:
        images = convert_from_bytes(pdf_content, fmt="png", first_page=page, last_page=page, grayscale=True)
        if images:
            img_io = BytesIO()
            images[0].save(img_io, format="PNG")
            img_io.seek(0)

            return {f"page_{page}": base64.b64encode(img_io.getvalue()).decode("utf-8")}
        return {}

    except Exception as e:
        logger.error(f"Error processing page {page}: {e}")
        return {}

async def convert_each_page(pdf_content: bytes, page_numbers: list[int]):
    """
    Convert multiple PDF pages concurrently.
    """
    try:
        logger.info(f"Starting conversion for pages: {page_numbers}")

        # Process each page concurrently
        tasks = [convert_single_page(pdf_content, page) for page in page_numbers]
        results = await asyncio.gather(*tasks)

        # Combine results into a single dictionary
        combined_results = {k: v for result in results for k, v in result.items()}

        logger.info("Conversion completed.")
        return combined_results

    except Exception as e:
        logger.error(f"Error in convert_each_page: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def get_frontend():
    return {"message": "Hello World"}

@app.post("/convert_pdf")
async def convert_pdf_to_images(
    file: UploadFile = File(...),
    pages: str = Form(...)
):
    """
    Endpoint to convert PDF to images based on selected pages.
    """
    try:
        # Parse and sort unique page numbers
        page_numbers = sorted(set(map(int, pages.split(','))))

        logger.info(f"Received file: {file.filename}, extracting pages: {page_numbers}")

        # Read the PDF file
        pdf_content = await file.read()

        # Convert the specified pages
        images = await convert_each_page(pdf_content=pdf_content, page_numbers=page_numbers)

        return images

    except Exception as e:
        logger.error(f"Error in convert_pdf_to_images: {e}")
        raise HTTPException(status_code=500, detail=str(e))
