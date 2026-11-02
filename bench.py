#!/usr/bin/env python3
"""Same program, four compiled languages (plus NumPy and bit-packed C for reference).

Game of Life, 512x512, 200 generations, wrapping edges, same seed file; every program must print
alive=18885. "naive" computes the wrap with % for every cell. "fast" handles the first and last column
separately, so the inner loop is contiguous. fast_int / fast_i32 count neighbours in 32 bits instead of 8;
zig/vector.zig uses explicit vectors.

For each program: build 3 times from clean (fastest counts), one warm-up run thrown away (macOS holds a
freshly built binary on first launch), then ROUNDS rounds over all programs in turn, so slow drift hits
everyone equally. Every program also times its own generation loop (sim_ms), so start-up and reading the seed file cannot
decide the order; a longer 2,000-generation run checks that again. Reported: best sim_ms, best and median
wall clock (process start included, compile excluded); peak memory; binary size. Separately, a hello-world per language: binary size, peak memory, best start-up time.
Writes results.json.
"""
import json, os, re, statistics, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
B = ROOT / "build"
SEED, N, GENS, ALIVE = "seed/start_512.txt", "512", "200", 18885
ROUNDS = 7
LONG_GENS, LONG_ROUNDS, SLOW_SKIP_LONG = "2000", 3, {"c_naive_O3", "zig_naive_safe"}

def clang(out, src, opt="-O2"): return ["clang", opt, "-o", f"build/{out}", src]
def rust(out, src): return ["rustc", "-C", "opt-level=3", "-o", f"build/{out}", src]
def go(out, src): return ["go", "build", "-o", f"build/{out}", src]
def zig(out, src, mode="ReleaseFast"): return ["zig", "build-exe", "-O", mode, f"-femit-bin=build/{out}", src]

PROGRAMS = {
    "c_naive": clang("c_naive", "c/naive.c"), "c_fast": clang("c_fast", "c/fast.c"), "c_fast_int": clang("c_fast_int", "c/fast_int.c"),
    "c_naive_O3": clang("c_naive_O3", "c/naive.c", "-O3"), "c_fast_O3": clang("c_fast_O3", "c/fast.c", "-O3"),
    "rust_naive": rust("rust_naive", "rust/naive.rs"), "rust_fast": rust("rust_fast", "rust/fast.rs"), "rust_fast_i32": rust("rust_fast_i32", "rust/fast_i32.rs"),
    "go_naive": go("go_naive", "go/naive.go"), "go_fast": go("go_fast", "go/fast.go"), "go_swar": go("go_swar", "go/swar.go"),
    "zig_naive": zig("zig_naive", "zig/naive.zig"), "zig_fast": zig("zig_fast", "zig/fast.zig"), "zig_vector": zig("zig_vector", "zig/vector.zig"),
    "zig_naive_safe": zig("zig_naive_safe", "zig/naive.zig", "ReleaseSafe"),
    "c_bitpacked": clang("c_bitpacked", "c/bitpacked.c"),
}
HELLO = {
    "c": clang("hello_c", "hello/hello.c"), "rust": rust("hello_rust", "hello/hello.rs"),
    "go": go("hello_go", "hello/hello.go"), "zig": zig("hello_zig", "hello/hello.zig"),
}
NUMPY = [str(ROOT / ".venv/bin/python"), "numpy/life.py"]

def build(name, cmd):
    best = None
    for _ in range(3):
        out = cmd[cmd.index("-o") + 1] if "-o" in cmd else next(a.split("=")[1] for a in cmd if a.startswith("-femit-bin="))
        Path(ROOT / out).unlink(missing_ok=True)
        t = time.perf_counter()
        subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True)
        d = time.perf_counter() - t
        best = d if best is None else min(best, d)
    return round(best, 3)

def wall(cmd):
    p = subprocess.run([str(B / "wall"), *cmd], cwd=ROOT, capture_output=True, text=True)
    m = re.search(r"seconds=([\d.]+) maxrss_kb=(\d+)", p.stdout)
    if not m: raise RuntimeError(f"{cmd}: {p.stdout!r} {p.stderr!r}")
    a = re.search(r"alive=(\d+)(?: sim_ms=([\d.]+))?", p.stdout)
    return (int(a[1]) if a else None), float(m[1]), int(m[2]), (float(a[2]) if a and a[2] else None)

