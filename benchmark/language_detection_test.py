import sys
import os
import json

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from services.indic_lid_detector import IndicLID


# Initialize detector
detector = IndicLID()


with open(
    "benchmark/datasets/language_detection.json",
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


correct = 0
total = len(data)


for item in data:

    text = item["text"]

    expected = item["expected_language"]

    try:

        detected = detector.detect(text)

    except Exception as e:

        detected = f"ERROR: {e}"

    print(f"\nTEXT: {text}")

    print(f"EXPECTED: {expected}")

    print(f"DETECTED: {detected}")

    if detected == expected:

        correct += 1


accuracy = (
    correct / total
) * 100

print(f"\nAccuracy: {accuracy:.2f}%")