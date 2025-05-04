from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import tempfile
from enc import classify_and_decrypt

app = Flask(__name__)
CORS(app)

# Load models once when the server starts
model1_path = "models/ResNet.h5"
model2_path = "models/EffecientNetB0.keras"
model1 = load_model(model1_path)
model2 = load_model(model2_path)
print("Both models loaded successfully!")

# Preprocess uploaded image
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array

# Perform ensemble prediction
def ensemble_predict(img_path):
    img_array = preprocess_image(img_path)
    pred1 = model1.predict(img_array)[0][0]
    pred2 = model2.predict(img_array)[0][0]
    final_prediction = (pred1 + pred2) / 2
    label = "Steganographic Image" if final_prediction > 0.5 else "Normal Image"
    confidence = float(final_prediction if final_prediction > 0.5 else 1 - final_prediction)
    print(label, confidence)
    return label, confidence

@app.route('/detect-stegano', methods=['POST'])
def detect_stegano():
    if 'file' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files['file']

    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
        file.save(temp.name)
        img_path = temp.name

    try:
        label, confidence = ensemble_predict(img_path)

        response = {
            "prediction": label,
            "confidence": round(confidence * 100, 2)
        }

        # If image is predicted as steganographic, attempt decryption
        if label == "Steganographic Image":
            result = classify_and_decrypt(img_path)
            response.update({
                "decryption_method": result.get("method"),
                "plain_text": result.get("plain_text")
            })
        print(response)
        return jsonify(response)

    except Exception as e:
        return jsonify({"message": "Prediction failed", "error": str(e)}), 500
    finally:
        os.remove(img_path)

if __name__ == '__main__':
    app.run(debug=True)
