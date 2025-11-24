import uuid
from types import SimpleNamespace
from logger_config import log
from services.purchaseOrderService import PurchaseOrderService

# # Simulate a User object (normally from accounts.models.User)
sample_user = SimpleNamespace(
    id=uuid.uuid4(),
    full_name="John Doe"
)

# Create a sample PurchaseRequest
sample_purchase_request = SimpleNamespace(
    id=uuid.uuid4(),
    title="Office Chairs Purchase",
    description="Requesting 10 ergonomic office chairs for the HR department.",
    amount=2500,
    created_by=sample_user,
    proforma="https://gnkiycezfddbmigtdjrz.supabase.co/storage/v1/object/public/purchase_orders/sample_proforma.pdf"
)


def main() -> None:
    service = PurchaseOrderService()
    result = service.create_purchase_order(
        sample_purchase_request,
        proforma_url=sample_purchase_request.proforma,
    )
    log(f"Purchase order PDF available at {result['pdf_url']}")


if __name__ == "__main__":
    main()