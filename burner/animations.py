def _cubic_bezier(t: float, p0: float, p1: float, p2: float, p3: float) -> float:
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t**2 * p2
        + t**3 * p3
    )


def pop(t: float, amp: float = 0.2, dur: float = 0.15) -> float:
    if t <= dur:
        return _cubic_bezier(t / dur, 1 - amp, 1 + amp, 1, 1)
    else:
        return 1.0
