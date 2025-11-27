# Procure-to-Pay IST File Service

An AWS Lambda function for processing purchase requests and generating purchase orders. This service extracts data from proforma invoices using OCR, generates structured purchase orders using OpenAI, creates PDF documents, and publishes notifications via RabbitMQ.

## Overview

This service is part of a procure-to-pay workflow that automates purchase order generation:

1. Receives a purchase request with a proforma invoice URL
2. Downloads the proforma invoice PDF from Supabase storage
3. Extracts text content from the PDF using OCR
4. Uses OpenAI to generate a structured purchase order from the extracted text
5. Creates a formatted PDF purchase order document
6. Uploads the generated PDF to Supabase storage
7. Publishes a notification to RabbitMQ with the purchase order details

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  API Gateway /  │────▶│  Lambda Handler  │────▶│  Supabase       │
│  Direct Invoke  │     │                  │◀────│  Storage        │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐
            │  OCR      │ │  OpenAI   │ │  RabbitMQ │
            │  Service  │ │  Service  │ │  Service  │
            └───────────┘ └───────────┘ └───────────┘
```

## Prerequisites

- Python 3.9+
- AWS Lambda runtime environment (for deployment)
- Supabase account with storage bucket configured
- OpenAI API key
- RabbitMQ instance (CloudAMQP or self-hosted)

## Project Structure

```
├── lambda_handler.py        # AWS Lambda entry point
├── main.py                  # Local development entry point
├── run_handler.py           # Script to test Lambda handler locally
├── config.py                # Environment configuration
├── logger_config.py         # Logging configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
├── services/
│   ├── purchaseOrderService.py  # Main service orchestrating the workflow
│   ├── ocrService.py            # PDF text extraction using pdfplumber
│   ├── openAiService.py         # OpenAI integration for purchase order generation
│   ├── pdfService.py            # PDF generation using ReportLab
│   ├── supabaseService.py       # Supabase storage operations
│   └── rabbitMqService.py       # RabbitMQ message publishing
└── purchase_request_json_example.json  # Sample input payload
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
RABBITMQ_URL=amqps://username:password@hostname/vhost
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT model access | Yes |
| `RABBITMQ_URL` | RabbitMQ connection URL (AMQP protocol) | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anonymous or service key | Yes |

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ericndungutse/procure-to-pay-ist-file-service.git
   cd procure-to-pay-ist-file-service
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Local Development

### Running the Main Script

```bash
python main.py
```

This runs a sample purchase order generation using hardcoded test data.

### Testing the Lambda Handler Locally

```bash
python run_handler.py
```

This simulates a Lambda invocation using the sample data in `purchase_request_json_example.json`.

## API Usage

### Lambda Event Format

The Lambda function accepts purchase request data in the following formats:

#### Via API Gateway (HTTP Request)

```json
{
  "body": "{\"id\": \"550e8400-e29b-41d4-a716-446655440000\", \"title\": \"Office Chairs Purchase\", \"description\": \"Requesting 10 ergonomic office chairs for the HR department.\", \"amount\": 2500, \"proforma\": \"https://your-project.supabase.co/storage/v1/object/public/purchase_orders/proforma.pdf\"}"
}
```

#### Direct Lambda Invocation

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Office Chairs Purchase",
  "description": "Requesting 10 ergonomic office chairs for the HR department.",
  "amount": 2500,
  "proforma": "https://your-project.supabase.co/storage/v1/object/public/purchase_orders/proforma.pdf"
}
```

### Request Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | string | Unique identifier for the purchase request | Yes |
| `title` | string | Title of the purchase request | Yes |
| `description` | string | Description of the purchase | Yes |
| `amount` | number | Budget amount for the purchase | Yes |
| `proforma` | string | URL to the proforma invoice PDF in Supabase | Yes |

### Response Format

#### Success (200)

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Purchase order generated successfully\", \"purchase_order_id\": \"550e8400-e29b-41d4-a716-446655440000\", \"pdf_url\": \"https://your-project.supabase.co/storage/v1/object/public/purchase_orders/purchase_order_550e8400.pdf\"}"
}
```

#### Error (400 - Invalid JSON)

```json
{
  "statusCode": 400,
  "body": "{\"error\": \"Invalid JSON in request body\"}"
}
```

#### Error (500 - Internal Error)

```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Internal server error processing purchase order\"}"
}
```

## AWS Lambda Deployment

### Creating the Deployment Package

1. Create a deployment directory:
   ```bash
   mkdir -p deployment
   pip install -r requirements.txt -t deployment/
   ```

2. Copy the source files:
   ```bash
   cp *.py deployment/
   cp -r services deployment/
   ```

3. Create the ZIP package:
   ```bash
   cd deployment
   zip -r ../lambda_function.zip .
   ```

### Lambda Configuration

- **Handler**: `lambda_handler.handler`
- **Runtime**: Python 3.9+
- **Memory**: 512 MB (recommended)
- **Timeout**: 60 seconds (recommended, adjust based on PDF processing needs)
- **Environment Variables**: Configure all required environment variables in the Lambda console

## Services

### PurchaseOrderService

The main orchestration service that coordinates the purchase order workflow:
- Downloads proforma invoices from Supabase
- Extracts text using OCR
- Generates purchase orders via OpenAI
- Creates PDF documents
- Uploads to Supabase
- Publishes to RabbitMQ

### OCRService

Extracts text content from PDF files using `pdfplumber`. Only PDF format is supported.

### OpenAIService

Uses OpenAI's GPT-4o-mini model to generate structured purchase order data from the proforma invoice text and purchase request information.

### PDFService

Generates formatted PDF purchase order documents using ReportLab, including:
- Header with purchase order details
- Vendor information
- Line items table with quantities and prices
- Total amount

### SupabaseService

Handles file operations with Supabase storage:
- Download files from storage buckets
- Upload files with configurable content types
- Generate public URLs for uploaded files

### RabbitMQService

Publishes purchase order completion notifications to RabbitMQ queues for downstream processing.

## RabbitMQ Message Format

When a purchase order is successfully generated, a message is published to the configured queue:

```json
{
  "purchase_order_id": "550e8400-e29b-41d4-a716-446655440000",
  "pdf_url": "https://your-project.supabase.co/storage/v1/object/public/purchase_orders/purchase_order_550e8400.pdf"
}
```

## License

This project is proprietary. All rights reserved.
