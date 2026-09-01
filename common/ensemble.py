"""
Shared logic for how the model "council" combines votes. Lives in common/
(not backend/ or ml/) because it's a rule about ensemble behavior, not
something either training or serving owns on its own - both should agree on
what "recent models count for a bit more" actually means numerically.
"""

from __future__ import annotations

# How much more influence the single newest council member gets vs. the
# single oldest one, before normalizing. 1.12 = 12% more, splitting the
# requested 10-15% range. Members in between are spaced evenly, so this is
# a mild tilt toward recency, not a dominant one.
NEWEST_MEMBER_BOOST = 1.12


def compute_recency_weights(n: int, newest_boost: float = NEWEST_MEMBER_BOOST) -> list[float]:
    """
    Returns `n` weights, ordered oldest -> newest, that sum to 1.0.

    The newest model's raw weight is `newest_boost` times the oldest's;
    everything in between is spaced evenly on that line. Dividing by the
    total to normalize scales every weight by the same constant, which
    preserves that ratio exactly - so the newest member ends up with
    precisely `newest_boost`x the oldest member's weight even after
    normalizing. With n=5 and the default 1.12 boost:
        [0.189, 0.194, 0.200, 0.206, 0.211]  (oldest -> newest)
    """
    if n <= 0:
        return []
    if n == 1:
        return [1.0]

    raw = [1.0 + (newest_boost - 1.0) * (i / (n - 1)) for i in range(n)]
    total = sum(raw)
    return [w / total for w in raw]