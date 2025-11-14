# cleaner.py
import csv
import json
import os
from collections import Counter, defaultdict
import statistics
import math
from typing import List, Dict, Tuple, Any

# -----------------------
# Helper type definitions
# -----------------------
Row = Dict[str, str]
Table = List[Row]

# -----------------------
# Loading & Saving CSV
# -----------------------
def load_csv(path: str) -> Tuple[List[str], Table]:
    """
    Load CSV into list of rows (each row is dict header -> string value).
    Returns (headers, rows)
    """
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = [dict(row) for row in reader]
    return headers, rows

def save_csv(path: str, headers: List[str], rows: Table) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

# -----------------------
# Type detection helpers
# -----------------------
def infer_cell_type(value: str) -> str:
    """
    Return 'int', 'float', or 'str' depending on content.
    Empty string considered as missing.
    """
    if value is None:
        return 'missing'
    v = value.strip()
    if v == '':
        return 'missing'
    # Try int
    try:
        int(v)
        return 'int'
    except Exception:
        pass
    # Try float
    try:
        float(v)
        return 'float'
    except Exception:
        pass
    return 'str'

def column_inferred_type(values: List[str]) -> str:
    """
    Majority inference for column. If majority numeric -> int/float else str.
    """
    counts = Counter(infer_cell_type(v) for v in values)
    # ignore 'missing' when deciding numeric vs string
    counts_no_missing = {k: v for k, v in counts.items() if k != 'missing'}
    if not counts_no_missing:
        return 'unknown'
    # choose highest count among int/float/str
    most_common = max(counts_no_missing.items(), key=lambda kv: kv[1])[0]
    return most_common

# -----------------------
# Detect missing & duplicates
# -----------------------
def detect_missing(headers: List[str], rows: Table) -> Dict[str, int]:
    missing = {h: 0 for h in headers}
    for r in rows:
        for h in headers:
            v = r.get(h, "")
            if v is None or str(v).strip() == "":
                missing[h] += 1
    return missing

def detect_duplicates(rows: Table) -> Tuple[int, List[int]]:
    """
    Return (duplicates_count, list_of_duplicate_row_indices)
    We treat a duplicate as an exact match of the full row string.
    """
    seen = {}
    duplicate_indices = []
    for i, r in enumerate(rows):
        key = tuple((k, r.get(k, "").strip()) for k in sorted(r.keys()))
        if key in seen:
            duplicate_indices.append(i)
        else:
            seen[key] = i
    return len(duplicate_indices), duplicate_indices

# -----------------------
# Outlier detection (simple)
# -----------------------
def detect_outliers_numeric(values: List[float]) -> List[int]:
    """
    Return indices of values considered outliers using IQR rule (1.5 * IQR).
    Input list may include float('nan') for missing - ignore those.
    """
    clean_values = [v for v in values if v is not None and not math.isnan(v)]
    if len(clean_values) < 4:
        return []
    sorted_vals = sorted(clean_values)
    q1 = statistics.quantiles(sorted_vals, n=4)[0]
    q3 = statistics.quantiles(sorted_vals, n=4)[2]
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outlier_indices = [i for i, v in enumerate(values) if v is not None and not math.isnan(v) and (v < lower or v > upper)]
    return outlier_indices

# -----------------------
# Type conversion utility
# -----------------------
def safe_convert_to_number(s: str) -> float:
    try:
        if s is None:
            return float('nan')
        s2 = s.strip()
        if s2 == '':
            return float('nan')
        # remove common separators like commas
        s3 = s2.replace(',', '')
        return float(s3)
    except Exception:
        return float('nan')

# -----------------------
# Column statistics
# -----------------------
def column_stats(headers: List[str], rows: Table) -> Dict[str, Dict[str, Any]]:
    stats = {}
    for h in headers:
        vals = [r.get(h, "") for r in rows]
        inferred = column_inferred_type(vals)
        non_missing = [v for v in vals if v is not None and str(v).strip() != ""]
        unique_count = len(set(non_missing))
        missing_count = len(vals) - len(non_missing)
        stats[h] = {
            "inferred_type": inferred,
            "non_missing": len(non_missing),
            "missing_count": missing_count,
            "unique_count": unique_count,
        }
        # For numeric columns, compute mean/median/mode
        if inferred in ('int', 'float'):
            numeric = [safe_convert_to_number(v) for v in vals]
            numeric_clean = [v for v in numeric if not math.isnan(v)]
            if numeric_clean:
                try:
                    stats[h].update({
                        "mean": statistics.mean(numeric_clean),
                        "median": statistics.median(numeric_clean),
                        "stdev": statistics.pstdev(numeric_clean) if len(numeric_clean) > 1 else 0.0,
                        "min": min(numeric_clean),
                        "max": max(numeric_clean),
                    })
                except Exception:
                    pass
    return stats

# -----------------------
# Cleaning functions
# -----------------------
def remove_duplicate_rows(rows: Table, duplicate_indices: List[int]) -> Table:
    # remove by index (keep earlier)
    filtered = [r for i, r in enumerate(rows) if i not in set(duplicate_indices)]
    return filtered

