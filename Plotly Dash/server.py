from waitress import serve
from app import server  # Import the Flask application object

if __name__ == "__main__":
    serve(server, host='0.0.0.0', port=8050)