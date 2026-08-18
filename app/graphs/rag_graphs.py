from langgraph.graph import END, START, StateGraph

from app.graphs.rag_nodes import (
    classify_question,
    generate_answer,
    retrieve_context,
    route_question,
    validate_answer,
)
from app.graphs.rag_state import RAGState
from app.observability.rag_utils import observe_rag_node


def build_rag_graph():
    #create the graph
    builder = StateGraph(RAGState)

    #add the nodes as a wrapped functions to allow the metrics addition in rag_utils
    builder.add_node(
        "classify_question",        #name in langgraph
        observe_rag_node(
            "classify_question",    #label metric name
            classify_question       #funtion to be executed
        )
    )
    builder.add_node("retrieve_context", observe_rag_node("retrieve_context",retrieve_context))
    builder.add_node("generate_answer", observe_rag_node("generate_answer", generate_answer))
    builder.add_node("validate_answer", observe_rag_node("validate_answer", validate_answer))

    #Define the start node
    builder.add_edge(START, "classify_question")

    #Define the conditional
    builder.add_conditional_edges(
        "classify_question",
        route_question,
        {
            "retrieval": "retrieve_context",
            "direct": "generate_answer"
        }
    )

    builder.add_edge("retrieve_context", "generate_answer")
    builder.add_edge("generate_answer", "validate_answer")

    #define the end node
    builder.add_edge("validate_answer", END)

    #create the graph compile
    return builder.compile()

rag_graph = build_rag_graph()