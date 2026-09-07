// ArtBot - pen carriage base. Qty 1.
// Bolts to the pen-carriage gantry plate. Carries the two guide rods, the
// front guide wall, and the servo bracket.
//
// Part axes (as printed, and as mounted):
//   X = along the horizontal rail        Y = vertical (up)
//   Z = out of the mount plate, TOWARD the whiteboard
include <params.scad>

base_w    = 90;   // X
base_h    = 76;   // Y
base_t    = 6;    // mount plate thickness
rib_t     = 6;
span      = 56;   // mount plate front face -> front wall back face
front_t   = 6;
rod_y     = 0;    // rods and marker are coplanar so the spring load is on-axis
servo_y   = 26;   // servo bracket bolt line, above the rods

module rod_axes()
    for (x = [-rod_spacing/2, rod_spacing/2]) translate([x, rod_y, 0]) children();

module mount_plate() {
    difference() {
        translate([-base_w/2, -base_h/2, 0]) cube([base_w, base_h, base_t]);

        // gantry plate: 4x M5 on the 20 mm grid, counterbored so the bolt
        // heads sit flush and the shuttle can travel to the plate face
        for (x = [-plate_grid/2, plate_grid/2], y = [-plate_grid/2, plate_grid/2])
            translate([x, y, -eps]) {
                cylinder(d = m5_clear, h = base_t + 2*eps);
                cylinder(d = m5_head_d, h = m5_head_h);
            }

        // rod seats - press fit, blind is fine, through is easier to clear
        rod_axes() translate([0, 0, -eps]) cylinder(d = rod_press, h = base_t + 2*eps);

        // marker clearance so a long marker can retract past the plate
        translate([0, rod_y, -eps]) cylinder(d = pen_clear_d, h = base_t + 2*eps);
    }
}

module front_wall() {
    translate([0, 0, base_t + span]) difference() {
        translate([-base_w/2, -base_h/2, 0]) cube([base_w, base_h, front_t]);
        rod_axes() translate([0, 0, -eps]) cylinder(d = rod_press, h = front_t + 2*eps);
        // the marker passes through here; this hole is the final tip guide,
        // so keep it snug-ish - it is what stops the pen wobbling at speed
        translate([0, rod_y, -eps]) cylinder(d = pen_clear_d, h = front_t + 2*eps);
    }
}

module side_ribs() {
    for (s = [-1, 1])
        translate([s * (base_w/2 - rib_t), -base_h/2, base_t])
            cube([rib_t, base_h, span]);
}

module servo_bracket_bosses() {
    // 2x M3 on the left rib for servo_bracket_sg90.scad, slotted THERE not here
    for (z = [base_t + 14, base_t + 34])
        translate([-base_w/2 - eps, servo_y, z]) rotate([0, 90, 0])
            cylinder(d = m3_clear, h = rib_t + 2*eps);
}

difference() {
    union() { mount_plate(); side_ribs(); front_wall(); }
    servo_bracket_bosses();
}

// PRINT: flat on the mount plate, 4 perimeters, 40% infill, no supports needed
// if you print it lying on its back (the ribs self-support at 90 deg).
