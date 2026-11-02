// Same algorithm as c/naive.c: two buffers, nested loops, wrapping edges computed with % for every cell.
const std = @import("std");

fn step(n: usize, cur: []const u8, next: []u8) void {
    for (0..n) |y| {
        const up = (y + n - 1) % n;
        const dn = (y + 1) % n;
        for (0..n) |x| {
            const lf = (x + n - 1) % n;
            const rt = (x + 1) % n;
            const c = cur[up * n + lf] + cur[up * n + x] + cur[up * n + rt] +
                cur[y * n + lf] + cur[y * n + rt] +
                cur[dn * n + lf] + cur[dn * n + x] + cur[dn * n + rt];
            next[y * n + x] = @intFromBool(c == 3 or (c == 2 and cur[y * n + x] == 1));
        }
    }
}

pub fn main(init: std.process.Init) !void {
    const arena = init.arena.allocator();
    const args = try init.minimal.args.toSlice(arena);
    const n = try std.fmt.parseInt(usize, args[1], 10);
    const gens = try std.fmt.parseInt(usize, args[2], 10);
    const text = try std.Io.Dir.cwd().readFileAlloc(init.io, args[3], arena, .unlimited);
    var cur = try arena.alloc(u8, n * n);
    var next = try arena.alloc(u8, n * n);
    var i: usize = 0;
    for (text) |b| {
        if (b != '\n') {
            cur[i] = @intFromBool(b == '1');
            i += 1;
        }
    }
    const t0 = std.Io.Clock.awake.now(init.io);
    for (0..gens) |_| {
        step(n, cur, next);
        std.mem.swap([]u8, &cur, &next);
    }
    const t1 = std.Io.Clock.awake.now(init.io);
    const sim_ms = @as(f64, @floatFromInt(t0.durationTo(t1).toNanoseconds())) / 1e6;
    var alive: u64 = 0;
    for (cur) |b| alive += b;
    var buf: [64]u8 = undefined;
    var w: std.Io.File.Writer = .init(.stdout(), init.io, &buf);
    try w.interface.print("alive={d} sim_ms={d:.3}\n", .{ alive, sim_ms });
    try w.interface.flush();
}
