"""Run the Lambda handler directly with sample data."""

import json
from types import SimpleNamespace
from lambda_handler import handler

# Load sample purchase request
with open("purchase_request_json_example.json", "r") as f:
    purchase_request = json.load(f)

# Create mock Lambda event
event = {
    "body": json.dumps(purchase_request)
}

# Create mock context
context = SimpleNamespace(
    function_name="purchase-order-handler",
    function_version="$LATEST",
    invoked_function_arn="arn:aws:lambda:us-east-1:123456789012:function:test",
    memory_limit_in_mb=512,
    aws_request_id="test-request-id",
)

# Run handler
print("Running Lambda handler...")
response = handler(event, context)

print(f"\nResponse Status: {response['statusCode']}")
print(f"Response Body: {response['body']}")
print("\nHandler returned. Background processing continues...")

