"""RAG and Analysis service using Gemini and retrieved chunks."""

from google import genai
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.services.embedding_service import vector_store


from app.models.schemas import ChatResponse, RiskAnalysisResponse, SourceCitationModel

def _get_genai_client():
    """Helper to initialize GenAI client."""
    settings = get_settings()
    if not settings.gemini_api_key:
        raise AppError("Gemini API key is missing. Set GEMINI_API_KEY.", status_code=500)
    
    return genai.Client(api_key=settings.gemini_api_key)


def _format_context(chunks: list[dict]) -> str:
    """Format chunks into a context string."""
    context_parts = []
    for i, chunk in enumerate(chunks):
        page = chunk["metadata"].get("page_number", "Unknown")
        text = chunk["text"]
        context_parts.append(f"--- Chunk {i+1} (Page {page}) ---\n{text}")
    return "\n\n".join(context_parts)


def answer_question(query: str, document_name: str | None = None) -> ChatResponse:
    """Answer a user question using RAG."""
    chunks = vector_store.query_chunks(query=query, n_results=5, document_name=document_name)
    if not chunks:
        return ChatResponse(
            answer="No relevant context found in the document.",
            citations=[],
            confidence_score="Low"
        )

    context = _format_context(chunks)
    client = _get_genai_client()
    
    prompt = f"""You are an expert AI Engineering Document Assistant.
Answer the user's question based strictly on the provided context.
If the answer is not in the context, say "I cannot answer this based on the provided document" to prevent hallucination.
Provide the answer, list the citations (page numbers and a short snippet), and give a confidence score (Low, Medium, High).

Context:
{context}

Question: {query}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-3.6-flash", 
            contents=prompt
        )
        answer_text = response.text
    except Exception as e:
        raise AppError(f"Failed to generate answer from Gemini API: {str(e)}", status_code=502)
    

    # Simple parsing of citations for the response object
    citations = [
        SourceCitationModel(
            page_number=c["metadata"].get("page_number", 0),
            text_snippet=c["text"][:100] + "..."
        ) for c in chunks
    ]
    
    return ChatResponse(
        answer=answer_text,
        citations=citations,
        confidence_score="High" if "cannot answer" not in answer_text.lower() else "Low"
    )


def analyze_risk(document_name: str | None = None) -> RiskAnalysisResponse:
    """Perform risk and compliance analysis on the document."""
    # Retrieve general top chunks for "risk and compliance"
    query = "risk compliance requirements legal obligations liabilities warnings"
    chunks = vector_store.query_chunks(query=query, n_results=8, document_name=document_name)
    
    if not chunks:
        return RiskAnalysisResponse(risks=[], compliance_issues=[], citations=[])

    context = _format_context(chunks)
    client = _get_genai_client()
    
    prompt = f"""You are a strict compliance and risk analysis expert.
Review the following document context and identify:
1. Potential engineering or business risks.
2. Compliance or regulatory issues.
Format your output cleanly as a list of risks and a list of compliance issues.
Only rely on the provided context to avoid hallucinations.

Context:
{context}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-3.6-flash", 
            contents=prompt
        )
        analysis_text = response.text
    except Exception as e:
        raise AppError(f"Failed to generate analysis from Gemini API: {str(e)}", status_code=502)
    

    # We will just parse the text into a simple list by splitting lines or return the raw text 
    # For robust production, use structured output or function calling. 
    # Here we simulate the split based on typical markdown lists.
    
    risks = []
    compliance = []
    
    current_section = "risks"
    for line in analysis_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "compliance" in line.lower() or "regulatory" in line.lower():
            current_section = "compliance"
            continue
        if line.startswith("-") or line.startswith("*") or (line and line[0].isdigit() and line[1] == "."):
            clean_line = line.lstrip("-*1234567890. ")
            if current_section == "risks":
                risks.append(clean_line)
            else:
                compliance.append(clean_line)

    # Fallback if parsing failed
    if not risks and not compliance:
        risks.append(analysis_text)
        
    citations = [
        SourceCitationModel(
            page_number=c["metadata"].get("page_number", 0),
            text_snippet=c["text"][:100] + "..."
        ) for c in chunks
    ]
    
    return RiskAnalysisResponse(
        risks=risks,
        compliance_issues=compliance,
        citations=citations
    )
