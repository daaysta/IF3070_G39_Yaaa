import itertools
import string

HORIZONTAL = "H"
VERTICAL = "V"
ORIENTS = (HORIZONTAL, VERTICAL)


def get_dim(v, orient):
    # (kolom, baris) yang dipakai kendaraan
    return (v.l, v.w) if orient == HORIZONTAL else (v.w, v.l)


def _as_dict(vehicles):
    if isinstance(vehicles, dict):
        return vehicles
    return {v.id: v for v in vehicles}


class State:
    def __init__(self, vehicles, ship, placements=None):
        self.vehicles = _as_dict(vehicles)
        self.ship = ship
        self.placements = {vid: None for vid in self.vehicles}
        if placements:
            self.placements.update(placements)
        self._rebuild_cache()

    # cache grid, total berat, total fee
    def _rebuild_cache(self):
        self.grid = [[None] * self.ship.w for _ in range(self.ship.l)]
        self.total_weight = self.total_fee = 0
        for vid, p in self.placements.items():
            if p is None:
                continue
            for cx, cy in self.footprint(vid, *p):
                if 0 <= cx < self.ship.w and 0 <= cy < self.ship.l:
                    self.grid[cy][cx] = vid
            v = self.vehicles[vid]
            self.total_weight += v.weight
            self.total_fee += v.fee

    def copy(self):
        new = State.__new__(State)
        new.vehicles = self.vehicles  # statis
        new.ship = self.ship
        new.placements = dict(self.placements)
        new.grid = [row[:] for row in self.grid]
        new.total_weight = self.total_weight
        new.total_fee = self.total_fee
        return new

    # geometri, validasi, value
    def footprint(self, vid, x, y, orient):
        dx, dy = get_dim(self.vehicles[vid], orient)
        return [(x + i, y + j) for j in range(dy) for i in range(dx)]

    def is_valid(self):
        seen = set()
        weight = 0
        for vid, p in self.placements.items():
            if p is None:
                continue
            if p[2] not in ORIENTS:
                return False
            for cell in self.footprint(vid, *p):
                x, y = cell
                if not (0 <= x < self.ship.w and 0 <= y < self.ship.l) or cell in seen:
                    return False
                seen.add(cell)
            weight += self.vehicles[vid].weight
        return weight <= self.ship.max_capacity

    def value(self):
        return self.total_fee

    def can_place(self, vid, x, y, orient):
        v = self.vehicles[vid]
        dx, dy = get_dim(v, orient)
        if x < 0 or y < 0 or x + dx > self.ship.w or y + dy > self.ship.l:
            return False
        weight = self.total_weight + v.weight
        if self.placements[vid] is not None:
            weight -= v.weight
        if weight > self.ship.max_capacity:
            return False
        for j in range(y, y + dy):
            for i in range(x, x + dx):
                if self.grid[j][i] not in (None, vid):
                    return False
        return True

    # internal, hanya buat state hasil copy
    def _remove(self, vid):
        p = self.placements[vid]
        if p is None:
            return
        for cx, cy in self.footprint(vid, *p):
            self.grid[cy][cx] = None
        v = self.vehicles[vid]
        self.total_weight -= v.weight
        self.total_fee -= v.fee
        self.placements[vid] = None

    # taruh kendaraan
    def _place(self, vid, x, y, orient):
        self._remove(vid)
        for cx, cy in self.footprint(vid, x, y, orient):
            self.grid[cy][cx] = vid
        v = self.vehicles[vid]
        self.total_weight += v.weight
        self.total_fee += v.fee
        self.placements[vid] = (x, y, orient)

    # builder tiap jenis move
    def _moved(self, vid, new_p):
        if new_p == self.placements[vid]:
            return None
        if new_p and not self.can_place(vid, *new_p):
            return None
        new = self.copy()
        if new_p:
            new._place(vid, *new_p)
        else:
            new._remove(vid)
        return new

    def _swapped(self, a, b):
        pa, pb = self.placements[a], self.placements[b]
        if pa == pb:
            return None
        new = self.copy()
        new._remove(a)
        new._remove(b)
        if pb:
            if not new.can_place(a, *pb):
                return None
            new._place(a, *pb)
        if pa:
            if not new.can_place(b, *pa):
                return None
            new._place(b, *pa)
        return new

    # semua posisi (x, y) yang muat di geladak
    def _anchors(self, vid, orient):
        dx, dy = get_dim(self.vehicles[vid], orient)
        return [(x, y) for y in range(self.ship.l - dy + 1)
                for x in range(self.ship.w - dx + 1)]

    def _random_target(self, vid, rng):
        cur = self.placements[vid]
        if cur and rng.random() < 0.1:
            return None
        orient = cur[2] if cur else rng.choice(ORIENTS)
        dx, dy = get_dim(self.vehicles[vid], orient)
        if dx > self.ship.w or dy > self.ship.l:
            return None
        return (rng.randint(0, self.ship.w - dx), rng.randint(0, self.ship.l - dy), orient)

    # neighbor
    def random_neighbor(self, rng, max_tries=50):
        ids = list(self.vehicles)
        for _ in range(max_tries):
            kind = rng.choice(("move", "rotate", "swap"))
            new = None
            if kind == "swap":
                if len(ids) >= 2:
                    a, b = rng.sample(ids, 2)
                    new = self._swapped(a, b)
            elif kind == "rotate":
                vid = rng.choice(ids)
                p = self.placements[vid]
                if p:
                    x, y, o = p
                    new = self._moved(vid, (x, y, VERTICAL if o == HORIZONTAL else HORIZONTAL))
            else:
                vid = rng.choice(ids)
                new = self._moved(vid, self._random_target(vid, rng))
            if new:
                return new
        return None

    def all_neighbors(self):
        ids = list(self.vehicles)
        for vid in ids:
            cur = self.placements[vid]
            if cur:
                x0, y0, o0 = cur
                other = VERTICAL if o0 == HORIZONTAL else HORIZONTAL
                targets = [(x, y, o0) for x, y in self._anchors(vid, o0)]
                targets += [None, (x0, y0, other)]
            else:
                targets = [(x, y, o) for o in ORIENTS for x, y in self._anchors(vid, o)]
            for t in targets:
                new = self._moved(vid, t)
                if new:
                    yield new
        for a, b in itertools.combinations(ids, 2):
            new = self._swapped(a, b)
            if new:
                yield new

    # state awal
    @staticmethod
    def random_state(vehicles, ship, rng, attempts=30):
        vehicles = _as_dict(vehicles)
        state = State(vehicles, ship)
        ids = list(vehicles)
        rng.shuffle(ids)
        for vid in ids:
            for _ in range(attempts):
                orient = rng.choice(ORIENTS)
                dx, dy = get_dim(vehicles[vid], orient)
                if dx > ship.w or dy > ship.l:
                    continue
                x = rng.randint(0, ship.w - dx)
                y = rng.randint(0, ship.l - dy)
                if state.can_place(vid, x, y, orient):
                    state._place(vid, x, y, orient)
                    break
        return state

    # bangun state dari rencana {id: (x, y, orient) / None},
    # yang bentrok atau kelebihan berat dibiarkan di luar kapal
    @staticmethod
    def from_plan(vehicles, ship, plan, order=None):
        vehicles = _as_dict(vehicles)
        state = State(vehicles, ship)
        for vid in (order or list(plan)):
            p = plan.get(vid)
            if p and state.can_place(vid, *p):
                state._place(vid, *p)
        return state

    # buat visualisasi
    def inside_ids(self):
        return [vid for vid, p in self.placements.items() if p]

    def outside_ids(self):
        return [vid for vid, p in self.placements.items() if not p]

    def to_dict(self):
        return {
            "value": self.value(),
            "total_weight": self.total_weight,
            "max_capacity": self.ship.max_capacity,
            "valid": self.is_valid(),
            "inside": {vid: {"x": p[0], "y": p[1], "orient": p[2]}
                       for vid, p in self.placements.items() if p},
            "outside": self.outside_ids(),
        }

    def render_text(self):
        chars = string.ascii_letters + string.digits
        sym = {vid: chars[i % len(chars)] for i, vid in enumerate(self.vehicles)}
        lines = ["".join(sym[c] if c else "." for c in row) for row in self.grid]
        legend = ", ".join(f"{sym[v]}={v}" for v in self.inside_ids())
        return "\n".join(lines) + f"\nvalue={self.value()} berat={self.total_weight}/{self.ship.max_capacity}\n{legend}"
