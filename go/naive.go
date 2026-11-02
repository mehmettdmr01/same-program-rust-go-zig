// Same algorithm as c/naive.c: two buffers, nested loops, wrapping edges computed with % for every cell.
package main

import (
	"bytes"
	"fmt"
	"os"
	"strconv"
	"time"
)

func step(n int, cur, next []byte) {
	for y := 0; y < n; y++ {
		up, dn := (y+n-1)%n, (y+1)%n
		for x := 0; x < n; x++ {
			lf, rt := (x+n-1)%n, (x+1)%n
			c := cur[up*n+lf] + cur[up*n+x] + cur[up*n+rt] +
				cur[y*n+lf] + cur[y*n+rt] +
				cur[dn*n+lf] + cur[dn*n+x] + cur[dn*n+rt]
			if c == 3 || (c == 2 && cur[y*n+x] == 1) {
				next[y*n+x] = 1
			} else {
				next[y*n+x] = 0
			}
		}
	}
}

func main() {
	n, _ := strconv.Atoi(os.Args[1])
	gens, _ := strconv.Atoi(os.Args[2])
	text, err := os.ReadFile(os.Args[3])
	if err != nil {
		panic(err)
	}
	text = bytes.ReplaceAll(text, []byte("\n"), nil)
	cur, next := make([]byte, n*n), make([]byte, n*n)
	for i, b := range text {
		if b == '1' {
			cur[i] = 1
		}
	}
	t0 := time.Now()
	for g := 0; g < gens; g++ {
		step(n, cur, next)
		cur, next = next, cur
	}
	sim := time.Since(t0).Seconds() * 1e3
	alive := 0
	for _, b := range cur {
		alive += int(b)
	}
	fmt.Printf("alive=%d sim_ms=%.3f\n", alive, sim)
}
