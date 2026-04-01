import re
import json
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
import llm

import config
from memory import session
from agent.tools import search_faq, track_order, create_support_ticket

# ── Routing Prompt ─────────────────────────────────────────────────────────────
# This prompt helps the LLM act as a "Smart Router" to extract details from history.
ROUTING_PROMPT = """You are a routing assistant for an e-commerce support agent.
Analyze the conversation history and the new user message.
Determine the user's intent and extract any available entities.

Available Intents:
- TRACK_ORDER: Seeking status of an order. Needs: order_id, mobile.
- CREATE_TICKET: Reporting an issue or requesting help. Needs: name, mobile, issue.
- FAQ: General questions about policies, returns, shipping, etc.
- GREETING: Hello, hi, etc.
- UNKNOWN: Anything else.

Entity Extraction Rules:
- Issue: ONLY extract if the user provides a specific description (e.g., "product is damaged", "refund not received"). 
- Do NOT extract "I have an issue", "help me", or "want to create a ticket" as the Issue. Leave it as None if no specific problem is stated.
- Order_ID: Look for patterns like ORD001. If missing, return exactly None.
- Mobile: Look for 10-digit numbers. If missing, return exactly None.
- Name: Customer's name. If missing, return exactly None.
- IMPORTANT: Never return placeholder text like "[To be determined]". If a field is missing, return only the word None.

Return your analysis in this EXACT format:
Intent: [INTENT]
Order_ID: [extracted order id or None]
Mobile: [extracted 10-digit mobile or None]
Name: [customer name or None]
Issue: [description of the issue or None]
"""

# ── Agent ─────────────────────────────────────────────────────────────────────

class EcommerceAgent:

    def __init__(self):
        self.llm = llm.get_llm()

    def _parse_routing(self, raw: str):
        """Helper to parse the router LLM's plain-text output into a dict with strict validation."""
        data = {"intent": "UNKNOWN", "order_id": None, "mobile": None, "name": None, "issue": None}
        for line in raw.split("\n"):
            line = line.strip()
            if ":" not in line: continue
            key, val = [x.strip() for x in line.split(":", 1)]
            key_lower = key.lower()

            # Clean Value: Remove brackets if LLM provides them [None]
            val = val.replace("[", "").replace("]", "").strip()
            if "none" in val.lower(): val = None
            
            if key_lower == "intent": data["intent"] = val
            elif key_lower == "order_id" and val:
                # Strictly validate Order ID: Must resemble ORD001
                if re.search(r"ORD\d+", val, re.IGNORECASE):
                    data["order_id"] = val.upper()
            elif key_lower == "mobile" and val:
                # Strictly validate Mobile: Must be digit-like and near 10 chars
                digits = "".join(filter(str.isdigit, val))
                if len(digits) >= 10:
                    data["mobile"] = digits[-10:]
            elif key_lower == "name": data["name"] = val
            elif key_lower == "issue": data["issue"] = val
        return data

    def run(self, session_id: str, user_message: str) -> str:
        """
        Main entry point for the agent.
        1. Save message to history.
        2. Use LLM as a router/extractor based on history.
        3. Execute manual tool logic based on extracted intent.
        """
        # Step 1 — Add and get History
        session.add_human_message(session_id, user_message)
        history = session.get_history(session_id)
        
        # Step 2 — Smart Routing & Extraction
        # We build a list of messages for the router to understand context
        history_text = "\n".join([f"{m.type.upper()}: {m.content}" for m in history[-6:]])
        router_input = f"{ROUTING_PROMPT}\n\nCONVERSATION HISTORY:\n{history_text}\n\nAnalyze the last HUMAN: message."
        
        router_response = self.llm.invoke(router_input)
        analysis = self._parse_routing(router_response.content)
        
        print(f"[Agent] Router analysis: {analysis}")

        # Step 3 — Switch based on Intent and mandatory info
        
        # ── A. ORDER TRACKING ──────────────────────────────────────────────
        if analysis["intent"] == "TRACK_ORDER":
            if analysis["order_id"] and analysis["mobile"]:
                result = track_order.invoke({"order_id": analysis["order_id"], "mobile": analysis["mobile"]})
                final_response = self.llm.invoke(f"Based on this tool result, give a helpful answer:\n{result}\nUser asked: {user_message}")
                session.add_ai_message(session_id, final_response.content)
                return final_response.content
            else:
                return "Please provide both your **Order ID** (e.g., ORD001) and your **10-digit registered mobile number** so I can track your order."

        # ── B. CREATE TICKET ───────────────────────────────────────────────
        # Trigger if the user has an issue and we are collecting info
        if analysis["intent"] == "CREATE_TICKET" or analysis["issue"]:
            if analysis["name"] and analysis["mobile"] and analysis["issue"]:
                result = create_support_ticket.invoke({
                    "name": analysis["name"],
                    "mobile": analysis["mobile"],
                    "issue": analysis["issue"]
                })
                # We return the tool result directly as the AI confirmed it
                session.add_ai_message(session_id, result)
                return result
            else:
                # If they already provided some info, ask for exactly what's missing
                missing = []
                if not analysis["name"]: missing.append("Name")
                if not analysis["mobile"]: missing.append("Mobile Number")
                if not analysis["issue"]: missing.append("Description of the issue")
                
                return f"I'm sorry to hear about this problem. To create a support ticket, please provide your **{', '.join(missing)}**."

        # ── C. FAQ / RAG SEARCH ────────────────────────────────────────────
        # Skip search for simple greetings
        if analysis["intent"] == "GREETING":
            return "Namaste! I am your e-commerce support assistant. How can I help you today? I can track orders, help with returns, or answer policy questions."

        # Default to RAG for anything else
        chunks = search_faq.invoke({"query": user_message})
        final_response = self.llm.invoke(f"Answer concisely using context:\nCONTEXT: {chunks}\nQUESTION: {user_message}")
        session.add_ai_message(session_id, final_response.content)
        return final_response.content


# ── Singleton ─────────────────────────────────────────────────────────────────
agent = EcommerceAgent()
