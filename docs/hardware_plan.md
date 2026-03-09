# ArtBot Hardware Execution Plan

## Frame & Mounting Overview

```
        ┌─────────────────────────────────────────────────────────────┐
        │  WHITEBOARD (180cm x 120cm, mounted to wall/stand)         │
        │                                                             │
  Motor ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● Motor
  Y-Left│  ↑ Pulley                                    Pulley ↑  │Y-Right
        │  │                                                  │  │
        │  │  Belt (vertical)                   Belt (vertical)│  │
        │  │                                                  │  │
        │  │    ┌──────────────────────────────────────┐      │  │
        │  │    │         X-RAIL (180cm 2040)           │      │  │
        │  │    │   ◄── Pen Carriage ──►               │      │  │
        │  │    │   [Motor X] [Servo Z] [Pen]          │      │  │
        │  │    └──────────────────────────────────────┘      │  │
        │  │                                                  │  │
        │  │  ← 5cm buffer everywhere →                       │  │
        │  │                                                  │  │
        │  ↓                                          ↓       │  │
        │  Idler                                    Idler     │  │
        └─────────────────────────────────────────────────────────┘
               ↑                                      ↑
          Counterweight                          Counterweight
          (behind board)                         (behind board)
```

---

## Bill of Materials (BOM)

### Structural — Rails & Extrusions

| Item | Spec | Qty | Purpose |
|------|------|-----|---------|
| V-Slot 2040 Aluminum Extrusion | 180cm length | 1 | X-axis horizontal rail |
| V-Slot 2020 Aluminum Extrusion | 120cm length | 2 | Y-axis vertical rails (left & right) |
| V-Slot 2020 Aluminum Extrusion | 180cm length | 2 | Top & bottom frame cross-members |
| 90-degree angle brackets | Standard V-Slot | 8 | Corner joints for the frame |
| T-nuts + M5 bolts | M5x8mm | 50+ pack | Securing everything to extrusions |
| L-brackets or corner plates | Aluminum | 4 | Reinforce frame corners |

**Note on X-rail**: Use 2040 (not 2020) for the horizontal rail. It's twice as rigid and resists bowing at center. If budget allows, a 4040 profile is even better but heavier (adjust counterweight accordingly).

**Mid-span support**: Bolt a flat aluminum bar (3mm thick, ~30mm wide, 180cm long) to the back of the 2040 X-rail to stiffen it further. This costs almost nothing and eliminates center sag.

### Motion — Belts, Pulleys, Carriages

| Item | Spec | Qty | Purpose |
|------|------|-----|---------|
| GT2 Timing Belt (open-ended) | 6mm wide | 10m roll | X-axis + both Y-axis runs |
| GT2 Pulley (20-tooth, 5mm bore) | Aluminum | 3 | One per motor shaft |
| GT2 Idler Pulley (20-tooth, smooth or toothed) | 5mm bore | 5 | Belt routing: 2 for Y-axis bottom, 2 for Y-axis top (counterweight side), 1 for X-axis end |
| V-Slot Gantry Plate (or OpenBuilds Mini V Wheel Plate) | Standard | 3 | 2 for X-rail ends riding on Y-rails, 1 for pen carriage on X-rail |
| Mini V-Wheels (Delrin) | Standard OpenBuilds | 12 | 4 per gantry plate (smooth rolling on V-slot) |
| Eccentric Spacers | Standard | 6 | 2 per gantry plate (for adjusting wheel tension) |
| Belt Tensioner / Spring Idler | Adjustable | 3 | One per belt run — CRITICAL for 180cm X-belt |

**Belt length breakdown**:
- X-axis belt: ~380cm (180cm each direction + wrap around pulleys + slack)
- Y-left belt: ~260cm (120cm each direction + wrap + counterweight routing)
- Y-right belt: ~260cm (same)
- Total: ~9m minimum → buy 10m to be safe

### Motors & Servo

| Item | Spec | Qty | Purpose |
|------|------|-----|---------|
| NEMA 17 Stepper Motor | >45 Ncm (63 oz-in), 1.5A–2A per phase | 3 | 2x Y-axis, 1x X-axis |
| SG90 Micro Servo | Standard | 1 | Z-axis pen up/down |
| NEMA 17 Motor Mounting Bracket | L-shaped, steel or aluminum | 3 | Bolting motors to extrusions |

