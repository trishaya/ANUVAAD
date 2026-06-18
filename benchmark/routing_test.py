import sys
import os
import json
import time

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from services.model_router import ModelRouter


router = ModelRouter()


with open(
    "benchmark/datasets/routing_test.json",
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


correct = 0
total = len(data)


print("\n========== ROUTING BENCHMARK ==========\n")


for item in data:

    category = item["category"]

    text = item["input"]

    expected = item["expected_model"]

    start = time.time()

    # =================================================
    # ROUTING LOGIC TEST
    # =================================================

    if router.is_code_mixed(text):

        routed_model = "Sarvam Translation API"

    elif router.is_roman_text(text):

        routed_model = "Sarvam Translation API"

    elif len(text.split()) > 12:

        routed_model = "IndicTrans"
    else:
        routed_model = "IndicTrans"

    end = time.time()

    latency = round(end - start, 4)

    print(f"CATEGORY: {category}")

    print(f"INPUT: {text}")

    print(f"EXPECTED: {expected}")

    print(f"ROUTED: {routed_model}")

    print(f"LATENCY: {latency}s")

    if routed_model == expected:

        print("RESULT: CORRECT\n")

        correct += 1

    else:

        print("RESULT: WRONG\n")


accuracy = (
    correct / total
) * 100


print("======================================")

print(f"\nRouting Accuracy: {accuracy:.2f}%")