import json
import os
import glob
from typing import List


def percentile(sorted_vals: List[int], p: float) -> int:
    if not sorted_vals:
        return 0
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return int(sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f))