**Motor positioning**:
- **Y-Left Motor**: Mounted at the TOP-LEFT corner, shaft pointing forward, pulley faces the board
- **Y-Right Motor**: Mounted at the TOP-RIGHT corner, shaft pointing forward, pulley faces the board
- **X Motor**: Mounted directly ON the horizontal X-rail, at the LEFT end, shaft perpendicular to rail
- **Servo**: Mounted on the pen carriage plate, arm controls a lever that retracts the pen

**CRITICAL — Y-Motor Wiring**:
The two Y-motors face OPPOSITE directions physically (mirrored on left vs right). When you clone Y to A on the CNC Shield, both drivers send identical step/direction signals. But because the motors are mirrored, one will push up while the other pushes down → the rail jams.

**Fix**: On ONE of the two Y-motors (pick either), swap the wiring of one coil pair. If the motor connector has 4 wires [A+ A- B+ B-], swap A+ and A- on that one motor. This reverses its rotation, making both motors move the rail in the same direction.

Test: power up, send a small Y move. If the rail moves smoothly, you're good. If it locks/jams/grinds, you swapped the wrong pair — try swapping B+/B- instead.

### Electronics

| Item | Spec | Qty | Purpose |
|------|------|-----|---------|
| Arduino Uno R3 | Original or clone | 1 | GRBL controller |
| CNC Shield V3 | Fits Arduino Uno | 1 | Motor driver interface |
| TMC2209 Stepper Driver Module | StepStick form factor | 3 | Drives the 3 NEMA 17s |
| 12V 10A Power Supply | Mean Well or equivalent, DC barrel or screw terminal | 1 | Powers motors + Arduino |
| Limit Switches (microswitch) | Normally-Open (NO), lever type | 3 | Homing: X-min, Y-min, (optional Z) |
| Wires / Dupont Jumpers | 22 AWG, assorted | 1 pack | General wiring |
| Drag Chain | 10x10mm or 10x15mm, flexible | 2m | Cable management for X-carriage wires |
| USB-B Cable | Standard Arduino | 1 | Connect Arduino to PC/Pi |

**Power supply sizing**:
- Each NEMA 17 at peak: ~2A per phase × 12V = 24W
- 3 motors simultaneous: ~72W peak
- 12V × 10A = 120W → gives ~40% headroom for spikes
- A 5A PSU WILL brown-out during fast diagonal moves — get 10A minimum

### Counterweight System

| Item | Spec | Qty | Purpose |
|------|------|-----|---------|
| Nylon Cord or Paracord | 3mm, rated >20kg | 5m | Connect X-rail to counterweights |
| Small Pulleys | Bearing type, 20-30mm diameter | 4 | 2 top-left, 2 top-right (route cable over top of frame) |
| Counterweight mass | Steel plates, sand bags, or water bottles | As needed | Must equal X-rail assembly weight |

**How to determine counterweight mass**:
1. Assemble the X-rail completely: rail + carriage + X-motor + servo + pen holder + brackets + belt clamps
2. Weigh it on a kitchen/bathroom scale
3. Your counterweight should be ~95-100% of that weight
4. Start at 95% (slightly light) so the rail gently settles down rather than floating up

**Pulley routing** (per side):
```
  Motor [Y]──Pulley at top─── Belt goes DOWN to X-rail bracket
                                        │
  Behind board:  X-rail bracket ───Cord──┤
                                         │
                                    ┌────┴────┐
                                    │Pulley at│
                                    │  top    │
                                    └────┬────┘
                                         │
                                    Counterweight
                                    (hangs behind board)
```

### Pen Mechanism

| Item | Spec | Qty | Purpose |
|------|------|-----|---------|
| Compression Spring | Light, ~10mm OD, ~20mm length | 1 | Pushes pen toward board |
| Pen Holder (3D print or buy) | Fits standard whiteboard markers | 1 | Holds the pen |
| Linear Bearing or Smooth Rod | 8mm diameter, ~50mm length | 1 | Pen slides in/out |
| 3D-Printed Pen Carriage Mount | Custom | 1 | Holds spring + pen + servo together |