def fill_missing_values(headers: List[str], rows: Table, strategy: str = "auto") -> Tuple[Table, Dict[str, Any]]:
    """
    strategy: "auto" -> numeric mean, text mode; "mean", "median", "mode", "empty"
    Returns (new_rows, fill_summary)
    """
    stats = column_stats(headers, rows)
    fill_summary = {}
    new_rows = [dict(r) for r in rows]
    for h in headers:
        inf = stats[h].get("inferred_type", "str")
        missing = stats[h].get("missing_count", 0)
        if missing == 0:
            fill_summary[h] = {"filled_with": None, "count": 0}
            continue
        if strategy == "empty":
            # leave as empty strings
            fill_with = ""
        elif inf in ('int', 'float'):
            # compute mean safely
            vals = [safe_convert_to_number(r.get(h, "")) for r in new_rows]
            numeric = [v for v in vals if not math.isnan(v)]
            if not numeric:
                fill_with = 0
            else:
                if strategy == "median":
                    fill_with = statistics.median(numeric)
                else:
                    # default mean
                    fill_with = statistics.mean(numeric)
        else:
            # mode for strings
            vals = [r.get(h, "") for r in new_rows if r.get(h, "") not in (None, "")]
            if vals:
                try:
                    fill_with = Counter(vals).most_common(1)[0][0]
                except Exception:
                    fill_with = ""
            else:
                fill_with = ""
        # Apply fills
        count = 0
        for r in new_rows:
            v = r.get(h, "")
            if v is None or str(v).strip() == "":
                r[h] = str(fill_with)
                count += 1
        fill_summary[h] = {"filled_with": fill_with, "count": count}
    return new_rows, fill_summary

# -----------------------
# Main pipeline
# -----------------------
def analyze_and_clean(csv_path: str, output_dir: str, fill_strategy: str = "auto") -> Dict[str, Any]:
    headers, rows = load_csv(csv_path)
    total_rows = len(rows)
    missing = detect_missing(headers, rows)
    dup_count, dup_indices = detect_duplicates(rows)
    col_stats = column_stats(headers, rows)

    # detect outliers for numeric columns
    outliers_report = {}
    for h in headers:
        if col_stats[h]['inferred_type'] in ('int', 'float'):
            numeric_vals = [safe_convert_to_number(r.get(h, "")) for r in rows]
            out_idx = detect_outliers_numeric(numeric_vals)
            outliers_report[h] = {
                "count": len(out_idx),
                "indices": out_idx
            }

    # Clean step: remove duplicates, fill missing
    rows_no_dup = remove_duplicate_rows(rows, dup_indices)
    cleaned_rows, fill_summary = fill_missing_values(headers, rows_no_dup, strategy=fill_strategy)

    # Save outputs
    os.makedirs(output_dir, exist_ok=True)
    cleaned_csv_path = os.path.join(output_dir, "cleaned_data.csv")
    save_csv(cleaned_csv_path, headers, cleaned_rows)

    # Create report
    report = {
        "original_file": os.path.basename(csv_path),
        "original_row_count": total_rows,
        "cleaned_row_count": len(cleaned_rows),
        "missing": missing,
        "duplicates_removed": dup_count,
        "duplicate_indices": dup_indices,
        "column_stats": col_stats,
        "outliers": outliers_report,
        "fill_summary": fill_summary,
    }

    # Compute a simple health score: 100 - weighted penalties
    missing_pct = sum(missing.values()) / max(1, total_rows * len(headers)) * 100
    dup_pct = dup_count / max(1, total_rows) * 100
    outlier_pct = sum(v["count"] for v in outliers_report.values()) / max(1, total_rows) * 100
    health_score = max(0, round(100 - (missing_pct * 0.6 + dup_pct * 0.25 + outlier_pct * 0.15)))

    report["health_score"] = health_score

    # write JSON and TXT summary
    json_path = os.path.join(output_dir, "summary.json")
    with open(json_path, "w", encoding='utf-8') as jf:
        json.dump(report, jf, indent=2, ensure_ascii=False)

    txt_path = os.path.join(output_dir, "report.txt")
    with open(txt_path, "w", encoding='utf-8') as tf:
        tf.write(f"Dataset Health Score: {health_score}%\n")
        tf.write(f"Original rows: {total_rows}\n")
        tf.write(f"Cleaned rows: {len(cleaned_rows)}\n")
        tf.write("Missing counts per column:\n")
        for h, c in missing.items():
            tf.write(f" - {h}: {c}\n")
        tf.write(f"Duplicates removed: {dup_count}\n")
        tf.write("Top messy columns (by missing):\n")
        top_messy = sorted(missing.items(), key=lambda kv: kv[1], reverse=True)[:5]
        for h, c in top_messy:
            tf.write(f" - {h}: {c}\n")
        tf.write("\nAuto-fill summary:\n")
        for h, info in fill_summary.items():
            tf.write(f" - {h}: filled_with={info['filled_with']}, count={info['count']}\n")

    return {
        "cleaned_csv": cleaned_csv_path,
        "json": json_path,
        "txt": txt_path,
        "report": report
    }
