// ArtBot - idler bracket for 2020 extrusion. Qty 3.
//   2x bottom of the left/right vertical rails (Y belt return)
//   1x right end of the horizontal rail (X belt return)
// Holds a 20T GT2 idler on an M5 bolt. Bolts into the extrusion slot on
// two M5 T-nuts.
include <params.scad>

br_t      = 7;
br_w      = 28;
br_h      = 62;
idler_off = 42;   // slot face -> idler axis. sets the belt plane; VERIFY it
                  // lines up with the motor pulley plane before printing 3.
tnut_pitch = 30;

difference() {
    union() {
        cube([br_w, br_t, br_h]);                       // face plate on the extrusion
        translate([0, 0, br_h - 18]) cube([br_w, idler_off, 18]);  // idler arm
    }

    // 2x M5 into the extrusion slot, counterbored
    for (z = [br_h/2 - tnut_pitch/2, br_h/2 + tnut_pitch/2])
        translate([br_w/2, -eps, z]) rotate([-90, 0, 0]) {
            cylinder(d = m5_clear, h = br_t + 2*eps);
            translate([0, 0, br_t - m5_head_h]) cylinder(d = m5_head_d, h = m5_head_h + eps);
        }

    // idler axle: M5 through the arm, nut trap on top
    translate([br_w/2, idler_off - 11, br_h - 18 - eps])
        cylinder(d = m5_clear, h = 18 + 2*eps);
}

// PRINT: face plate flat on the bed, arm pointing up, WITH supports under the
// arm overhang. 5 perimeters, 60% infill - this part is in the belt load path
// and a sloppy one shows up as wandering lines.
