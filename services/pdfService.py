import io
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from typing import Any, Dict, List

class PDFService:
    @staticmethod
    def create_purchase_order_pdf_bytes(purchase_order: Dict[str, Any]) -> bytes:
        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=LETTER)
        width, height = LETTER

        margin_x = inch
        margin_y = inch
        line_height = 14
        cursor_y = height - margin_y

        table_width = width - (margin_x * 2)
        col_widths = [
            table_width * 0.4,
            table_width * 0.15,
            table_width * 0.2,
            table_width * 0.25,
        ]
        col_positions = [margin_x]
        for w in col_widths:
            col_positions.append(col_positions[-1] + w)

        def ensure_space(required_height: float) -> None:
            nonlocal cursor_y
            if cursor_y - required_height <= margin_y:
                pdf.showPage()
                cursor_y = height - margin_y

        def draw_text(text: str, font: str = "Helvetica", size: int = 11) -> None:
            nonlocal cursor_y
            wrapped_lines = simpleSplit(text, font, size, table_width)
            for line in wrapped_lines:
                ensure_space(line_height)
                pdf.setFont(font, size)
                pdf.drawString(margin_x, cursor_y, line)
                cursor_y -= line_height

        def draw_spacer(multiplier: float = 1.0) -> None:
            nonlocal cursor_y
            cursor_y -= line_height * multiplier

        def draw_table_row(values: List[Any], header: bool = False) -> None:
            nonlocal cursor_y
            row_height = line_height * 1.5
            ensure_space(row_height)
            pdf.setFont("Helvetica-Bold" if header else "Helvetica", 11)
            y_text = cursor_y - (row_height - line_height + 2)
            for idx, value in enumerate(values):
                text = str(value)
                pdf.drawString(col_positions[idx] + 4, y_text, text)
            pdf.line(margin_x, cursor_y, margin_x + table_width, cursor_y)
            cursor_y -= row_height

        # Header
        draw_text("Purchase Order", font="Helvetica-Bold", size=16)
        draw_spacer(0.5)

        header_fields = [
            ("Title", purchase_order.get("title", "N/A")),
            ("Description", purchase_order.get("description", "N/A")),
            ("Amount", str(purchase_order.get("amount", "N/A"))),
            ("Vendor", purchase_order.get("vendor_name", "N/A")),
            ("Vendor Address", purchase_order.get("vendor_address", "N/A")),
            ("Date Created", purchase_order.get("date_created", "N/A")),
        ]
        for label, value in header_fields:
            draw_text(f"{label}: {value}")

        draw_spacer()
        draw_text("Items", font="Helvetica-Bold", size=13)
        draw_spacer(0.25)

        items: List[Dict[str, Any]] = purchase_order.get("items", [])
        if not items:
            draw_text("No line items provided.")
        else:
            draw_table_row(["Item", "Qty", "Unit Price", "Line Total"], header=True)
            for idx, item in enumerate(items, start=1):
                name = item.get("name", f"Item {idx}")
                quantity = item.get("quantity", "N/A")
                unit_price = item.get("unit_price", "N/A")
                try:
                    line_total_value = float(quantity) * float(unit_price)
                except (TypeError, ValueError):
                    line_total_value = None
                line_total_display = f"{line_total_value:.2f}" if line_total_value is not None else "N/A"
                draw_table_row([name, quantity, unit_price, line_total_display])

        draw_spacer()
        total = purchase_order.get("total")
        if total is not None:
            draw_text(f"Total: {total}", font="Helvetica-Bold", size=12)

        pdf.save()
        pdf_buffer.seek(0)
        return pdf_buffer.read()  # Returns PDF bytes
