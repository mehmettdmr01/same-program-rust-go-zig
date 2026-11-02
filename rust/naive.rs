// Same algorithm as c/naive.c: two buffers, nested loops, wrapping edges computed with % for every cell.
use std::{env, fs};

fn step(n: usize, cur: &[u8], next: &mut [u8]) {
    for y in 0..n {
        let up = (y + n - 1) % n;
        let dn = (y + 1) % n;
        for x in 0..n {
            let lf = (x + n - 1) % n;
            let rt = (x + 1) % n;
            let c = cur[up * n + lf] + cur[up * n + x] + cur[up * n + rt]
                + cur[y * n + lf] + cur[y * n + rt]
                + cur[dn * n + lf] + cur[dn * n + x] + cur[dn * n + rt];
            next[y * n + x] = (c == 3 || (c == 2 && cur[y * n + x] == 1)) as u8;
        }
    }
}

fn main() {
    let a: Vec<String> = env::args().collect();
    let n: usize = a[1].parse().unwrap();
    let gens: usize = a[2].parse().unwrap();
    let text = fs::read(&a[3]).unwrap();
    let mut cur: Vec<u8> = text.iter().filter(|b| **b != b'\n').map(|b| (*b == b'1') as u8).collect();
    let mut next = vec![0u8; n * n];
    let t0 = std::time::Instant::now();
    for _ in 0..gens {
        step(n, &cur, &mut next);
        std::mem::swap(&mut cur, &mut next);
    }
    let sim_ms = t0.elapsed().as_secs_f64() * 1e3;
    let alive: u64 = cur.iter().map(|&b| b as u64).sum();
    println!("alive={alive} sim_ms={sim_ms:.3}");
}
