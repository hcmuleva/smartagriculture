"""
AI model inference - loaded once when Flask starts,
called every time a new scan image arrives.

When AI team hands over the trained model file:
1. Drop tomato_disease_model.keras into the model/ folder
2. Confirm CLASS_NAMES order and IMG_SIZE with them
3. Uncomment the real code below and delete the stub
"""
import numpy as np
import tensorflow as tf
import os

# --- Confirm these 3 values with your AI teammate ---
MODEL_PATH  = os.path.join("model", "tomato_disease_model.keras")
CLASS_NAMES = ["early_blight", "healthy", "late_blight", "mosaic_virus"]  # confirm order
IMG_SIZE    = (160, 160)  # confirm size used during training

# Load model once at startup
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"Model loaded from {MODEL_PATH}")
    else:
        print(f"WARNING: Model file not found at {MODEL_PATH}. Using stub predictions.")


def predict_disease(image_path: str) -> dict:
    """
    Takes path to a leaf image.
    Returns disease name and confidence score.
    """
    if model is None:
        # Stub response when model file not available yet
        return {
            "disease":    "early_blight",
            "confidence": 0.91,
        }

    img  = tf.keras.utils.load_img(image_path, target_size=IMG_SIZE)
    arr  = tf.keras.utils.img_to_array(img)
    arr  = np.expand_dims(arr, axis=0)

    predictions   = model.predict(arr, verbose=0)[0]
    predicted_idx = int(np.argmax(predictions))

    # Normalize disease name to lowercase with underscores
    disease_name = CLASS_NAMES[predicted_idx].lower().replace(" ", "_")

    return {
        "disease":    disease_name,
        "confidence": float(predictions[predicted_idx]),
    }