**How the pen mechanism works**:
```
  Board Surface    ← Spring pushes pen this way
       │
       │   [Pen Tip]──[Pen Body]──[Spring]──[Backstop]
       │                                        │
       │                              [Servo Arm]
       │                              (retracts pen when pen-up)
```
- **Pen Down (M3 S90)**: Servo rotates to release position → spring pushes pen against board
- **Pen Up (M5)**: Servo rotates to pull pen back from board → pen lifts off surface

---

## Assembly Sequence

### Phase 1: Frame (Day 1-2)

1. **Lay out the frame on the floor** (easier than working vertical)
   - Bottom rail: 180cm 2020 horizontal
   - Top rail: 180cm 2020 horizontal
   - Left rail: 120cm 2020 vertical
   - Right rail: 120cm 2020 vertical
2. **Square the corners** — measure BOTH diagonals. They must be equal (within 2mm). If not, your drawings will be skewed.
3. **Bolt corners** with angle brackets + T-nuts. Tighten firmly.
4. **Mount the frame** to the whiteboard or a separate backing structure. Use at least 6 mounting points.

### Phase 2: Y-Axis Rails & Motors (Day 3-4)

1. **Install V-wheels on the two Y-axis gantry plates** (these carry the X-rail)
2. **Slide gantry plates onto the left and right vertical rails** — adjust eccentric spacers so wheels grip snugly but still roll freely
3. **Mount Y-Left motor** at top-left corner, pulley facing inward
4. **Mount Y-Right motor** at top-right corner, pulley facing inward
5. **Install idler pulleys** at the bottom of each vertical rail
6. **Route Y-axis belts**: Motor pulley → down to idler → back up to gantry plate. Attach belt ends to gantry plate with belt clamps.
7. **Test**: Turn both motor shafts BY HAND. Both gantry plates should move up and down smoothly and evenly.

### Phase 3: X-Axis Rail (Day 5-6)

1. **Bolt the 180cm 2040 rail horizontally** between the two Y-axis gantry plates
2. **Check level** — the X-rail must be perfectly horizontal. Shim if needed.
3. **Install pen carriage gantry plate** onto the X-rail with V-wheels
4. **Mount X-motor** at the left end of the X-rail
5. **Install X-axis idler pulley** at the right end
6. **Route X-axis belt**: Motor → along rail → around idler → back to carriage. Clamp both belt ends to the carriage plate.
7. **Install belt tensioner** on the X-axis — this is the longest belt run and WILL sag without tensioning
8. **(Optional) Bolt mid-span stiffener** to the back of the 2040 rail

### Phase 4: Counterweights (Day 6-7)

1. **Weigh the entire X-rail assembly** (with motor, carriage, servo, everything mounted)
2. **Install pulleys at the top of the frame** — 2 per side, behind the board
3. **Attach cord** to both ends of the X-rail, route over pulleys, hang weights
4. **The One-Finger Test**: Push the X-rail with ONE finger. It should move easily and STAY where you leave it. If it drifts down, add weight. If it drifts up, remove weight.
5. **Lock in the counterweight** — once balanced, secure the weights so they can't shift

### Phase 5: Electronics (Day 7-8)

1. **Flash GRBL onto the Arduino** (use Arduino IDE, flash grbl firmware hex)
2. **Plug CNC Shield onto Arduino**
3. **Insert TMC2209 drivers** into X, Y, and A slots
   - **Set the A-axis jumper** on the CNC Shield to clone Y
4. **Wire motors**:
   - X-motor → X driver slot
   - Y-Left motor → Y driver slot
   - Y-Right motor → A driver slot (Y clone)
   - **REVERSE ONE Y-MOTOR'S COIL** (swap A+ and A- on one of them)
5. **Wire servo** → SpnEn pin on CNC Shield (or a separate Arduino pin with GRBL servo mod)
6. **Wire limit switches**:
   - X-min switch → X-limit pins
   - Y-min switch → Y-limit pins
   - Connect as Normally Open (NO) to GND and signal
7. **Mount limit switches**:
   - X-min: at the LEFT end of the X-rail (pen carriage triggers it)
   - Y-min: at the TOP of one vertical rail (X-rail triggers it when fully up)
   - "Min" means the home position. Home = top-left corner = origin (0,0)
8. **Connect 12V PSU** to the CNC Shield power input
9. **Connect Arduino via USB** to your laptop

### Phase 6: Calibration & First Draw (Day 9-10)

