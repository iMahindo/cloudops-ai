from time import perf_counter
from opentelemetry import trace
import inspect

from app.observability.metrics import RAG_NODES_DURATION_SECONDS

tracer = trace.get_tracer(__name__)

def observe_rag_node(node_name, node_func):
    #return the node function will be executed by langgraph
    #Add the metrics to every node without change every function in code
    async def wrapped_node(state):
        start_time = perf_counter()
        try:
            #trace the node
            with tracer.start_as_current_span(f"rag.{node_name}") as span:
                span.set_attribute("rag.node", node_name)

                requires_retrieval = state.get("requires_retrieval")

                if requires_retrieval is not None:
                    span.set_attribute(
                        "rag.requires_retrieval",
                        requires_retrieval
                    )
                    
                #the function could be async or sync
                result = node_func(state)
                #call the node function
                if inspect.isawaitable(result):
                    #result is a coroutine
                    return await result
                #result is the function result
                return result
        finally:
            #update the metrics
            RAG_NODES_DURATION_SECONDS.labels(
                node=node_name
            ).observe(
                perf_counter() - start_time
            )
    
    return wrapped_node