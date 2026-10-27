
from flask import Flask, request, jsonify
import joblib
import os

from src.extract_urls import extract_urls
from src.url_features import extract_url_features

app = Flask(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")

# Load existing text-only models
models = {
    "decision_tree": joblib.load(
        os.path.join(MODEL_DIR, "decision_tree.pkl")
    ),
    "random_forest": joblib.load(
        os.path.join(MODEL_DIR, "random_forest.pkl")
    ),
    "svm": joblib.load(
        os.path.join(MODEL_DIR, "svm.pkl")
    ),
}

# Load the combined SMS + URL model
combined_model = joblib.load(
    os.path.join(MODEL_DIR, "svm_url_combined.pkl")
)


@app.route("/", methods=["GET"])
def home():
    return "SMS-Based Smishing Detection API is running!"


@app.route("/models", methods=["GET"])
def get_models():
    return jsonify({
        "text_models": list(models.keys()),
        "combined_model": "svm_url_combined"
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please send a JSON request."
        }), 400

    sms_text = data.get("text", "")

    if not isinstance(sms_text, str) or not sms_text.strip():
        return jsonify({
            "error": "Please provide SMS text."
        }), 400

    model_name = data.get("model", "svm_url_combined")

    # Extract URLs from the SMS
    extracted_urls = extract_urls(sms_text)

    # Select the model
    if model_name == "svm_url_combined":
        url_features = (
            extract_url_features(extracted_urls[0])
            if extracted_urls
            else {
                "url_length": 0,
                "uses_https": 0,
                "dot_count": 0,
                "digit_count": 0,
                "special_char_count": 0,
                "has_ip_address": 0,
                "subdomain_count": 0,
            }
        )

        # Keep the column names and structure expected during training
        import pandas as pd

        input_data = pd.DataFrame([{
            "TEXT": sms_text,
            **url_features,
        }])

        prediction = int(combined_model.predict(input_data)[0])

    elif model_name in models:
        prediction = int(models[model_name].predict([sms_text])[0])

    else:
        return jsonify({
            "error": (
                "Choose decision_tree, random_forest, svm, "
                "or svm_url_combined."
            )
        }), 400

    result = "Suspicious" if prediction == 1 else "Legitimate"

    return jsonify({
        "model": model_name,
        "prediction": prediction,
        "result": result,
        "extracted_urls": extracted_urls,
        "url_count": len(extracted_urls),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

