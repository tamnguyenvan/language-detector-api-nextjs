import os
import logging
from pathlib import Path
from functools import wraps

from flask import Flask, request, jsonify
from mediapipe.tasks import python
from mediapipe.tasks.python import text

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the language detector
data_dir = Path(__file__).resolve().parent / "data"
detector_path = str(data_dir / "detector.tflite")
base_options = python.BaseOptions(model_asset_path=detector_path)
options = text.LanguageDetectorOptions(base_options=base_options)
detector = text.LanguageDetector.create_from_options(options)

logger.info("Language detector initialized successfully.")

def check_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("X-RapidAPI-Proxy-Secret")
        if not auth_header:
            logger.warning(f"Authorization header missing. IP: {request.remote_addr}")
            return jsonify({"success": False, "error": "Authorization header is missing"}), 401

        # Uncomment the following lines when ready to implement full auth check
        token = os.getenv("API_KEY")
        if not auth_header == token:
            logger.warning(f"Invalid authorization header. IP: {request.remote_addr}")
            return jsonify({"success": False, "error": "Invalid authorization header"}), 401

        logger.info(f"Request authorized. IP: {request.remote_addr}")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/detect", methods=["POST"])
@check_auth
def detect_language():
    data = request.json
    input_text = data.get("text", "")

    if not input_text:
        logger.warning("Request received with no text to analyze.")
        return jsonify({"error": "No text provided"}), 400

    logger.info(f"Received request to analyze text: {input_text[:50]}...")  # Log first 50 chars for privacy

    try:
        # Perform language detection
        detection_result = detector.detect(input_text)

        # Process the detection result
        results = []
        for detection in detection_result.detections:
            results.append({
                "language_code": detection.language_code,
                "probability": round(detection.probability, 2)
            })

        logger.info(f"Language detection successful. Detected {len(results)} language(s).")
        return jsonify({"results": results})

    except Exception as e:
        logger.error(f"Error occurred during language detection: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred during language detection"}), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"500 error: {str(error)}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

@app.route("/ping")
def ping():
    return "ok", 200

if __name__ == "__main__":
    logger.info("Starting the Flask application...")
    app.run(debug=True)
    logger.info("Flask application stopped.")