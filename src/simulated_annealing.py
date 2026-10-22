"""SA untuk maksimisasi fee; trace menyimpan proposal dan keputusan sebenarnya."""
import math
import random
import time
from result import SearchResult


def simulated_annealing(initial, initial_temp=100.0, cooling_rate=0.995,
                        min_temp=0.01, max_iter=5000, stuck_window=100,
                        skor_evaluasi=0.0, rng=None):
    if not initial.is_valid():
        raise ValueError('Initial state tidak valid')
    if not (math.isfinite(initial_temp) and math.isfinite(min_temp)
            and 0 < min_temp < initial_temp and 0 < cooling_rate < 1):
        raise ValueError('Perlu 0 < min_temp < initial_temp dan 0 < cooling_rate < 1')
    if max_iter < 1 or stuck_window < 1 or not math.isfinite(skor_evaluasi):
        raise ValueError('Parameter iterasi/window/bias tidak valid')
    rng = rng or random.Random()
    start = time.perf_counter()
    current = initial.copy()
    best = current.copy()
    history, best_history, trace = [current.value()], [best.value()], []
    stale = stuck_count = 0
    temp = initial_temp
    stop = 'max_iter'
    for iteration in range(1, max_iter + 1):
        if temp < min_temp:
            stop = 'min_temp'
            break
        # Tidak ada proposal bukan bukti bahwa seluruh neighborhood kosong.
        candidate = current.random_neighbor(rng) if current.vehicles else None
        delta = None if candidate is None else candidate.value() - current.value()
        effective_delta = None if delta is None else delta + skor_evaluasi
        prob = None if delta is None else math.exp(min(0.0, effective_delta / temp))
        draw = rng.random() if prob is not None and prob < 1 else None
        accepted = prob is not None and (prob == 1 or draw < prob)
        before = current.value()
        if accepted:
            current = candidate
        if current.value() > best.value():
            best = current.copy()
            stale = 0
        else:
            stale += 1
        # Satu episode dihitung saat ambang tercapai, bukan setiap iterasi setelahnya.
        stuck_event = stale == stuck_window
        stuck_count += int(stuck_event)
        history.append(current.value())
        best_history.append(best.value())
        trace.append(dict(iteration=iteration, temperature=temp, delta=delta,
                          effective_delta=effective_delta, probability=prob,
                          random_draw=draw, accepted=accepted, before=before,
                          current_value=current.value(), best_value=best.value(),
                          stagnation_length=stale, stuck_event=stuck_event))
        temp *= cooling_rate
    return SearchResult(
        name='sa', params=dict(initial_temp=initial_temp, cooling_rate=cooling_rate,
            min_temp=min_temp, max_iter=max_iter, stuck_window=stuck_window,
            skor_evaluasi=skor_evaluasi), initial_state=initial.copy(),
        final_state=current, history=history, iterations=len(trace),
        duration=time.perf_counter()-start,
        extras=dict(trace=trace, best_history=best_history, best_state=best.to_dict(),
                    best_value=best.value(), stuck_count=stuck_count,
                    stuck_definition='Episode >= stuck_window iterasi tanpa best baru; proxy stagnasi, bukan pembuktian local optimum.',
                    stop_reason=stop))
