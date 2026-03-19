from flask import render_template, Flask, request, Response, g
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST
)
from flipkart.data_ingestion import DataIngestor
from flipkart.rag_chain import RAGChainBuilder
from dotenv import load_dotenv
from functools import wraps
import time
import traceback

load_dotenv()

# =========================
# 🔥 CORE METRICS
# =========================

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5]
)

ACTIVE_REQUESTS = Gauge(
    "active_requests",
    "Number of active requests"
)

ERROR_COUNT = Counter(
    "app_errors_total",
    "Total application errors",
    ["endpoint"]
)

# =========================
# 🚀 API PERFORMANCE METRICS
# =========================

api_calls = Counter(
    'api_calls_total',
    'Total API calls',
    ['service', 'endpoint', 'status']
)

api_latency = Histogram(
    'api_latency_seconds',
    'API call latency',
    ['service', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

api_errors = Counter(
    'api_errors_total',
    'API errors',
    ['service', 'error_type']
)

concurrent_requests = Gauge(
    'concurrent_api_requests',
    'Number of concurrent API requests',
    ['service']
)

# =========================
# 🧠 LLM / RAG METRICS
# =========================

RAG_LATENCY = Histogram(
    "rag_chain_latency_seconds",
    "RAG chain response time",
    buckets=[0.1, 0.5, 1, 2, 5, 10]
)

VECTOR_DB_LATENCY = Histogram(
    "vector_db_latency_seconds",
    "Vector DB query latency",
    ["operation"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5]
)

# =========================
# 🎯 DECORATOR (FIXED)
# =========================

def track_api_call(service: str, endpoint: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            concurrent_requests.labels(service=service).inc()
            start_time = time.time()
            status = 'success'

            try:
                response = func(*args, **kwargs)

                # ✅ Handle Flask response formats
                if isinstance(response, tuple):
                    status_code = response[1]
                    if status_code >= 400:
                        status = 'error'
                else:
                    status_code = 200

                return response

            except Exception as e:
                status = 'error'

                api_errors.labels(
                    service=service,
                    error_type=type(e).__name__
                ).inc()

                raise

            finally:
                duration = time.time() - start_time

                api_latency.labels(
                    service=service,
                    endpoint=endpoint
                ).observe(duration)

                api_calls.labels(
                    service=service,
                    endpoint=endpoint,
                    status=status
                ).inc()

                concurrent_requests.labels(service=service).dec()

        return wrapper
    return decorator


# =========================
# 🚀 INITIALIZATION
# =========================

print("🚀 Initializing DataIngestor...", flush=True)
ingestor = DataIngestor()

print("📦 Loading Vector Store...", flush=True)
vector_store = ingestor.ingest(load_existing=True)

print("🧠 Building RAG Chain...", flush=True)
rag_chain = RAGChainBuilder(vector_store).build_chain()

print("✅ Initialization Complete", flush=True)


# =========================
# 🌐 FLASK APP
# =========================

def create_app():
    app = Flask(__name__)

    # -------------------------
    # BEFORE REQUEST
    # -------------------------
    @app.before_request
    def before_request():
        g.start_time = time.time()
        ACTIVE_REQUESTS.inc()

    # -------------------------
    # AFTER REQUEST
    # -------------------------
    @app.after_request
    def after_request(response):
        try:
            latency = time.time() - getattr(g, "start_time", time.time())
            endpoint = request.url_rule.rule if request.url_rule else request.path

            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(latency)

            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=str(response.status_code)
            ).inc()

        finally:
            ACTIVE_REQUESTS.dec()

        return response

    # -------------------------
    # ROUTES
    # -------------------------

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/get", methods=["POST"])
    @track_api_call(service="rag", endpoint="/get")
    def get_response():
        try:
            user_input = request.form.get("msg", "").strip()

            if not user_input:
                return "Please enter a message.", 400

            with RAG_LATENCY.time():
                with VECTOR_DB_LATENCY.labels(operation="similarity_search").time():

                    result = rag_chain.invoke(
                        {"input": user_input},
                        config={"configurable": {"session_id": "user-session"}}
                    )

            print("✅ DEBUG RESULT:", result, flush=True)

            # ✅ Safe extraction
            if isinstance(result, dict):
                response_text = (
                    result.get("answer")
                    or result.get("output")
                    or result.get("result")
                )
                return response_text if response_text else str(result)

            return str(result)

        except Exception as e:
            print("🔥 ERROR:", str(e), flush=True)
            traceback.print_exc()

            ERROR_COUNT.labels(endpoint="/get").inc()

            return "Internal Server Error. Check logs.", 500

    @app.route("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    @app.route("/health")
    def health():
        return {"status": "healthy"}

    return app


# =========================
# 🟢 RUN APP
# =========================

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)