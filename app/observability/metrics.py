from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL =Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status_code"]
)

HTTP_REQUEST_ERRORS_TOTAL =Counter(
    "http_requests_errors_total",
    "Total number of failed HTTP requests",
    ["method", "path"]
)

HTTP_REQUEST_DURATION_SECONDS =Histogram(
    "http_requests_duration_seconds",
    "HTTP requests duration in seconds",
    ["method", "path"]
)

RAG_EXECUTIONS_TOTAL=Counter(
    "rag_executions_total",
    "Total number of RAG executions",
)

RAG_FAILURES_TOTAL=Counter(
    "rag_failures_total",
    "Total number of RAG failures",
)

RAG_DURATION_SECONDS=Histogram(
    "rag_duration_seconds",
    "RAG executions duration in seconds",
)

RAG_NODES_DURATION_SECONDS=Histogram(
    "rag_nodes_duration_seconds",
    "RAG nodes execution duration in seconds",
    ["node"]
)

KNOWLEDGE_SEARCH_TOTAL=Counter(
    "knowledge_search_total",
    "Total number of knowledge search executions"
)

KNOWLEDGE_SEARCH_FAILURES_TOTAL=Counter(
    "knowledge_search_failures_total",
    "Total number of knowledge search failures"
)

KNOWLEDGE_SEARCH_DURATION_SECONDS=Histogram(
    "knowledge_search_duration_seconds",
    "knowledge search executions duration in seconds"
)

KNOWLEDGE_INGESTIONS_TOTAL=Counter(
    "knowledge_ingestions_total",
    "Total number of knowledge ingestions executions",
    ["source_type"]
)

KNOWLEDGE_INGESTIONS_FAILURES_TOTAL=Counter(
    "knowledge_ingestions_failures_total",
    "Total number of knowledge ingestions failures",
    ["source_type"]
)

KNOWLEDGE_INGESTIONS_DURATION_SECONDS=Histogram(
    "knowledge_ingestions_duration_seconds",
    "knowledge ingestions executions duration in seconds",
    ["source_type"]
)

KNOWLEDGE_INGESTIONS_CHUNKS_TOTAL=Counter(
    "knowledge_ingestions_chunks_total",
    "Total number of knowledge ingestions chunks created",
    ["source_type"]
)