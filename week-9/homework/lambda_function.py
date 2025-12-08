import json
from io import BytesIO
from urllib import request

import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL_PATH = "hair_classifier_empty.onnx"
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
TARGET_SIZE = (200, 200)


def download_image(url: str) -> Image.Image:
    """Download an image from URL and ensure RGB mode."""
    with request.urlopen(url) as resp:
        buffer = resp.read()
    return Image.open(BytesIO(buffer)).convert("RGB")


def prepare_image(img: Image.Image, target_size=TARGET_SIZE) -> np.ndarray:
    """Resize, normalize (ImageNet), and return NCHW float32 tensor with batch dim."""
    img = img.resize(target_size, Image.NEAREST)
    arr = np.array(img).astype(np.float32) / 255.0  # HWC, [0,1]
    arr = np.transpose(arr, (2, 0, 1))               # CHW
    arr = (arr - IMAGENET_MEAN[:, None, None]) / IMAGENET_STD[:, None, None]
    return np.expand_dims(arr, axis=0)               # NCHW


def predict(url: str) -> float:
    session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    img = download_image(url)
    tensor = prepare_image(img)
    output = session.run(None, {input_name: tensor})[0]
    return float(output.squeeze())


def lambda_handler(event, context):
    url = event.get("url") if isinstance(event, dict) else None
    if not url:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "url is required"}),
        }
    pred = predict(url)
    return {
        "statusCode": 200,
        "body": json.dumps({"prediction": pred}),
    }

