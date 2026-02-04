# HTML to PDF Converter Service

A Flask-based microservice that converts HTML files stored in AWS S3 to PDF documents using `wkhtmltopdf`.

## Features

- Downloads HTML files from a specified S3 bucket.
- Converts HTML to PDF with customizable options (A2 size, margins, etc.).
- Uploads the generated PDF back to S3.
- Returns a public URL for the generated PDF.
- Dockerized for easy deployment.

## Prerequisites

- Python 3.9+
- `wkhtmltopdf` installed on the system (if running locally).
- AWS Account with S3 access.

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd wkhtml_pdf
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```

2.  Update `.env` with your AWS credentials:
    ```ini
    AWS_ACCESS_KEY_ID=your_access_key_id
    AWS_SECRET_ACCESS_KEY=your_secret_access_key
    AWS_REGION=us-west-1
    ```

## Usage

### Running Locally

```bash
python app.py
```

The server will start at `http://localhost:5000`.

### Running with Docker

1.  Build the Docker image:
    ```bash
    docker build -t html-to-pdf-service .
    ```

2.  Run the container:
    ```bash
    docker run -p 5000:5000 --env-file .env html-to-pdf-service
    ```

### API Endpoint

**POST** `/convert-html-to-pdf`

**Request Body:**

```json
{
  "s3_uri": "s3://your-bucket-name/path/to/file.html"
}
```

**Response:**

```json
{
  "pdf_s3_url": "https://your-bucket-name.s3.amazonaws.com/path/to/file.pdf"
}
```

## Notes

- The service uses `wkhtmltopdf` with specific options for layout.
- Ensure the S3 bucket has appropriate permissions for reading and writing.