def versions():
    v = lambda *c: subprocess.run(c, capture_output=True, text=True).stdout.splitlines()[0]
    return {"clang": v("clang", "--version"), "rustc": v("rustc", "--version"), "go": v("go", "version"),
            "zig": v("zig", "version"), "numpy": subprocess.run([NUMPY[0], "-c", "import numpy,sys;print(numpy.__version__, sys.version.split()[0])"], capture_output=True, text=True).stdout.strip()}

def main():
    B.mkdir(exist_ok=True)
    subprocess.run(["clang", "-O2", "-o", "build/wall", "lib/wall.c"], cwd=ROOT, check=True)
    res = {"machine": "MacBook Air M1 2020, 8 GB", "versions": versions(), "load_before": os.getloadavg(), "programs": {}, "hello": {}}
    print("load", res["load_before"], flush=True)
    for name, cmd in PROGRAMS.items():
        res["programs"][name] = {"build_cmd": " ".join(cmd), "build_s": build(name, cmd), "binary_kb": 0, "times": [], "rss_kb": 0}
        res["programs"][name]["binary_kb"] = (B / name).stat().st_size // 1024
        print("built", name, res["programs"][name]["build_s"], flush=True)
    for n in ("numpy", "numpy_four_rolls"):
        res["programs"][n] = {"build_cmd": "", "build_s": 0, "binary_kb": 0, "times": [], "rss_kb": 0}
    cmds = {n: [str(B / n), N, GENS, SEED] for n in PROGRAMS}
    cmds["numpy"] = [*NUMPY, N, GENS, SEED]
    cmds["numpy_four_rolls"] = [NUMPY[0], "numpy/four_rolls.py", N, GENS, SEED]
    for n, c in cmds.items():
        wall(c)
        res["programs"][n]["sim_ms"] = []
    for r in range(ROUNDS):
        for n, c in cmds.items():
            alive, s, rss, sim = wall(c)
            if alive != ALIVE: raise SystemExit(f"{n}: alive={alive}")
            res["programs"][n]["times"].append(s)
            res["programs"][n]["sim_ms"].append(sim)
            res["programs"][n]["rss_kb"] = max(res["programs"][n]["rss_kb"], rss)
        print("round", r + 1, flush=True)
    # longer run, so a few milliseconds of start-up cannot decide the order; every program must still agree
    long_alive = set()
    for r in range(LONG_ROUNDS):
        for n, c in cmds.items():
            if n in SLOW_SKIP_LONG: continue
            cl = [*c]; cl[-2] = LONG_GENS
            alive, s, rss, sim = wall(cl)
            long_alive.add(alive)
            res["programs"][n].setdefault("sim_ms_2000", []).append(sim)
        print("long round", r + 1, flush=True)
    if len(long_alive) != 1: raise SystemExit(f"{LONG_GENS} generations disagree: {long_alive}")
    res["alive_2000"] = long_alive.pop()
    for name, cmd in HELLO.items():
        out = f"hello_{name}"
        b = build(out, cmd)
        wall([str(B / out)])
        runs = [wall([str(B / out)]) for _ in range(50)]
        res["hello"][name] = {"build_s": b, "binary_kb": (B / out).stat().st_size // 1024,
                              "start_ms_best": round(min(x[1] for x in runs) * 1000, 2), "rss_kb": max(x[2] for x in runs)}
    res["load_after"] = os.getloadavg()
    for n, p in res["programs"].items():
        p["best_s"], p["median_s"], p["sim_ms_best"] = min(p["times"]), statistics.median(p["times"]), min(p["sim_ms"])
        p["sim_ms_2000_best"] = min(p["sim_ms_2000"]) if p.get("sim_ms_2000") else None
    (ROOT / "results.json").write_text(json.dumps(res, indent=1))
    print(f"\n{'program':18s} {'sim ms':>8} {'wall s':>8} {'sim2000':>9} {'MB':>6} {'bin KB':>7} {'build':>6}")
    for n, p in sorted(res["programs"].items(), key=lambda x: x[1]["sim_ms_best"]):
        l = p["sim_ms_2000_best"]
        print(f"{n:18s} {p['sim_ms_best']:8.2f} {p['best_s']:8.4f} {(l or 0):9.1f} {p['rss_kb']/1024:6.1f} {p['binary_kb']:7d} {p['build_s']:6.2f}")
    print("\nhello:", json.dumps(res["hello"]))
    print("load after", res["load_after"])

if __name__ == "__main__":
    main()
