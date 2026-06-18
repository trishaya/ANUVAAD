import sys
import os
import json
import time
from collections import defaultdict

# =====================================================
# Add Project Root
# =====================================================

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from services.model_router import ModelRouter

# =====================================================
# Initialize Router
# =====================================================

router = ModelRouter()

# =====================================================
# Load Dataset
# =====================================================

with open(
    "benchmark/datasets/benchmark_dataset.json",
    "r",
    encoding="utf-8"
) as f:

    dataset = json.load(f)

# =====================================================
# Metrics Storage
# =====================================================

model_times = defaultdict(list)

category_times = defaultdict(list)

routing_correct = 0

fallback_count = 0

total = len(dataset)

# =====================================================
# Benchmark Start
# =====================================================

print("\n========== BENCHMARK ==========\n")

for sample in dataset:

    text = sample["input"]

    category = sample["category"]

    expected_model = sample["expected_model"]

    # =================================================
    # Expected Routing Logic
    # =================================================

    if category in [

        "romanized",
        "code_mixed",
        "english"

    ]:

        routed_model = "Sarvam"

    else:

        routed_model = "IndicTrans"

    # =================================================
    # Translation Direction
    # =================================================

    if category in [

        "romanized",
        "code_mixed",
        "native"

    ]:

        source_lang = "hi"

        target_lang = "en"

    else:

        source_lang = "en"

        target_lang = "hi"

    # =================================================
    # Start Timer
    # =================================================

    start = time.time()

    # =================================================
    # Translation Request
    # =================================================

    result = router.translate(

        text=text,

        source_lang=source_lang,

        target_lang=target_lang
    )

    # =================================================
    # End Timer
    # =================================================

    end = time.time()

    elapsed = round(

        end - start,

        3
    )

    # =================================================
    # Extract Model
    # =================================================

    actual_model = result.get(

        "model_used",

        "Unknown"
    )

    # =================================================
    # Fallback Detection
    # =================================================

    if "Fallback" in actual_model:

        fallback_count += 1

    # =================================================
    # Store Metrics
    # =================================================

    model_times[
        actual_model
    ].append(elapsed)

    category_times[
        category
    ].append(elapsed)

    # =================================================
    # Routing Accuracy
    # =================================================

    if expected_model in actual_model:

        routing_correct += 1

    # =================================================
    # Print Individual Result
    # =================================================

    print(f"INPUT: {text}")

    print(f"CATEGORY: {category}")

    print(f"SOURCE LANG: {source_lang}")

    print(f"TARGET LANG: {target_lang}")

    print(f"EXPECTED MODEL: {expected_model}")

    print(f"ROUTED MODEL: {routed_model}")

    print(f"ACTUAL MODEL USED: {actual_model}")

    print(f"TIME: {elapsed}s")

    print("-" * 60)

# =====================================================
# Final Metrics
# =====================================================

print("\n========== FINAL METRICS ==========\n")

# =====================================================
# Model-wise Latency
# =====================================================

print("MODEL-WISE LATENCY:\n")

for model, times in model_times.items():

    avg = round(

        sum(times) / len(times),

        3
    )

    print(
        f"AVG {model} TIME: {avg}s"
    )

print()

# =====================================================
# Category-wise Latency
# =====================================================

print("CATEGORY-WISE LATENCY:\n")

for category, times in category_times.items():

    avg = round(

        sum(times) / len(times),

        3
    )

    print(
        f"AVG {category.upper()} TIME: {avg}s"
    )

print()

# =====================================================
# Routing Accuracy
# =====================================================

accuracy = round(

    (routing_correct / total) * 100,

    2
)

print(
    f"ROUTING ACCURACY: {accuracy}%"
)

print()

# =====================================================
# Fallback Statistics
# =====================================================

fallback_rate = round(

    (fallback_count / total) * 100,

    2
)

print(
    f"FALLBACK RATE: {fallback_rate}%"
)

print()

# =====================================================
# Benchmark Summary
# =====================================================

print("========== BENCHMARK COMPLETE ==========")