1. **Connect to GRBL** via Universal Gcode Sender (UGS) or CNCjs
2. **Configure GRBL parameters**:
   ```
   $100=80    ; X steps/mm
   $101=80    ; Y steps/mm
   $110=5000  ; X max feed rate mm/min
   $111=5000  ; Y max feed rate mm/min
   $120=200   ; X acceleration mm/s^2 (start low, increase gradually)
   $121=100   ; Y acceleration mm/s^2 (lower than X — heavy rail)
   $130=1700  ; X max travel mm
   $131=1100  ; Y max travel mm
   $22=1      ; Enable homing
   $23=3      ; Homing direction invert (both X and Y home to min)
   ```
3. **Home the machine**: Send `$H`. The machine should move to top-left, hit both limit switches, and stop.
4. **Test movement**: Jog X +100mm (should move RIGHT). Jog Y +100mm (should move DOWN). If either direction is wrong, flip the `$3` direction invert mask.
5. **Draw a test square**:
   ```gcode
   G21
   G90
   G0 X50 Y50 F5000
   M3 S90
   G4 P0.15
   G1 X200 Y50 F3000
   G1 X200 Y200
   G1 X50 Y200
   G1 X50 Y50
   M5
   G0 X0 Y0 F5000
   M2
   ```
   This draws a 150mm square. Measure it with a ruler. If it's not 150mm, your steps/mm ($100/$101) need adjusting.

---

## Wiring Diagram (Block Level)

```
                    ┌──────────────┐
   12V 10A PSU ────►│  CNC Shield  │
                    │    V3        │
                    │  ┌────────┐  │
                    │  │Arduino │  │◄──── USB to PC
                    │  │  Uno   │  │
                    │  │ (GRBL) │  │
                    │  └────────┘  │
                    │              │
                    │  X-Driver ───┼──── X Motor (NEMA 17)
                    │  (TMC2209)   │
                    │              │
                    │  Y-Driver ───┼──── Y-Left Motor (NEMA 17)
                    │  (TMC2209)   │
                    │              │
                    │  A-Driver ───┼──── Y-Right Motor (NEMA 17)
                    │  (TMC2209)   │     ⚠ ONE COIL PAIR REVERSED
                    │  [Y clone]   │
                    │              │
                    │  SpnEn ──────┼──── SG90 Servo (Pen Z)
                    │              │
                    │  X-Lim ──────┼──── Limit Switch (X home)
                    │  Y-Lim ──────┼──── Limit Switch (Y home)
                    └──────────────┘
```

---

## What Can Go Wrong (Failure Modes)

| Failure | Cause | Prevention |
|---------|-------|------------|
| Rail crashes down on power loss | No counterweight or belt breaks | Counterweights hold rail in place even with no power |
| Skipped steps (drawing shifts mid-job) | Acceleration too high, PSU too weak, belt too loose | Tune $120/$121 conservatively, use 10A PSU, tension belts |
| Y-axis jams on startup | Both Y-motors fighting each other | Reverse one motor's coil wiring |
| Drawing is skewed/rhombus | Frame not square | Measure diagonals during assembly |
| Pen doesn't touch board consistently | Spring too weak, or servo range wrong | Tune spring compression, calibrate servo angle |
| Belt skips teeth | Belt too loose, pulley grub screw loose | Belt tensioners + Loctite on grub screws |
| X-rail bows at center | 180cm span too long for 2020 profile | Use 2040 profile + mid-span stiffener |
| Homing fails or overshoots | Limit switch not triggering, wrong GRBL config | Test switches manually, check $22/$23/$24/$25 |
| Lines are wavy/vibrating | Rail chatter from high speed | Lower feed rate, stiffen X-rail, reduce acceleration |

---

## Procurement Priority

Buy in this order so you can start building while waiting for later shipments:

1. **First** (frame + rails): V-Slot extrusions, brackets, T-nuts, bolts
2. **Second** (motion): V-wheels, gantry plates, eccentric spacers, GT2 belt, pulleys, tensioners
3. **Third** (motors): 3x NEMA 17 + mounting brackets + SG90 servo
4. **Fourth** (electronics): Arduino Uno, CNC Shield V3, 3x TMC2209, 12V 10A PSU, limit switches, wires, drag chain
5. **Last** (pen): Spring, pen holder, 3D-print the carriage mount (or iterate on cardboard prototype first)
