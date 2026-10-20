"""
state.py - Representasi state, validasi constraint, value, dan move (bagian A).

KONVENSI KOORDINAT (jangan diubah diam-diam, B dan C ikut memakainya):
  - Geladak adalah grid berukuran ship.w kolom (sumbu x) x ship.l baris (sumbu y).
  - (x, y) = sel pojok kiri-atas kendaraan, dimulai dari 0.
  - VERTICAL   : kendaraan menempati w kolom x l baris (searah geladak).
  - HORIZONTAL : kendaraan menempati l kolom x w baris (diputar 90 derajat).
  - placements[id] = (x, y, orient)  jika di DALAM kapal,
                     None            jika di LUAR kapal.

DESAIN: state selalu VALID (tidak overlap, di dalam batas, berat <= kapasitas).
Move yang menghasilkan state tidak valid langsung dibuang (mengembalikan None).
State TIDAK diubah in-place oleh move: setiap move menghasilkan State baru
(lewat copy), jadi state lama aman dipakai ulang (mis. oleh GA atau SA).
"""
import itertools
import string

HORIZONTAL = "H"
VERTICAL = "V"
ORIENTS = (HORIZONTAL, VERTICAL)


def footprint_size(vehicle, orient):
    """Ukuran (dx, dy) = (jumlah kolom, jumlah baris) yang ditempati kendaraan."""
    if orient == HORIZONTAL:
        return vehicle.l, vehicle.w
    return vehicle.w, vehicle.l


