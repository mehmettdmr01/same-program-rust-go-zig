// Same as naive.rs with the bounds checks removed (get_unchecked), to measure what they cost: about 258 ms against 340 ms.
use std::{env, fs};

fn step(n: usize, cur: &[u8], next: &mut [u8]) {
    for y in 0..n { unsafe {
        let up = (y + n - 1) % n;
        let dn = (y + 1) % n;
        for x in 0..n {
            let lf = (x + n - 1) % n;
            let rt = (x + 1) % n;
            let c = *cur.get_unchecked(up * n + lf) + *cur.get_unchecked(up * n + x) + *cur.get_unchecked(up * n + rt)
                + *cur.get_unchecked(y * n + lf) + *cur.get_unchecked(y * n + rt)
                + *cur.get_unchecked(dn * n + lf) + *cur.get_unchecked(dn * n + x) + *cur.get_unchecked(dn * n + rt);
            *next.get_unchecked_mut(y * n + x) = (c == 3 || (c == 2 && *cur.get_unchecked(y * n + x) == 1)) as u8;
        }
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
    for _ in 0..gens {
        step(n, &cur, &mut next);
        std::mem::swap(&mut cur, &mut next);
    }
    let alive: u64 = cur.iter().map(|&b| b as u64).sum();
    println!("alive={alive}");
}
