import json

def save_llm_outputs(outputs, filename):
    """Save a list of LLM outputs (as strings or dicts) to a JSON file."""
    cleaned = []

    for item in outputs:
        if isinstance(item, str):
            cleaned.append({"output": item})
        elif isinstance(item, dict):
            cleaned.append(item)
        else:
            continue  # skip invalid formats

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)

    print(f"✅ Saved {len(cleaned)} outputs to {filename}")

# === Example Usage ===

basic_outputs = [
    {"output": '{"weights": {"Feature": {"Units Sold": 5.1, "Revenue": 3.8}, "Price Decrease": {"Units Sold": 2.4, "Revenue": 1.1}, "Feature + Price Decrease": {"Units Sold": 6.5, "Revenue": null}}}'}
]

conditional_outputs = [
    {"output": '{"weights": {"Feature": {"Units Sold": 4.0, "Revenue": 2.0}, "Price Decrease": {"Units Sold": 3.0, "Revenue": 1.5}, "Feature + Price Decrease": {"Units Sold": 5.5, "Revenue": null}}}'}
]

# Save both
save_llm_outputs(basic_outputs, "preliminary_outputs.json")
save_llm_outputs(conditional_outputs, "conditional_outputs.json")