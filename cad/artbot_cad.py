#!/usr/bin/env python3
"""
ArtBot - full parametric CAD assembly.

Real B-rep solids via build123d/OpenCascade. Exports STEP (opens in Fusion 360,
SolidWorks, FreeCAD, Onshape) plus STL per printable part.

    pip install build123d
    python3 artbot_cad.py

Coordinate frame, board plane upright:
    X = along the horizontal rail      Y = up      Z = out of the board
The 7 deg lean is applied to the whole rig at the end; the legs are computed
in world coordinates to land on the floor.

Parts are kept as SEPARATE solids in a Compound - not fused - so the STEP opens
as an assembly tree you can pick apart, not one welded blob.
"""
from build123d import *
import math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ============================ parameters ============================
FRAME_W, FRAME_H = 1800.0, 1200.0     # outer envelope of the board frame
EXT              = 20.0
WORK_W, WORK_H   = 1600.0, 980.0      # real pen travel (see engineering notes)
STANDOFF         = 55.0               # board surface -> back face of the rail
LEAN             = 7.0                # degrees, leaning back
RISER            = 700.0              # board bottom above the floor
BOARD_T          = 20.0

PITCH_R  = 20 * 2 / (2 * math.pi)     # 20T GT2 pitch radius = 6.366 mm
BELT_W   = 6.0
BELT_T   = 1.4

NEMA_BODY, NEMA_LEN = 56.4, 76.0      # NEMA 23, 1.9 N.m class
NEMA_BC             = 47.14           # bolt circle, square
NEMA_BOSS           = 38.1
NEMA_SHAFT          = 8.0

HW = FRAME_W/2 - EXT/2
HH = FRAME_H/2 - EXT/2
RAIL_Z = STANDOFF + EXT/2

parts = []          # (name, solid, printable?, space)  space: "rig" | "world"
def add(name, solid, printable=False, space="rig"):
    parts.append((name, solid, printable, space))
    return solid

