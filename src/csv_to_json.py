import csv
import json
import argparse

def csv_to_json(csv_file, json_file, indent, sort_keys, compact):
    with open(csv_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if compact:
        json_str = json.dumps(rows, separators=(",", ":"), ensure_ascii=False)
    else:
        json_str = json.dumps(rows, indent=indent, sort_keys=sort_keys, ensure_ascii=False)

    with open(json_file, mode="w", encoding="utf-8") as f:
        f.write(json_str)

    print(f"Converted {csv_file} → {json_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CSV to JSON with options")
    parser.add_argument("csv_file", help="Path to the input CSV file")
    parser.add_argument("json_file", help="Path to the output JSON file")
    parser.add_argument("--indent", type=int, default=4, help="Indentation level for pretty JSON (default: 4)")
    parser.add_argument("--sort-keys", action="store_true", help="Sort JSON object keys alphabetically")
    parser.add_argument("--compact", action="store_true", help="Output compact JSON (no spaces, overrides indent)")

    args = parser.parse_args()
    csv_to_json(args.csv_file, args.json_file, args.indent, args.sort_keys, args.compact)
