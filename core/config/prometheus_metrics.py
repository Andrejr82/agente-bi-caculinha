from prometheus_client import start_http_server, Counter

# Create a metric to track the number of requests.
REQUEST_COUNT = Counter('request_count', 'App Request Count', ['method', 'endpoint', 'http_status'])

def start_metrics_server(port=8000):
    """
    Starts a Prometheus metrics server.
    """
    start_http_server(port)
