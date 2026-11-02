const std = @import("std");

pub fn main(init: std.process.Init) !void {
    var buf: [64]u8 = undefined;
    var w: std.Io.File.Writer = .init(.stdout(), init.io, &buf);
    try w.interface.print("hello\n", .{});
    try w.interface.flush();
}
