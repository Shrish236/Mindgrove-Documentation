from waitress import serve
from app import app  # Import the Flask application object

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=8050)