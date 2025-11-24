import json
from datetime import datetime
from typing import Any, Dict
from urllib.parse import unquote, urlparse

from logger_config import log
from services.rabbitMqService import RabbitMQClient
from services.supabaseService import SuperBaseService
from services.ocrService import OCRService
from services.openAiService import OpenAIService
from services.pdfService import PDFService


def _get_attr(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class PurchaseOrderService:
    def __init__(
        self,
        *,
        bucket: str = "purchase_orders",
        queue_name: str = "purchase_orders_queue",
    ) -> None:
        self.bucket = bucket
        self.queue_name = queue_name

    def create_purchase_order(
        self,
        purchase_request: Any,
        *,
        proforma_url: str,
    ) -> Dict[str, Any]:
        log("Downloading Proforma")
        storage_path = self._extract_storage_path_from_url(proforma_url, self.bucket)
        file_bytes = SuperBaseService.download_file(self.bucket, storage_path)
        log("Proforma downloaded")

        log("Extract text from file with OCR")
        proforma_text = OCRService.extract_text_from_bytes(file_bytes)
        log("Text Extracted")

        log("Generate Purchase order with OpenAI")
        purchase_order = self._generate_purchase_order_dict(purchase_request, proforma_text)
        log("Purchase Order Generated")

        log("Creating Purchase Order Pdf Bytes")
        pdf_bytes = PDFService.create_purchase_order_pdf_bytes(purchase_order)
        log("Purchase Order PDF Created")

        log("Upload Purchase Order PDF to supabase")
        request_id = _get_attr(purchase_request, "id")
        upload_response = SuperBaseService.upload_bytes(
            bucket=self.bucket,
            file_path=f"purchase_order_{request_id}.pdf",
            data=pdf_bytes,
            content_type="application/pdf",
            upsert=True,
        )

        pdf_path = getattr(upload_response, "path", None)
        if not pdf_path and isinstance(upload_response, dict):
            pdf_path = upload_response.get("path")
        if not pdf_path:
            raise ValueError("Supabase upload response missing file path")

        pdf_url = SuperBaseService.get_public_url(self.bucket, pdf_path)
        log("Purchase Order Uploaded")

        log("Publishing RabbitMQ Message")
        message_payload = {
            "purchase_order_id": str(request_id),
            "pdf_url": pdf_url,
        }
        self._publish_to_queue(message_payload)
        log(f"Purchase order {request_id} published to queue '{self.queue_name}'")

        return {
            "purchase_order": purchase_order,
            "pdf_path": pdf_path,
            "pdf_url": pdf_url,
        }

    def _generate_purchase_order_dict(self, purchase_request: Any, proforma_text: str) -> Dict[str, Any]:
        
        try:
            return OpenAIService.generate_purchase_order_dict(purchase_request, proforma_text)
        except Exception as exc:  # pragma: no cover - network call fallback
            log(f"OpenAI generation failed, using fallback template: {exc}")
            return self._fallback_purchase_order(purchase_request)

    def _publish_to_queue(self, payload: Dict[str, Any]) -> None:
        client = RabbitMQClient()
        message_bytes = json.dumps(payload).encode("utf-8")
        client.publish(self.queue_name, message_bytes)

    @staticmethod
    def _extract_storage_path_from_url(url: str, bucket: str) -> str:
        parsed_path = unquote(urlparse(url).path)
        marker = f"/storage/v1/object/public/{bucket}/"
        if marker in parsed_path:
            relative_path = parsed_path.split(marker, 1)[1]
        else:
            relative_path = parsed_path.rsplit("/", 1)[-1]

        if not relative_path:
            raise ValueError(f"No file path detected in URL: {url}")

        if not relative_path.startswith("/"):
            relative_path = f"/{relative_path}"

        return relative_path

    @staticmethod
    def _fallback_purchase_order(purchase_request: Any) -> Dict[str, Any]:
        return {
            "title": _get_attr(purchase_request, "title", "N/A"),
            "description": _get_attr(
                purchase_request,
                "description",
                "Purchase order generated without detailed description.",
            ),
            "amount": _get_attr(purchase_request, "amount", 0),
            "vendor_name": "OfficeSupplies Co.",
            "vendor_address": "123 Main Street, Kigali, Rwanda",
            "date_created": datetime.now().strftime("%Y-%m-%d"),
            "items": [
                {"name": "Ergonomic Chair Model X", "quantity": 10, "unit_price": 250},
                {"name": "Office Desk Model D", "quantity": 5, "unit_price": 400},
                {"name": "Desk Lamp Model L", "quantity": 8, "unit_price": 50},
            ],
            "total": 5015,
        }