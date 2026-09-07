// ArtBot - GT2 belt clamp, two-piece. Qty 6 (two ends x three belt runs).
// The toothed base meshes with the belt teeth; the flat cap squeezes it.
// A clamp that only relies on friction WILL creep on a 180 cm run.
include <params.scad>

cl_w      = belt_w + 8;   // across the belt
cl_l      = 26;           // along the belt: 13 teeth of grip
cl_t      = 5;
teeth_n   = floor(cl_l / belt_pitch);
bolt_gap  = 17;           // M3 centres, straddling the belt

module tooth_comb() {
    for (i = [0 : teeth_n - 1])
        translate([i * belt_pitch + belt_pitch/2, -eps, cl_t])
            rotate([-90, 0, 0])
                cylinder(d = belt_pitch * 0.9, h = cl_w + 2*eps, $fn = 24);
}

module bolts(h) {
    for (x = [cl_l * 0.2, cl_l * 0.8])
        translate([x, cl_w/2, -eps]) {
            cylinder(d = m3_clear, h = h + 2*eps);
        }
}

module base() {
    difference() {
        cube([cl_l, cl_w, cl_t + belt_tooth]);
        tooth_comb();
        bolts(cl_t + belt_tooth);
        // nut traps underneath
        for (x = [cl_l * 0.2, cl_l * 0.8])
            translate([x, cl_w/2, -eps])
                cylinder(d = m3_nut_af / cos(30), h = m3_nut_t, $fn = 6);
    }
}

module cap() {
    difference() {
        cube([cl_l, cl_w, cl_t]);
        bolts(cl_t);
    }
}

base();
translate([0, cl_w + 6, 0]) cap();

// PRINT: as laid out, teeth up, 0.15 mm layers (the teeth need the
// resolution), 5 perimeters, 50% infill. Print one pair and test the mesh on
// an offcut of belt BEFORE printing all six.
