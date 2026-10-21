
import csv

input_file = "traces-td1.csv"
output_file = "model-question-comparison-en.csv"

columns = [
    "case_id",
    "model_id",
    "trace_file",
    "cell_id",
    "nature",
    "status",
    "value_cents",
    "reference_cents",
    "explanation"
]

rows = []

with open(input_file, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    for trace in reader:
        verdict = trace["verdict"]

        if verdict == "correct":
            explanation = "The generated SQL returned the expected value."
        else:
            explanation = ""

        rows.append({
            "case_id": trace["case_id"],
            "model_id": trace["model_requested"],
            "trace_file": input_file,
            "cell_id": trace["cell_id"],
            "nature": trace["nature"],
            "status": verdict,
            "value_cents": trace["value"],
            "reference_cents": trace["reference"],
            "explanation": explanation
        })

with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print(f"{len(rows)} rows written to {output_file}")
