from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route('/detect-stegano', methods=['POST'])
def detect_stegano():
    if 'file' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files['file']
    
    # Process the image and detect steganography here
    # For now, returning a dummy response
    return jsonify({"message": "Steganography detected!", "confidence":9.8})

if __name__ == '__main__':
    app.run(debug=True)
