from __future__ import annotations

import math


def consistency_report(values: list[dict]) -> dict:
    if not values:
        return {"n_runs": 0, "metrics": {}}
    keys = sorted({k for item in values for k, v in item.items() if isinstance(v, (int, float))})
    out = {"n_runs": len(values), "metrics": {}}
    for key in keys:
        series = [float(item[key]) for item in values if isinstance(item.get(key), (int, float))]
        if not series:
            continue
        mean = sum(series) / len(series)
        variance = sum((x - mean) ** 2 for x in series) / len(series)
        out["metrics"][key] = {
            "mean": mean,
            "std": math.sqrt(variance),
            "min": min(series),
            "max": max(series),
        }
    return out
