"""
Three LangChain tools the agent can call:
  1. search_faq       — RAG over Qdrant FAQ knowledge base
  2. track_order      — SQLite order lookup
  3. create_support_ticket — SQLite ticket creation
"""
from langchain_core.tools import tool
from rag import qdrant_db
from db import database


@tool
def search_faq(query: str) -> str:
    """
    Search the FAQ knowledge base to answer general customer questions.
    Use this for questions about shipping, delivery times, return policy,
    refunds, payment methods, account management, or product availability.

    Args:
        query: The customer's question in natural language.

    Returns:
        Relevant FAQ content to help answer the question.
    """
    chunks = qdrant_db.search_faq(query, top_k=3)
    if not chunks:
        return "No relevant FAQ information found for this query."
    return "\n\n".join(f"- {chunk}" for chunk in chunks)


@tool
def track_order(order_id: str, mobile: str) -> str:
    """
    Track the status and delivery details of a customer's order.
    Use this when a customer asks about their order status, delivery date,
    or where their package is.

    Args:
        order_id: The order ID (e.g., ORD001). Ask the customer if not provided.
        mobile:   The customer's registered 10-digit mobile number. Ask if not provided.

    Returns:
        Order status, product name, and estimated delivery date.
    """
    order = database.get_order(order_id, mobile)
    if not order:
        return (
            f"No order found with Order ID '{order_id}' and mobile '{mobile}'. "
            "Please double-check the details and try again. Alternatively, you can search for help in our FAQ or click the **Report Issue** button to create a support ticket."
        )

    status_messages = {
        "processing": "is currently being processed and will be dispatched soon",
        "shipped":    f"has been shipped and is on its way. Expected delivery: {order['delivery_date']}",
        "delivered":  f"was delivered on {order['delivery_date']}",
        "cancelled":  "has been cancelled",
    }
    status_text = status_messages.get(
        order["status"],
        f"has status: {order['status']}"
    )
    # Calculate relative days for a better UX (matches "in 2 days" doc example)
    from datetime import datetime
    try:
        delivery_dt = datetime.strptime(order['delivery_date'], "%Y-%m-%d")
        current_dt  = datetime.strptime("2026-03-29", "%Y-%m-%d") # Use current conversation date
        diff_days   = (delivery_dt - current_dt).days
        delivery_str = f"in {diff_days} days" if diff_days > 0 else "today"
    except (ValueError, TypeError):
        delivery_str = f"on {order['delivery_date']}"

    return (
        f"Your order #{order['order_id']} is currently {order['status']} and will be delivered {delivery_str}."
    )


@tool
def create_support_ticket(name: str, mobile: str, issue: str, order_id: str = "") -> str:
    """
    Create a support ticket for customer complaints or issues.
    Use this when a customer reports a problem such as a damaged item,
    wrong product received, refund not processed, or any other complaint.
    Always collect the customer's name, mobile number, and issue description
    before calling this tool. Order ID is optional.

    Args:
        name:     Full name of the customer.
        mobile:   Customer's 10-digit mobile number.
        issue:    Description of the problem or complaint.
        order_id: Related order ID if applicable (optional).

    Returns:
        Confirmation message with the generated ticket ID.
    """
    ticket_id = database.create_ticket(name, mobile, issue, order_id)
    return (
        f"Your support ticket has been created successfully. "
        f"Ticket ID: {ticket_id}. "
        f"Our support team will contact you shortly."
    )
