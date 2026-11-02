# Same program in C, Rust, Go and Zig: the measurements

Video: https://youtu.be/4txLuE-7kcc

Conway's Game of Life, 512x512, 200 generations, wrapping edges, same starting file. Every program must print `alive=18885`; a longer 2,000-generation run must print `alive=8836`. This follows [same-program-14-ways](https://github.com/mehmettdmr01/same-program-14-ways) and corrects it: "NumPy beat plain C" was wrong, my C had a `% N` in the hot loop.

Apple M1 (MacBook Air 2020, 8 GB). Apple clang version 17.0.0 (clang-1700.3.19.1); rustc 1.99.1 (58cf8f9c3 2026-10-13) (Homebrew); go version go1.27.3 darwin/arm64; zig 0.17.0; NumPy 2.5.4 3.15.2.

## Results

Simulation = the generation loop only, timed by each program, without start-up or reading the file. Wall = whole process. Best of 7 interleaved rounds. Memory is peak RSS.

| Program | Simulation (ms) | Wall (ms) | Memory (MB) | Binary (KB) | Build (s) |
|---|---|---|---|---|---|
| c_bitpacked | 3.35 | 5.7 | 1.6 | 33 | 0.07 |
| rust_fast | 5.25 | 7.5 | 2.3 | 463 | 0.17 |
| c_fast_O3 | 6.33 | 8.2 | 2.0 | 33 | 0.075 |
| c_fast | 6.41 | 8.3 | 2.0 | 33 | 0.073 |
| zig_vector | 6.89 | 9.2 | 2.2 | 403 | 6.687 |
| rust_fast_i32 | 14.90 | 17.0 | 2.3 | 463 | 0.173 |
| c_fast_int | 17.15 | 18.9 | 2.0 | 33 | 0.073 |
| go_swar | 22.96 | 26.4 | 4.9 | 2423 | 0.105 |
| numpy_four_rolls | 23.22 | 82.3 | 28.7 | — | — |
| numpy | 58.50 | 127.9 | 31.9 | — | — |
| zig_fast | 65.27 | 67.7 | 2.2 | 403 | 6.786 |
| go_fast | 66.15 | 69.5 | 5.0 | 2423 | 0.113 |
| zig_naive | 205.38 | 207.7 | 2.2 | 403 | 6.806 |
| c_naive_O3 | 230.37 | 232.9 | 2.0 | 33 | 0.07 |
| c_naive | 232.81 | 234.8 | 2.0 | 33 | 0.068 |
| go_naive | 268.83 | 272.1 | 4.9 | 2423 | 0.109 |
| rust_naive | 339.57 | 341.9 | 2.3 | 463 | 0.157 |
| zig_naive_safe | 388.90 | 391.3 | 2.4 | 532 | 7.697 |

- `naive`: wraps edges with `%` for every cell. `fast`: handles the first and last column separately. `fast_int` / `fast_i32`: counts neighbours in 32 bits rather than 8.
- `zig/vector.zig` uses explicit vectors; `go/swar.go` fits 8 cells in a 64-bit integer; `numpy/four_rolls.py` is a faster NumPy.
- `rust/naive_unchecked.rs` removes bounds checks (about 258 ms wall); not part of `bench.py`.
- Hello-world size, memory and start-up: `results.json`.

## What this does and doesn't show

- One program on one machine. This is not a ranking of languages.
- Clang reports `loop not vectorized` for `c/naive.c` and `vectorized loop (vectorization width: 16)` for `c/fast.c` (`-Rpass=loop-vectorize -Rpass-missed=loop-vectorize`).
- Zig 0.17 (official and Homebrew builds) left `zig/fast.zig` scalar: no vector instructions in the disassembly. Why is unexplained. Go's compiler didn't vectorize this loop either.
- Rust `fast` leads C `fast` by 1.22 times. The cause isn't settled; it looks like code generation.
- An earlier version of the C read the seed with `fgetc`, which added about 4 ms and made Rust look 1.65 times faster. Fixed here, and reading is now outside the timed loop.
- Not tested: hand-written vector code in C or Rust, GOEXPERIMENT=simd.

The scripts were written with Claude Code.

## Run it

```
python3 -m venv .venv && .venv/bin/pip install numpy
python3 bench.py
```
