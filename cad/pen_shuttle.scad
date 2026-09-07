// ArtBot - pen shuttle. Qty 1.
// Slides on the two guide rods. Clamps the marker. Two compression springs
// (one per rod) push it toward the board; the servo cam pushes it back.
include <params.scad>

sh_w   = 62;   // X
sh_h   = 34;   // Y
sh_d   = 22;   // Z, bearing length on the rods
slit_w = 2.0;  // split-clamp kerf

tab_h  = 26;   // servo cam tab, rises above the body
tab_t  = 5;

module body() {
    translate([-sh_w/2, -sh_h/2, 0]) cube([sh_w, sh_h, sh_d]);
}

module cam_tab() {
    // flat face on the -Z side: the servo horn sweeps against this and
    // pushes the shuttle away from the board. Push-only, spring returns it.
    translate([-tab_t/2 - 22, -sh_h/2, 0]) cube([tab_t, sh_h/2 + tab_h, tab_t + 3]);
}

difference() {
    union() { body(); cam_tab(); }

    // running bores on the rods
    for (x = [-rod_spacing/2, rod_spacing/2])
        translate([x, 0, -eps]) cylinder(d = rod_slide, h = sh_d + 2*eps);

    // marker bore
    translate([0, 0, -eps]) cylinder(d = pen_d, h = sh_d + 2*eps);

    // clamp kerf: from the top face down into the marker bore
    translate([-slit_w/2, 0, -eps]) cube([slit_w, sh_h/2 + eps, sh_d + 2*eps]);

    // pinch bolt across the kerf: M3 clear one side, nut trap the other
    translate([0, sh_h/2 - 6, sh_d/2]) rotate([0, 90, 0]) {
        translate([0, 0, -sh_w/2 - eps]) cylinder(d = m3_clear, h = sh_w + 2*eps);
        translate([0, 0, sh_w/2 - m3_nut_t]) cylinder(d = m3_nut_af / cos(30), h = m3_nut_t + eps, $fn = 6);
    }
}

// PRINT: on its back (the +Z face down) so the rod bores print as vertical
// circles - they come out round and need no support. 4 perimeters, 40% infill.
// If the bores are tight, scale rod_slide up 0.1 mm at a time; do NOT ream by
// hand, you will oval them and the shuttle will bind.