def _as_dict(vehicles):
    """Terima list[Vehicle] atau dict id->Vehicle, selalu kembalikan dict."""
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

    # ------------------------------------------------------------------
    # Cache (grid, total berat, total fee) supaya pengecekan cepat
    # ------------------------------------------------------------------
    def _rebuild_cache(self):
        """Hitung ulang grid dan total dari self.placements.
        Sel di luar geladak dilewati supaya state tidak valid tetap bisa dibuat
        untuk keperluan tes; is_valid() adalah penentu kebenaran yang sebenarnya."""
        self.grid = [[None] * self.ship.w for _ in range(self.ship.l)]
        self.total_weight = 0
        self.total_fee = 0
        for vid, p in self.placements.items():
            if p is None:
                continue
            for cx, cy in self.footprint(vid, *p):
                if 0 <= cx < self.ship.w and 0 <= cy < self.ship.l:
                    self.grid[cy][cx] = vid
            self.total_weight += self.vehicles[vid].weight
            self.total_fee += self.vehicles[vid].fee

    def copy(self):
        """Salinan yang tidak berbagi grid/placements dengan aslinya."""
        new = State.__new__(State)
        new.vehicles = self.vehicles          # data statis, boleh dibagi
        new.ship = self.ship
        new.placements = dict(self.placements)  # isinya tuple (immutable)
        new.grid = [row[:] for row in self.grid]
        new.total_weight = self.total_weight
        new.total_fee = self.total_fee
        return new

    # ------------------------------------------------------------------
    # Geometri, validasi, value
    # ------------------------------------------------------------------
    def footprint(self, vid, x, y, orient):
        """Daftar sel (cx, cy) yang ditempati kendaraan vid jika ditaruh di (x, y, orient)."""
        dx, dy = footprint_size(self.vehicles[vid], orient)
        return [(x + i, y + j) for j in range(dy) for i in range(dx)]

    def is_valid(self):
        """Cek dari nol (tidak memakai cache): batas geladak, no overlap, kapasitas."""
        seen = set()
        weight = 0
        for vid, p in self.placements.items():
            if p is None:
                continue
            x, y, orient = p
            if orient not in ORIENTS:
                return False
            dx, dy = footprint_size(self.vehicles[vid], orient)
            if x < 0 or y < 0 or x + dx > self.ship.w or y + dy > self.ship.l:
                return False                      # keluar batas geladak
            for cell in self.footprint(vid, x, y, orient):
                if cell in seen:
                    return False                  # overlap
                seen.add(cell)
            weight += self.vehicles[vid].weight
        return weight <= self.ship.max_capacity   # kapasitas

    def value(self):
        """Objective function: total ShippingFee kendaraan yang diangkut."""
        return self.total_fee

    def can_place(self, vid, x, y, orient):
        """Cek cepat (pakai cache) apakah vid boleh ditaruh di (x, y, orient).
        Sel dan berat vid sendiri diabaikan jika ia sedang berada di kapal,
        jadi cocok dipakai untuk memindah/memutar kendaraan yang sama."""
        v = self.vehicles[vid]
        dx, dy = footprint_size(v, orient)
        if x < 0 or y < 0 or x + dx > self.ship.w or y + dy > self.ship.l:
            return False
        weight = self.total_weight
        if self.placements[vid] is not None:
            weight -= v.weight
        if weight + v.weight > self.ship.max_capacity:
            return False
        for j in range(y, y + dy):
            row = self.grid[j]
            for i in range(x, x + dx):
                if row[i] is not None and row[i] != vid:
                    return False
        return True

    # ------------------------------------------------------------------
    # Operasi internal (hanya dipakai pada state hasil copy / state baru)
    # ------------------------------------------------------------------
    def _remove(self, vid):
        p = self.placements[vid]
        if p is None:
            return
        for cx, cy in self.footprint(vid, *p):
            self.grid[cy][cx] = None
        self.total_weight -= self.vehicles[vid].weight
        self.total_fee -= self.vehicles[vid].fee
        self.placements[vid] = None

    def _place(self, vid, x, y, orient):
        """Taruh vid di (x, y, orient). Wajib sudah dicek dengan can_place."""
        self._remove(vid)
        for cx, cy in self.footprint(vid, x, y, orient):
            self.grid[cy][cx] = vid
        self.total_weight += self.vehicles[vid].weight
        self.total_fee += self.vehicles[vid].fee
        self.placements[vid] = (x, y, orient)

    # ------------------------------------------------------------------
    # Builder tiap jenis move: kembalikan State baru, atau None jika tidak valid
    # ------------------------------------------------------------------
    def _moved(self, vid, new_p):
        """Pindahkan vid ke new_p ((x,y,orient) atau None = keluar kapal).
        Dipakai untuk move 'pindah' dan 'ubah orientasi'."""
        if new_p == self.placements[vid]:
            return None                            # tidak ada perubahan
        if new_p is not None and not self.can_place(vid, *new_p):
            return None
        new = self.copy()
        if new_p is None:
            new._remove(vid)
        else:
            new._place(vid, *new_p)
        return new

    def _swapped(self, a, b):
        """Tukar placement a dan b (boleh salah satunya di luar kapal)."""
        pa, pb = self.placements[a], self.placements[b]
        if pa == pb:
            return None                            # keduanya di luar: tidak ada efek
        new = self.copy()
        new._remove(a)
        new._remove(b)
        if pb is not None:
            if not new.can_place(a, *pb):
                return None
            new._place(a, *pb)
        if pa is not None:
            if not new.can_place(b, *pa):
                return None
            new._place(b, *pa)
        return new

    def _anchors(self, vid, orient):
        """Semua (x, y) sehingga kendaraan muat di dalam batas geladak."""
        dx, dy = footprint_size(self.vehicles[vid], orient)
        return [(x, y) for y in range(self.ship.l - dy + 1)
                for x in range(self.ship.w - dx + 1)]

    def _random_target(self, vid, rng):
        """Tujuan acak untuk move 'pindah'. None = keluar kapal."""
        cur = self.placements[vid]
        if cur is not None and rng.random() < 0.1:
            return None                            # sesekali keluarkan dari kapal
        orient = cur[2] if cur is not None else rng.choice(ORIENTS)
        dx, dy = footprint_size(self.vehicles[vid], orient)
        if dx > self.ship.w or dy > self.ship.l:
            return None                            # tidak muat pada orientasi ini
        return (rng.randint(0, self.ship.w - dx), rng.randint(0, self.ship.l - dy), orient)

    # ------------------------------------------------------------------
    # Neighbor
    # ------------------------------------------------------------------
    def random_neighbor(self, rng, max_tries=50):
        """Satu neighbor acak yang valid (untuk stochastic HC, SA, mutasi GA).
        Mengembalikan None jika setelah max_tries percobaan tidak ketemu."""
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
                if p is not None:
                    x, y, o = p
                    new = self._moved(vid, (x, y, VERTICAL if o == HORIZONTAL else HORIZONTAL))
            else:
                vid = rng.choice(ids)
                new = self._moved(vid, self._random_target(vid, rng))
            if new is not None:
                return new
        return None

    def all_neighbors(self):
        """Generator semua neighbor valid (untuk steepest ascent / sideways move)."""
        ids = list(self.vehicles)
        for vid in ids:
            cur = self.placements[vid]
            if cur is None:
                targets = [(x, y, o) for o in ORIENTS for (x, y) in self._anchors(vid, o)]
            else:
                x0, y0, o0 = cur
                other = VERTICAL if o0 == HORIZONTAL else HORIZONTAL
                targets = [(x, y, o0) for (x, y) in self._anchors(vid, o0)]
                targets += [None, (x0, y0, other)]  # keluar kapal, dan ubah orientasi
            for t in targets:
                new = self._moved(vid, t)
                if new is not None:
                    yield new
        for a, b in itertools.combinations(ids, 2):
            new = self._swapped(a, b)
            if new is not None:
                yield new

    # ------------------------------------------------------------------
    # Pembuat state awal
    # ------------------------------------------------------------------
    @staticmethod
    def random_state(vehicles, ship, rng, attempts=30):
        """Initial state random: kendaraan diurutkan acak, lalu masing-masing dicoba
        ditaruh di posisi/orientasi acak sampai `attempts` kali. Kalau gagal,
        kendaraan dibiarkan di luar kapal."""
        vehicles = _as_dict(vehicles)
        state = State(vehicles, ship)
        ids = list(vehicles)
        rng.shuffle(ids)
        for vid in ids:
            for _ in range(attempts):
                orient = rng.choice(ORIENTS)
                dx, dy = footprint_size(vehicles[vid], orient)
                if dx > ship.w or dy > ship.l:
                    continue
                x = rng.randint(0, ship.w - dx)
                y = rng.randint(0, ship.l - dy)
                if state.can_place(vid, x, y, orient):
                    state._place(vid, x, y, orient)
                    break
        return state

    # ------------------------------------------------------------------
    # Keluaran untuk visualisasi / penyimpanan hasil
    # ------------------------------------------------------------------
    def inside_ids(self):
        return [vid for vid, p in self.placements.items() if p is not None]

    def outside_ids(self):
        return [vid for vid, p in self.placements.items() if p is None]

    def to_dict(self):
        """Dict siap di-json: keadaan kendaraan (dalam/luar), value, dan validitas."""
        return {
            "value": self.value(),
            "total_weight": self.total_weight,
            "max_capacity": self.ship.max_capacity,
            "valid": self.is_valid(),
            "inside": {vid: {"x": p[0], "y": p[1], "orient": p[2]}
                       for vid, p in self.placements.items() if p is not None},
            "outside": self.outside_ids(),
        }

    def render_text(self):
        """Gambar ASCII geladak untuk debugging cepat di terminal."""
        symbols = string.ascii_uppercase + string.ascii_lowercase + string.digits
        sym = {vid: symbols[i % len(symbols)] for i, vid in enumerate(self.vehicles)}
        lines = ["".join(sym[c] if c is not None else "." for c in row) for row in self.grid]
        legend = ", ".join(f"{sym[v]}={v}" for v in self.inside_ids())
        return "\n".join(lines) + f"\nvalue={self.value()} berat={self.total_weight}/{self.ship.max_capacity}\n{legend}"


def state_resolution(vehicles, ship, desired, order=None):
    """Bangun State VALID dari placements `desired` yang mungkin bentrok.
    Kendaraan diproses sesuai `order` (default: urutan key desired). Yang tidak bisa
    ditaruh (overlap / keluar batas / melebihi kapasitas) dikeluarkan dari kapal.
    Dipakai GA setelah crossover supaya anak selalu valid (repair)."""
    vehicles = _as_dict(vehicles)
    state = State(vehicles, ship)
    for vid in (order if order is not None else list(desired)):
        p = desired.get(vid)
        if p is not None and state.can_place(vid, *p):
            state._place(vid, *p)
    return state