def rod_between(a, b, r):
    """Round strut spanning two world points."""
    d = Vector(b[0]-a[0], b[1]-a[1], b[2]-a[2])
    L = d.length
    if L < 1: return None
    s = Cylinder(r, L)
    n = d.normalized()
    dot = max(-1.0, min(1.0, Vector(0,0,1).dot(n)))
    ang = math.degrees(math.acos(dot))
    if abs(ang) > 1e-6 and abs(ang-180) > 1e-6:
        ax = Vector(0,0,1).cross(n).normalized()
        s = s.rotate(Axis((0,0,0), (ax.X, ax.Y, ax.Z)), ang)
    elif abs(ang-180) <= 1e-6:
        s = s.rotate(Axis.X, 180)
    return Pos((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2) * s

# ============================ profiles ============================
def _slot(face_len):
    y0 = face_len/2
    pts = [(-5.6, y0+0.1), (-3.1, y0-2.5), (-3.1, y0-4.3),
           (-5.8, y0-4.3), (-5.8, y0-7.3), ( 5.8, y0-7.3),
           ( 5.8, y0-4.3), ( 3.1, y0-4.3), ( 3.1, y0-2.5),
           ( 5.6, y0+0.1)]
    return make_face(Polyline(*pts, close=True))

def vslot(w, h):
    """V-slot cross-section: T-channels with the 45 deg V mouth, plus centre bores."""
    s = Rectangle(w, h)
    for sy in ([0] if h <= 20 else [-h/4, h/4]):
        s -= Pos(0, sy) * (Rot(0, 0,  90) * _slot(w))
        s -= Pos(0, sy) * (Rot(0, 0, -90) * _slot(w))
    for sx in ([0] if w <= 20 else [-w/4, w/4]):
        s -= Pos(sx, 0) * _slot(h)
        s -= Pos(sx, 0) * (Rot(0, 0, 180) * _slot(h))
    for by in ([0] if h <= 20 else [-h/4, h/4]):
        s -= Pos(0, by) * Circle(2.1)
    return s

PROF_2020 = vslot(20, 20)
PROF_2040 = vslot(20, 40)

def bar(profile, length, along="z"):
    b = extrude(profile, amount=length)
    b = Pos(0, 0, -length/2) * b          # centre it on its own origin
    if along == "x": b = Rot(0, 90, 0) * b
    if along == "y": b = Rot(-90, 0, 0) * b
    return b

# ============================ fasteners ============================
def m5_bolt(length=10.0):
    """M5 socket head cap screw, head at origin pointing -Z."""
    return (Cylinder(4.25, 5, align=(Align.CENTER, Align.CENTER, Align.MAX))
            + Cylinder(2.5, length, align=(Align.CENTER, Align.CENTER, Align.MIN)))

def t_nut():
    """Drop-in M5 T-nut for a 6 mm slot."""
    return ((Box(10.6, 6.0, 3.0) + Pos(0, 0, 2.6) * Box(6.0, 6.0, 2.2))
            - Cylinder(2.6, 12))

def corner_bracket():
    """20x20 90 degree angle bracket, 2 x M5."""
    b = Box(20, 20, 3, align=(Align.CENTER, Align.MIN, Align.MIN)) \
      + Box(20, 3, 20, align=(Align.CENTER, Align.MIN, Align.MIN))
    b -= Pos(0, 11, 0) * Cylinder(2.6, 12)
    b -= Pos(0, 0, 11) * (Rot(90, 0, 0) * Cylinder(2.6, 12))
    return b

# ============================ machine parts ============================
def nema23():
    """NEMA 23. Body, pilot boss, shaft, 4 bolt holes on the 47.14 square."""
    m = Box(NEMA_BODY, NEMA_BODY, NEMA_LEN)
    m = fillet(m.edges().filter_by(Axis.Z), 4)
    m += Pos(0, 0, -NEMA_LEN/2 - 0.8) * Cylinder(NEMA_BOSS/2, 1.6)
    m += Pos(0, 0, -NEMA_LEN/2 - 12)  * Cylinder(NEMA_SHAFT/2, 24)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m -= Pos(sx*NEMA_BC/2, sy*NEMA_BC/2, -NEMA_LEN/2 + 5) * Cylinder(2.6, 14)
    return m

def pulley20t(bore=8.0):
    """20 tooth GT2 pulley, real tooth count, axis Z."""
    p = Cylinder(PITCH_R + 0.6, 7.4)
    for i in range(20):
        a = i / 20 * 2 * math.pi
        p += Pos(math.cos(a)*(PITCH_R+0.35), math.sin(a)*(PITCH_R+0.35), 0) \
             * Box(1.2, 1.2, 6.6)
    for z in (-4.6, 4.6):
        p += Pos(0, 0, z) * Cylinder(PITCH_R + 2.6, 1.5)
    p -= Cylinder(bore/2, 20)
    return p

def belt_run(a, b, width=BELT_W):
    """A straight length of GT2 between two points (Vector-like tuples)."""
    ax, ay, az = a; bx, by, bz = b
    d = Vector(bx-ax, by-ay, bz-az)
    L = d.length
    if L < 1: return None
    s = Box(width, BELT_T, L)
    s = Rot(0, 0, 0) * s
    # orient +Z along d
    zaxis = Vector(0, 0, 1)
    n = d.normalized()
    dot = max(-1.0, min(1.0, zaxis.dot(n)))
    ang = math.degrees(math.acos(dot))
    if abs(ang) > 1e-6 and abs(ang - 180) > 1e-6:
        axis = zaxis.cross(n).normalized()
        s = Rotation(*(0,0,0)) * s
        s = s.rotate(Axis((0,0,0), (axis.X, axis.Y, axis.Z)), ang)
    elif abs(ang - 180) <= 1e-6:
        s = s.rotate(Axis.X, 180)
    return Pos((ax+bx)/2, (ay+by)/2, (az+bz)/2) * s

def gantry_plate():
    """OpenBuilds Mini-V style plate, 20 mm M5 grid."""
    p = Box(62, 62, 6)
    p = fillet(p.edges().filter_by(Axis.Z), 6)
    for gx in (-20, 0, 20):
        for gy in (-20, 0, 20):
            p -= Pos(gx, gy, 0) * Cylinder(2.6, 10)
    for wx in (-1, 1):
        for wy in (-1, 1):
            p -= Pos(wx*30, wy*22, 0) * Cylinder(3.2, 10)
    return p

def v_wheel():
    """Delrin V-wheel: two 45 deg cones back to back."""
    w = Cone(12, 8.5, 4.2, align=(Align.CENTER, Align.CENTER, Align.MIN)) \
      + Rot(180, 0, 0) * Cone(12, 8.5, 4.2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    w -= Cylinder(2.6, 20)
    return w

def spring(free_len=14.0, rad=6.2, coils=5, wire=0.9):
    """Real helical compression spring. Falls back to a tube if the sweep fails."""
    try:
        h = Helix(pitch=free_len/coils, height=free_len, radius=rad)
        sec = Plane(origin=h @ 0, z_dir=h % 0) * Circle(wire)
        return sweep(sec, path=h, is_frenet=True)
    except Exception as e:
        print("   ! spring sweep failed (%s) - using a plain tube" % e)
        return Cylinder(rad+wire, free_len) - Cylinder(rad-wire, free_len+1)

def sg90():
    s = Box(23.0, 12.4, 22.6)
    s += Pos(0, 0, 1.0) * Box(32.2, 12.4, 2.6)
    s += Pos(-5.9, 0, 13.5) * Cylinder(6, 4.5)
    return s

def micro_switch():
    s = Box(20, 6.5, 10)
    s += Pos(2, 0, 7) * Box(18, 1.0, 1.2)
    for x in (-4.75, 4.75):
        s -= Pos(x, 0, 0) * (Rot(90, 0, 0) * Cylinder(1.3, 10))
    return s

t0 = time.time()
print("building...")

# ============================ frame ============================
add("upright_left_2020",  Pos(-HW, 0, 10) * bar(PROF_2020, FRAME_H, "y"))
add("upright_right_2020", Pos( HW, 0, 10) * bar(PROF_2020, FRAME_H, "y"))
add("cross_top_2020",     Pos(0,  HH, 10) * bar(PROF_2020, FRAME_W - 2*EXT, "x"))
add("cross_bottom_2020",  Pos(0, -HH, 10) * bar(PROF_2020, FRAME_W - 2*EXT, "x"))

for i, (bx, by, rz) in enumerate([(-HW, HH, 0), (HW, HH, 90), (HW, -HH, 180), (-HW, -HH, 270)]):
    add("corner_bracket_%d" % i, Pos(bx, by, 22) * (Rot(0, 0, rz) * corner_bracket()))

# whiteboard, sitting inside the frame, retained by brackets - never drilled
add("whiteboard", Pos(0, 0, -BOARD_T/2 - 2) * Box(FRAME_W - 40, FRAME_H - 40, BOARD_T))

# ============================ Y axis ============================
for s in (-1, 1):
    side = "left" if s < 0 else "right"
    add("motor_Y_%s" % side, Pos(s*HW, HH, 70) * nema23())
    add("pulley_Y_%s" % side, Pos(s*HW, HH, 22) * pulley20t(8.0))
    add("idler_Y_%s" % side, Pos(s*HW, -HH, 22) * pulley20t(5.0))
    for z in (-1, 1):
        b = belt_run((s*HW + z*PITCH_R, -HH, 22), (s*HW + z*PITCH_R, HH, 22))
        if b: add("belt_Y_%s_%d" % (side, z), b)

# ============================ X rail + gantry ============================
GY = 0.0    # rail parked at mid travel for the model
add("rail_2040", Pos(0, GY, RAIL_Z) * bar(PROF_2040, FRAME_W, "x"))
add("rail_stiffener", Pos(0, GY, RAIL_Z + 21) * Box(FRAME_W - 30, 30, 3))
for s in (-1, 1):
    side = "left" if s < 0 else "right"
    add("gantry_plate_%s" % side, Pos(s*HW, GY, 34) * gantry_plate())
    for wx in (-1, 1):
        for wy in (-1, 1):
            add("vwheel_%s_%d%d" % (side, wx, wy),
                Pos(s*HW + wx*30, GY + wy*22, 24) * v_wheel())

add("motor_X", Pos(-HW + 60, GY, RAIL_Z + 60) * nema23())
add("pulley_X", Pos(-HW + 60, GY, RAIL_Z + 12) * pulley20t(8.0))
add("idler_X", Pos(HW - 46, GY, RAIL_Z + 12) * pulley20t(5.0))
for z in (-1, 1):
    b = belt_run((-HW + 60, GY + z*PITCH_R, RAIL_Z + 12), (HW - 46, GY + z*PITCH_R, RAIL_Z + 12))
    if b: add("belt_X_%d" % z, b)

# ============================ pen carriage ============================
CX = 0.0
MP_Z, FW_Z = RAIL_Z + 27, RAIL_Z - 35

mount = Box(90, 76, 8)
for gx in (-10, 10):
    for gy in (-10, 10):
        mount -= Pos(gx, gy, 0) * Cylinder(2.7, 12)
for rx in (-20, 20):
    mount -= Pos(rx, 0, 0) * Cylinder(4.0, 12)
mount -= Cylinder(12, 12)
add("carriage_mount_plate", Pos(CX, GY, MP_Z) * mount, printable=True)

front = Box(90, 76, 8)
for rx in (-20, 20):
    front -= Pos(rx, 0, 0) * Cylinder(4.0, 12)
front -= Cylinder(12, 12)
add("carriage_front_wall", Pos(CX, GY, FW_Z) * front, printable=True)

for s in (-1, 1):
    add("carriage_rib_%d" % s,
        Pos(CX + s*42, GY, (MP_Z+FW_Z)/2) * Box(6, 76, MP_Z - FW_Z), printable=True)
for rx in (-20, 20):
    add("guide_rod_%d" % rx, Pos(CX + rx, GY, (MP_Z+FW_Z)/2) * Cylinder(4, MP_Z - FW_Z))

shut = Box(62, 34, 18)
shut -= Pos(0, 17, 0) * Box(62, 3.2, 18)
shut -= Cylinder(6.0, 20)                       # Sharpie: 12 mm barrel
for rx in (-20, 20):
    shut -= Pos(rx, 0, 0) * Cylinder(4.25, 20)
shut -= Pos(0, 11, 0) * (Rot(0, 90, 0) * Cylinder(1.7, 70))
add("pen_shuttle", Pos(CX, GY, RAIL_Z) * shut, printable=True)

for rx in (-20, 20):
    add("spring_%d" % rx, Pos(CX + rx, GY, RAIL_Z + 9) * spring())

add("servo_sg90", Pos(CX - 52, GY + 26, RAIL_Z - 12) * sg90())
add("sharpie", Pos(CX, GY, RAIL_Z - 34) * Cylinder(6, 130))

# ============================ base, legs, electronics ============================
COS, SIN = math.cos(math.radians(LEAN)), math.sin(math.radians(LEAN))
rig_y = RISER + (FRAME_H/2) * COS

def W(x, y, z=0.0):
    """Rig-local (x,y,z) -> world, after the lean and the riser."""
    return (x, rig_y + y*COS - z*SIN, y*(-SIN) + z*COS)

# legs, toes, rear braces - all in WORLD space, they must reach the floor
for s_ in (-1, 1):
    fb = W(s_*HW, -FRAME_H/2 + 10)
    gnd = (fb[0], 0.0, fb[2])
    r = rod_between(fb, gnd, 15);                          add("leg_%d" % s_, r, space="world")
    r = rod_between(gnd, (fb[0], 0.0, fb[2] + 430), 12);   add("toe_%d" % s_, r, space="world")
    mid = W(s_*HW, 60)
    r = rod_between(mid, (fb[0], 0.0, fb[2] - 820), 13);   add("brace_%d" % s_, r, space="world")
    add("foot_pad_f_%d" % s_, Pos(fb[0], 9, fb[2] + 430) * Box(170, 18, 100), space="world")
    add("foot_pad_r_%d" % s_, Pos(fb[0], 9, fb[2] - 820) * Box(170, 18, 100), space="world")

lf, rf = W(-HW, -FRAME_H/2 + 10), W(HW, -FRAME_H/2 + 10)
r = rod_between((lf[0], 240, lf[2]), (rf[0], 240, rf[2]), 11)
add("base_tie", r, space="world")

# control enclosure hangs off the left rear brace
ex, ez = W(-HW, 60)[0], W(-HW, 60)[2] - 430
add("enclosure", Pos(ex, 430, ez) * Box(300, 210, 130), space="world")
for i in range(3):
    add("tb6600_%d" % i, Pos(ex - 84 + i*84, 470, ez + 60) * Box(56, 96, 22), space="world")
add("psu_24v", Pos(ex, 330, ez + 55) * Box(215, 50, 115), space="world")
add("arduino_shield", Pos(ex + 90, 340, ez + 60) * Box(69, 25, 53), space="world")

# ============================ fasteners ============================
# M5 throughout. Bolt heads face out, T-nuts sit in the slot behind.
def bolted(name, x, y, z, rx=0, ry=0, rz=0, blen=10):
    add("bolt_" + name, Pos(x, y, z) * (Rot(rx, ry, rz) * m5_bolt(blen)))
    add("tnut_" + name, Pos(x, y, z) * (Rot(rx, ry, rz) * (Pos(0, 0, blen) * t_nut())))

nb = 0
# frame corners: 2 bolts per bracket leg
for cx, cy, sx, sy in ((-HW, HH, 1, -1), (HW, HH, -1, -1), (HW, -HH, -1, 1), (-HW, -HH, 1, 1)):
    bolted("cnr%d_a" % nb, cx + sx*11, cy, 34, ry=0);        nb += 1
    bolted("cnr%d_b" % nb, cx, cy + sy*11, 34, ry=0);        nb += 1

# NEMA 23 mounts: 4 per motor on the 47.14 square
for mx, my, mz in ((-HW, HH, 70+NEMA_LEN/2), (HW, HH, 70+NEMA_LEN/2),
                   (-HW+60, GY, RAIL_Z+60+NEMA_LEN/2)):
    for ox in (-NEMA_BC/2, NEMA_BC/2):
        for oy in (-NEMA_BC/2, NEMA_BC/2):
            bolted("mot%d" % nb, mx+ox, my+oy, mz, blen=14); nb += 1

# gantry plates onto the rail, 4 each on the 20 mm grid
for s_ in (-1, 1):
    for ox in (-20, 20):
        for oy in (-20, 20):
            bolted("gp%d" % nb, s_*HW+ox, GY+oy, 40); nb += 1

# pen carriage onto its plate
for ox in (-10, 10):
    for oy in (-10, 10):
        bolted("car%d" % nb, CX+ox, GY+oy, MP_Z+6); nb += 1

# board retention: L-brackets clamping the board frame - the board is NEVER drilled
for bx, by in ((-700, HH), (0, HH), (700, HH), (-700, -HH), (0, -HH), (700, -HH)):
    add("board_clip_%d" % nb, Pos(bx, by, 4) * Box(40, 24, 6)); nb += 1
    bolted("bd%d" % nb, bx, by, 18); nb += 1

print("   %d fastener positions" % nb)

add("limit_switch_X", Pos(-HW + 40, GY - 50, 30) * micro_switch())
add("limit_switch_Y", Pos(-HW + 30, HH - 60, 30) * micro_switch())

print("   %d solids in %.1fs" % (len(parts), time.time() - t0))

# ============================ export ============================
rig_solids   = [p for _, p, _, sp in parts if sp == "rig"   and p is not None]
world_solids = [p for _, p, _, sp in parts if sp == "world" and p is not None]

rig = Compound(label="rig", children=list(rig_solids))
rig = Pos(0, rig_y, 0) * (Rot(-LEAN, 0, 0) * rig)

machine = Compound(label="ArtBot", children=[rig] + list(world_solids))
# CAD convention is Z-up; the model is built Y-up to match the 3D viewer.
machine = Rot(90, 0, 0) * machine

t1 = time.time()
step_path = os.path.join(OUT, "artbot_assembly.step")
export_step(machine, step_path)
print("   STEP  %-34s %6.1f MB  (%.1fs)" %
      (os.path.basename(step_path), os.path.getsize(step_path)/1e6, time.time()-t1))

t1 = time.time()
stl_path = os.path.join(OUT, "artbot_assembly.stl")
export_stl(machine, stl_path)
print("   STL   %-34s %6.1f MB  (%.1fs)" %
      (os.path.basename(stl_path), os.path.getsize(stl_path)/1e6, time.time()-t1))

n = 0
for name, solid, printable, sp in parts:
    if not printable or solid is None: continue
    export_stl(solid, os.path.join(OUT, "print_%s.stl" % name))
    n += 1
print("   %d printable parts exported as individual STL" % n)

bb = machine.bounding_box()
print("   envelope  %.0f x %.0f x %.0f mm (w x d x h)" % (bb.size.X, bb.size.Y, bb.size.Z))

# second moment of area, straight off the real profile
try:
    props = PROF_2040.moments_of_inertia if hasattr(PROF_2040, "moments_of_inertia") else None
    print("\n   2040 profile area %.1f mm2  -> %.3f kg/m (published ~0.90)"
          % (PROF_2040.area, PROF_2040.area * 1000 * 2.70e-6))
except Exception:
    pass
print("\ndone in %.1fs -> %s" % (time.time() - t0, OUT))
