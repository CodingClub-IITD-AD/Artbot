// ArtBot - SG90 servo bracket. Qty 1.
// Bolts to the LEFT rib of pen_carriage_base. Slotted holes on both
// interfaces: the servo throw needs trimming at assembly, always.
include <params.scad>

br_l   = 46;   // along Z (fore/aft, toward the board)
br_h   = 44;   // along Y
br_t   = 5;
wing_l = 24;

module slot(len, d, h) {
    hull() for (o = [-len/2, len/2]) translate([o, 0, 0]) cylinder(d = d, h = h);
}

difference() {
    union() {
        // vertical face: carries the servo
        cube([br_t, br_h, br_l], center = false);
        // foot: bolts to the carriage rib
        cube([wing_l, br_h, br_t]);
    }

    // servo mount tabs -> slotted along Z for throw adjustment
    for (z = [br_l/2 - sg90_tab_span/2, br_l/2 + sg90_tab_span/2])
        translate([-eps, br_h/2, z]) rotate([0, 90, 0])
            rotate([0, 0, 90]) slot(6, sg90_screw_d, br_t + 2*eps);

    // servo body pocket so the case sits flush against the face
    translate([-eps, br_h/2 - sg90_wid/2, br_l/2 - sg90_len/2])
        cube([2.2, sg90_wid, sg90_len]);

    // foot -> 2x M3 slotted along X, matches the rib bosses at 20 mm pitch
    for (y = [br_h/2 - 10, br_h/2 + 10])
        translate([wing_l/2, y, -eps]) slot(6, m3_clear, br_t + 2*eps);
}

// PRINT: foot down, 4 perimeters, 40% infill, no supports.
