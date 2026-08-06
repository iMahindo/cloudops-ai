from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.exceptions import RAGServiceException
from app.core.logging import get_logger
from app.schemas.rag import RAGResponse,RAGSource
from app.core.config import settings
from app.services.knowledge_search import search_knowledge
from app.services.llm import llm

logger = get_logger(__name__)

async def generate_rag_response(question: str) -> RAGResponse:
    if not question.strip():
        raise RAGServiceException(
            "Question cannot be empty"
        )
    try:
        #Get the semantic search response
        search_response = await search_knowledge(query = question, limit= settings.rag_retrieval_limit)

        #create the context
        context_parts = []
        sources = []

        for result in search_response.results:
            context_parts.append(result.content)
            result_source = RAGSource(file_name=result.metadata["file_name"], chunk_index=result.metadata["chunk_index"])
            sources.append(result_source)

        context = "\n\n".join(context_parts)

        #create the prompt template 
        rag_prompt = ChatPromptTemplate.from_messages(
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

        output_parser = StrOutputParser()

        #create the chain
        rag_chain = rag_prompt | llm | output_parser

        #execute the chain
        answer = await rag_chain.ainvoke(
            {
                "context": context,
                "question": question
            }
        )

        return RAGResponse(
            answer=answer,
            sources=sources
        )
    except Exception as exc:
        logger.exception("Failed to generate RAG response")
        raise RAGServiceException(
            "Failed to generate RAG response"
        ) from exc
