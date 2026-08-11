from pickle import TRUE
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.graphs.rag_state import RAGState
from app.services.llm import llm
from app.schemas.rag import RAGQuestionClassification, RAGSource
from app.core.config import settings
from app.services.knowledge_search import search_knowledge

question_classifier = llm.with_structured_output(
    RAGQuestionClassification,
    method="json_schema",
    strict=True
)

classification_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Decide si la pregunta debe consultar la base de conocimiento interna. "
            "Devuelve requires_retrieval=True para preguntas factuales, técnicas, "
            "operativas o documentales que puedan beneficiarse de información "
            "almacenada en la base de conocimiento, aunque también puedas conocer "
            "la respuesta por conocimiento general. "
            "Devuelve requires_retrieval=False únicamente para saludos, conversación "
            "general, interacción social o peticiones que claramente no necesitan "
            "consultar documentación."
        ),
        (
            "human",
            "{question}",
        ),
    ]
)

rag_answer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
            "Eres un asistente de CloudOps. " 
            "Usa únicamente el contexto proporcionado. "
            "Si la respuesta no aparece en el contexto, " 
            "indica que no tienes información suficiente."
            )
        ),
        (
            "human",
            ( 
                "context:\n{context}\n\n"
                "question:\n{question}"
            )
        )
    ]
)

direct_answer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un asistente CloudOps. "
            "Responde de forma clara y concisa"
        ),
        (
            "human",
            "{question}"
        ),
    ]
)

output_parser = StrOutputParser()

classification_chain = classification_prompt | question_classifier

rag_answer_chain = rag_answer_prompt | llm | output_parser

direct_answer_chain = direct_answer_prompt | llm | output_parser

async def classify_question(state: RAGState) -> dict:
    classification = await classification_chain.ainvoke(
        {
            "question": state["question"]
        }
    )

    return {
        "requires_retrieval": classification.requires_retrieval
    }

def route_question(state: RAGState) -> str:
    #decide the route based on the state
    if state["requires_retrieval"]:
        return "retrieval"
    return "direct"

async def retrieve_context(state: RAGState) -> dict:
    search_response = await search_knowledge(
        query=state["question"],
        limit=settings.rag_retrieval_limit,
    )

    #create the context
    context_parts = []
    sources = []

    for result in search_response.results:
        context_parts.append(result.content)
        result_source = RAGSource(file_name=result.metadata["file_name"], chunk_index=result.metadata["chunk_index"])
        sources.append(result_source)

    context = "\n\n".join(context_parts)

    return {
        "context": context,
        "sources": sources
    }

async def generate_answer(state: RAGState) -> dict:
    if state["requires_retrieval"]:
       answer = await rag_answer_chain.ainvoke(
            {
                "question": state["question"],
                "context": state["context"]
            }
        )
    else:
        answer = await direct_answer_chain.ainvoke(
            {
                "question": state["question"],
            }
        )
    return{
        "answer": answer
    }

def validate_answer(state: RAGState) -> dict:
    if not state["answer"].strip():
        return {
            "is_valid": False
        }
    if state["requires_retrieval"] is True and not state["context"].strip():
        return {
            "is_valid": False
        }

    return {
        "is_valid": True
    }