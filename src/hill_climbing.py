import random
import time

from result import SearchResult


def hill_climbing_sideways(initial, max_sideways=100, max_iter=10_000,
                           reset_on_improve=True, rng=None):
    rng = rng or random.Random()
    start = time.perf_counter()

    current = initial
    history = [current.value()]
    sideways_used = 0
    streak = 0
    iterations = 0
    stop_reason = "max_iter"

    while iterations < max_iter:
        cur_val = current.value()
        best, best_val, n_best = None, None, 0

        for nb in current.all_neighbors():
            v = nb.value()
            if best_val is None or v > best_val:
                best, best_val, n_best = nb, v, 1
            elif v == best_val:
                n_best += 1
                if rng.random() < 1.0 / n_best:
                    best = nb

        if best is None:
            stop_reason = "no_neighbor"
            break
        if best_val < cur_val:
            stop_reason = "local_optimum"
            break

        if best_val == cur_val:
            used = streak if reset_on_improve else sideways_used
            if used >= max_sideways:
                stop_reason = "max_sideways"
                break
            streak += 1
            sideways_used += 1
        else:
            streak = 0

        current = best
        iterations += 1
        history.append(current.value())

    return SearchResult(
        name="hc_sideways",
        params={"max_sideways": max_sideways, "max_iter": max_iter,
                "reset_on_improve": reset_on_improve},
        initial_state=initial,
        final_state=current,
        history=history,
        iterations=iterations,
        duration=time.perf_counter() - start,
        extras={"stop_reason": stop_reason, "sideways_used": sideways_used},
    )