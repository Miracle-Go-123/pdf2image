# PDF2Image

PDF2Image is a Python-based FastAPI application for converting PDF files into high-quality images (PNG format). It supports multi-page PDFs and allows users to extract specific pages as Base64-encoded images.

## Features

- Convert entire PDFs or specific pages to images.
- Supports concurrent page processing for faster conversions.
- API secured with API key authentication.
- Lightweight and containerized with Docker.

## Requirements

- Python 3.6 or higher
- System dependency: `poppler-utils`
- Python dependencies (see `requirements.txt`):
  - `fastapi`, `uvicorn`, `pdf2image`, `Pillow`, etc.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Miracle-Go-123/pdf2image.git
   cd pdf2image
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install Poppler:
   - **Windows**: [Download Poppler](http://blog.alivate.com.au/poppler-windows/) and add it to PATH.
   - **Linux**:
     ```bash
     sudo apt-get install poppler-utils
     ```
   - **MacOS**:
     ```bash
     brew install poppler
     ```

## Usage

### Running the Application

1. Start the FastAPI server:

   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

2. Access the API at `http://localhost:8000`.

### API Endpoints

- **GET `/`**: Health check endpoint.
- **POST `/convert_pdf`**: Convert PDF to images.
  - **Parameters**:
    - `file` (PDF file): The PDF to convert.
    - `pages` (string): Comma-separated page numbers to extract.
  - **Response**: JSON object with Base64-encoded images.

### Example Request

```bash
curl -X POST "http://localhost:8000/convert_pdf" \
-F "file=@example.pdf" \
-F "pages=1,2,3"
```

### Docker

1. Build the Docker image:

   ```bash
   docker build -t pdf2image .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 --env NEXT_API_KEY=<your_api_key> pdf2image
   ```
