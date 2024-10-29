from .measure import measure


def cubic_bezier(t: float, p0: float, p1: float, p2: float, p3: float) -> float:
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t**2 * p2
        + t**3 * p3
    )


def pop_up(t: float, dur: float = 0.15) -> float:
    if t <= dur:
        return cubic_bezier(t / dur, 0.8, 1.2, 1.05, 1)
    else:
        return 1.0
