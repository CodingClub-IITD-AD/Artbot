// ArtBot - limit switch mount for 2020 extrusion. Qty 2 (X-min, Y-min).
// Slotted so you can slide the trigger point during homing setup without
// re-drilling anything.
include <params.scad>

ms_w = 30;
ms_t = 5;
ms_h = 34;

module slot(len, d, h) {
    hull() for (o = [-len/2, len/2]) translate([o, 0, 0]) cylinder(d = d, h = h);
}

difference() {
    union() {
        cube([ms_w, ms_t, ms_h]);
        cube([ms_w, 20, ms_t]);   // switch shelf
    }

    // M5 into the extrusion slot, slotted vertically for position trim
    translate([ms_w/2, -eps, ms_h - 10]) rotate([-90, 0, 0])
        rotate([0, 0, 90]) slot(10, m5_clear, ms_t + 2*eps);

    // switch screws
    for (x = [ms_w/2 - sw_hole_pitch/2, ms_w/2 + sw_hole_pitch/2])
        translate([x, 12, -eps]) cylinder(d = sw_hole_d, h = ms_t + 2*eps);
}

// PRINT: flat, 3 perimeters, 30% infill, no supports.
