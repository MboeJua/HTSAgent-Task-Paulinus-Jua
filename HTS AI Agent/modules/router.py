from .hts_duty import calculate_duty
from .rag_tool import rag_tool_func, rag_chain



def route_query(query: str, chat_history: list = None) -> str:
    q = query.lower()
    if "hts code" in q and ("cost" in q or "price" in q or "$" in q):
        try:
            return calculate_duty(query)
        except Exception as e:
            return f"HTS Duty calculator error: {str(e)}"

    try:
        return rag_tool_func(query, chat_history)
    except Exception as e:
        import traceback
        return f"RAG error:\n{traceback.format_exc()}"

