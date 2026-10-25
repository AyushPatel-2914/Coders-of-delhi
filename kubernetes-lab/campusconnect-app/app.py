import argparse, os, signal, socket, sys
from flask import Flask, jsonify

app = Flask(__name__)
DATA_DIR = os.environ.get("DATA_DIR", "/data")
COUNT_FILE = os.path.join(DATA_DIR, "visits.txt")
APP_VERSION = os.environ.get("APP_VERSION", "v1")

def read_count():
    try:
        with open(COUNT_FILE) as f:
            return int(f.read().strip() or 0)
    except FileNotFoundError:
        return 0

def write_count(n):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(COUNT_FILE, "w") as f:
        f.write(str(n))

@app.route("/")
def index():
    n = read_count() + 1
    write_count(n)
    return jsonify(message="Hello from CampusConnect!", visits=n,
                   hostname=socket.gethostname(), pid=os.getpid(),
                   version=APP_VERSION)

@app.route("/health")
def health():
    return jsonify(status="ok")

def handle_sigterm(signum, frame):
    print("Received SIGTERM - shutting down gracefully", flush=True)
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    print(f"Starting CampusConnect {APP_VERSION} on port {args.port}", flush=True)
    app.run(host="0.0.0.0", port=args.port)
