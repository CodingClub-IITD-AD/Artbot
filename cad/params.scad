// ArtBot - shared parameters for all printed parts. Units: mm.
// Anything tagged VERIFY must be measured against the parts actually ordered
// before you burn filament on a full set.

$fn = 64;
eps = 0.01;

/* ---------- fasteners (clearance holes, not tapped) ---------- */
m2_clear   = 2.4;
m3_clear   = 3.4;
m3_nut_af  = 5.6;   // across flats
m3_nut_t   = 2.6;
m5_clear   = 5.4;
m5_head_d  = 9.6;
m5_head_h  = 5.2;

/* ---------- V-slot extrusion ---------- */
vslot      = 20;    // 2020 face width
vslot_2040 = 40;    // 2040 long face

/* ---------- gantry plate bolt grid ----------
   OpenBuilds Mini-V / Xtreme plates all use a 20 mm M5 grid.
   VERIFY the actual hole positions on the plate you buy - vendors differ
   on WHICH grid holes are present, not on the pitch.                      */
plate_grid = 20;

/* ---------- GT2 belt ---------- */
belt_w      = 6;
belt_pitch  = 2;
belt_back   = 0.80;  // thickness behind the teeth
belt_tooth  = 0.75;  // tooth depth

/* ---------- pen shuttle guide rods ---------- */
rod_d       = 8;
rod_press   = 7.85;  // interference fit in the fixed walls (tune per printer)
rod_slide   = 8.5;   // running clearance in the moving shuttle
rod_spacing = 40;    // centre-to-centre, horizontal
rod_len     = 74;    // cut length. base plate + span + front wall

/* ---------- whiteboard marker ---------- */
pen_d       = 17;    // VERIFY: calliper the barrel of the marker you'll use
pen_clear_d = 24;    // pass-through in the front wall

/* ---------- SG90 servo ----------
   Mount holes are SLOTTED in servo_bracket_sg90.scad on purpose: SG90 clones
   vary by ~1 mm and the throw needs fore/aft trimming at assembly anyway.   */
sg90_len     = 23.0;
sg90_wid     = 12.4;
sg90_hgt     = 22.6;
sg90_tab_span = 32.2;  // screw centre to screw centre
sg90_tab_t    = 2.6;
sg90_screw_d  = 2.4;

/* ---------- limit switch (V-153 / KW12 style lever microswitch) ---------- */
sw_hole_pitch = 9.5;  // VERIFY against your switch
sw_hole_d     = 2.6;
