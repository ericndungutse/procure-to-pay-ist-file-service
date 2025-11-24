
import json
from typing import Any, Dict

from logger_config import log, logger
from services.purchaseOrderService import PurchaseOrderService


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    log("Lambda invocation received")

    try:
        # Parse event body (API Gateway sends body as JSON string)
        # For async invocation or SQS, event might already be the purchase_request dict
        if isinstance(event.get("body"), str):
            purchase_request = json.loads(event["body"])
        elif "body" in event:
            purchase_request = event["body"]
        else:
            # Direct invocation - event is the purchase_request itself
            purchase_request = event
        
        proforma_url = purchase_request.get("proforma") or purchase_request.get("proforma_url")
        if not proforma_url:
            raise ValueError("Missing 'proforma' URL in request")
        
        # Process purchase order
        log(f"Processing purchase order for request {purchase_request.get('id')}")
        service = PurchaseOrderService()
        result = service.create_purchase_order(
            purchase_request,
            proforma_url=proforma_url,
        )
        
        log(f"Purchase order generated successfully: {result['pdf_url']}")
        
        # Return success response
        # For async invocation, this response may not be returned to caller
        response = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Purchase order generated successfully",
                "purchase_order_id": str(purchase_request.get("id")),
                "pdf_url": result["pdf_url"]
            }),
        }
        
        log("Lambda invocation completed successfully")
        return response
        
    except json.JSONDecodeError as exc:
        logger.error(f"Invalid JSON in request body: {exc}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON in request body"}),
        }
    except Exception as exc:
        logger.error(f"Error in Lambda handler: {exc}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error processing purchase order"}),
        }

