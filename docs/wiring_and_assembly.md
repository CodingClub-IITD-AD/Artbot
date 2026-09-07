# ArtBot - Wiring & Assembly Spec

Supersedes the electronics half of `hardware_plan.md`, which still carries
leftovers from two abandoned design branches (TMC2209 drivers, and the
counterweight system). Corrections are listed at the bottom - read those
before you order anything.

Architecture is unchanged: dual-Y Cartesian, 3x NEMA 23, GRBL on an Arduino
Uno, servo pen lift.

---

## 1. Parts that matter electrically

| Item | Spec | Qty | Note |
|---|---|---|---|
| NEMA 23 stepper | >=120 Ncm holding, 2.5-3.0 A/phase, 1.8 deg | 3 | **Record the shaft diameter when you order** - it sets the pulley bore. Torque derivation in section 1a |
| Stepper driver | external brick, 3 A+ capable | 3 | TB6600 or DM542 - both work, see "Driver choice" in section 2 |
| Arduino Uno R3 | - | 1 | |
| CNC Shield V3 | - | 1 | Used only as a signal breakout here |
| PSU | 24 V, 15 A, screw terminal | 1 | 360 W vs ~150 W real peak. Enclosed case, not open-frame |
| SG90 servo | - | 1 | Runs off Arduino 5 V |
| Lever microswitch | NO contact, V-153 / KW12 style | 2 | X-min, Y-min. No Z switch |
| GT2 pulley, 20T | **bore = motor shaft dia** | 3 | See correction 2 |
| GT2 idler, 20T | 5 mm bore | 3 | Rides on M5 bolts. See correction 3 |

---

## 1a. Why NEMA 23, and the actual torque number

The sizing case is **holding the X rail against gravity on the Y axis**, not
drawing force. A pen needs essentially no torque; the rail hanging off two
belts needs all of it.

    moving mass (rail + carriage + X motor + belts)  3.96 kg
    force                       3.96 x 9.81        = 38.9 N
    20T GT2 pitch radius        40 / (2 * pi)      = 6.37 mm
    per motor, 2 Y motors       (38.9/2) x 0.00637 = 0.124 N.m

So **each Y motor needs 0.124 N.m** to hold station. Steppers keep roughly a
third of holding torque once moving, so a 1.9 N.m NEMA 23 has about
0.57 N.m available: a **4.6x margin**.

**Minimum honest spec: 1.2 N.m (120 N.cm) holding, 2.5-3.0 A/phase, 8 mm
shaft.** The 1.9 N.m in `SHOPPING_LIST.md` is comfortable, not required. If
1.9 is out of stock locally, a 1.5 is fine. Note that NEMA 23 is a *frame
size* (56 mm face, 47.14 mm bolt circle), not a torque rating - 1.2 and 1.9
N.m are both NEMA 23 and share brackets, pulleys and mounting.

**Why NEMA 17 fails, which is the number to quote if asked.** A good NEMA 17
is ~0.45 N.m. Derated for speed: 0.135 N.m against a 0.124 N.m need, a
**1.09x margin**. It holds fine at rest (over 15x on raw holding torque) and
then loses steps the moment it moves. That gap between the static and the
moving case is the entire justification for the larger frame.

**The X motor is deliberately oversized.** X moves a 0.55 kg carriage roughly
horizontally; at a 7 deg lean with $120=200 mm/s^2 it needs on the order of
0.05 N.m. It is a NEMA 23 so that all three motors, drivers, brackets and DIP
settings are interchangeable and the club carries one spare, **not** because
X needs the torque. Do not defend it as a torque requirement.

**Where this is soft:** the 30% speed derating is a rule of thumb, not a
torque-speed curve. The real operating point is 5000 mm/min = 83 mm/s over
40 mm/rev = **125 RPM**, and a 3 A NEMA 23 on 24 V is still near flat there
(the knee is usually 300-600 RPM). So 4.6x is conservative and the true
margin is likely double. If you want it tight, read the curve for the motor
you actually buy at 125 RPM.

---

## 2. Signal wiring - CNC Shield V3 to the drivers

The TB6600s do **not** plug into the shield. Leave all four driver sockets
empty and take STEP/DIR off the socket header pins. The shield is doing one
job: turning GRBL's outputs into labelled screw-terminal-friendly pins.

GRBL / CNC Shield V3 pin map on an Uno:

| Signal | Uno pin | Shield label |
|---|---|---|
| X STEP | D2 | X.STEP |
| Y STEP | D3 | Y.STEP |
| Z STEP | D4 | Z.STEP (unused) |
| X DIR | D5 | X.DIR |
| Y DIR | D6 | Y.DIR |
| Z DIR | D7 | Z.DIR (unused) |
| Stepper enable | D8 | EN (active LOW) |
| X limit | D9 | X+/X- |
| Y limit | D10 | Y+/Y- |
| Spindle PWM -> **servo** | D11 | see section 4 |
| A STEP / A DIR | via clone jumpers | A axis |

### Dual-Y: clone Y onto A

The shield has jumper pads for cloning an axis onto the A driver. Fit the
**two jumpers that clone Y to A**. Both Y motors then receive identical
STEP/DIR. With the sockets empty you can equally just wire the second Y
driver's PUL/DIR straight off D3/D6 in parallel - electrically the same
thing, and one less thing to get wrong. Pick one and write down which.

### Per-driver connections (common-cathode, 5 V logic)

For each TB6600:

```
  PUL+  <- STEP signal   (D2 for X, D3 for both Y drivers)
  PUL-  -> Arduino GND
  DIR+  <- DIR  signal   (D5 for X, D6 for both Y drivers)
  DIR-  -> Arduino GND
  ENA+  -- LEAVE DISCONNECTED
  ENA-  -- LEAVE DISCONNECTED
```

**Why ENA is deliberately unconnected:** GRBL's D8 enable is active LOW,
which is backwards relative to how the TB6600 opto expects to be driven, and
wiring it "the obvious way" leaves the motors disabled. More importantly,
this machine has **no counterweights** - the X-rail is held up purely by
motor torque. Drivers permanently enabled means the rail holds position
whenever the PSU is on, including between jobs. That is the behaviour you
want. The trade: the motors run warm at idle. That is normal for a stepper
and not a fault.

**Ground:** Arduino GND and the TB6600 signal grounds must be common. The
24 V motor supply ground goes only to the drivers' VCC/GND terminals - do
not tie 24 V anywhere near the Arduino.

### Motor power

```
  24 V PSU  V+  ->  VCC on all three drivers
  24 V PSU  V-  ->  GND on all three drivers
  Arduino       ->  powered by USB from the control laptop
```

Do **not** feed 24 V into the CNC Shield's power terminal. Nothing on the
shield needs it once the sockets are empty, and it is one more path to a
dead Arduino.

**PSU sizing.** Motors are rated by current, not watts - "3.0 A/phase" is the
spec, and the 2-3 V on the motor label is just I x R, not what you feed it.
Real draw is set by copper loss: at ~1.2 ohm/phase a motor holding both
phases dissipates 2 x 3^2 x 1.2 = **~22 W**, call it 30 W at the wall with
driver losses. Three motors is **~90 W typical, ~150 W peak in motion**, plus
a couple of watts for the servo.

A 24 V 15 A (360 W) supply is therefore running at about a quarter load, not
the 40% headroom `hardware_plan.md` claims (see correction 7). Keep the 360 W
anyway - the price delta over a 240 W is small, and a supply loafing at 25%
runs cool through a multi-hour session while one at 60% in a warm room is a
candidate to die mid-drawing. **Buy an enclosed case, not the open-frame type
with exposed mains terminals** - this runs in a room with an audience.

### Driver choice: TB6600 or DM542

Both are external opto-isolated bricks with PUL / DIR / ENA screw terminals
and DIP switches for current and microstepping. **The wiring in this document
is identical for both.** Same pin map off the shield, same ENA-unconnected
reasoning, same grounding. A swap changes nothing but the DIP table.

| | TB6600 | DM542 |
|---|---|---|
| Type | analog chopper | digital / DSP, anti-resonance |
| Supply | 9-42 V | 20-50 V (24 V is legal, bottom of range) |
| Cost each | ~$8-12 | ~$20-30 |
| Motion | more whine, mid-band resonance | smoother, quieter, cooler |

**The DM542 is the better driver and the delta is about $45 across three.**
It is worth naming why that matters: the original decision accepted TB6600
noise for a public run because the quiet alternative (TMC5160) needed
standalone-mode config judged too fiddly for a team new to robotics. **The
DM542 was not in that comparison.** It is quieter than a TB6600 *and* it is
configured by DIP switches exactly like one - no SPI, no UART, no firmware.
It recovers most of what was given up without the config problem that caused
the rejection.

Not overselling: a DM542 is not TMC-in-StealthChop silent. It is an audible
chopper, just smoother and less resonant.

**If you buy DM542, check two things.** (1) Many DM542 current tables list
**both RMS and peak columns** while the TB6600 table is peak only - read the
right column or you will run the motor ~1.4x over rating and cook it.
(2) Clone quality varies wildly; a real Leadshine and a $12 marketplace
"DM542" are different products. Neither is a reason not to buy one.

Microstepping stays at **16** either way, so `steps_per_mm: 80` and
`$100/$101` are unchanged.

### DIP switches

Set microstepping to **16** and current to the motor's rated phase current.
The switch tables are printed on the side of each unit and **clone units
disagree with each other** - use the label on the brick in your hand, not a
table from the internet. Set current one step *below* rated for the first
power-up; you can raise it if you see missed steps.

16 microsteps is what makes the config's `steps_per_mm: 80` correct:
200 steps/rev x 16 = 3200 steps/rev, over a 20T GT2 pulley = 40 mm/rev, so
3200 / 40 = 80. Change the microstepping and you must change `$100/$101`.

### The mirrored Y motor

The two Y motors are physically mirrored, so identical signals drive them in
opposite directions and the rail jams. Fix on **one** motor only: swap the
two wires of **one coil pair** (A+ with A-). Which pair is "A" depends on the
motor's wire colours - if swapping one pair does not fix it, put it back and
swap the other. Do this at the driver terminals, not by cutting the motor
lead.

Test before the belts are on: power up, jog Y a few mm, confirm both shafts
turn the direction that moves the rail the same way.

---

## 3. Limit switches

Two switches, both wired Normally-Open between the signal pin and GND:

```
  X-min switch -> D9  (X+/X- header) and GND
  Y-min switch -> D10 (Y+/Y- header) and GND
```

Home is the **top-left corner = origin (0,0)**, matching the software's
top-left origin and Y-increases-downward convention. So:

- X-min mounts at the **left** end of the horizontal rail; the pen carriage
  trips it.
- Y-min mounts at the **top** of one vertical rail; the X-rail trips it when
  fully raised.

Enable GRBL's internal pull-ups (`$5` invert setting) and confirm with `?`
that the switch states read correctly *before* you ever send `$H`. A homing
cycle into a switch that is not reading is how gantries get bent.

---

## 4. The servo - read this before you solder

The servo signal is whatever pin your firmware maps `SPINDLE_PWM` to. The
software already speaks the servo dialect: `M3 S90` = pen down, `M5` = pen
up, with the S value used as an angle. That is the **grbl-servo** convention,
not stock GRBL - stock GRBL treats S as a spindle speed and will not give you
a usable servo pulse.

So: **flash a servo-capable GRBL build**, not stock GRBL.

On an Uno running GRBL 1.1 with variable spindle enabled, the PWM output is
**D11**, and Z-limit gets swapped to D12 to make room. On a CNC Shield V3,
D11 is the **Z+/Z- limit header** - so the servo signal comes off the Z-limit
header pin, which looks wrong and is correct.

Wire:

```
  Servo signal (orange) -> D11  (Z limit header signal pin)
  Servo V+     (red)    -> Arduino 5 V
  Servo GND    (brown)  -> Arduino GND
```

**Verify the pin before soldering.** Flash the firmware, send `M3 S90` then
`M5`, and find which pin toggles - an LED and a resistor is enough. Different
grbl-servo forks make different pin choices and I am not going to pretend
they all agree. This is a two-minute check that saves an afternoon.

The SG90 draws enough on stall to brown out an Uno on USB power. If the board
resets when the pen lifts, give the servo its own 5 V supply with a common
ground.

---

## 5. Commissioning order

Do these in order. Each step is only meaningful if the one before it passed.

1. **Bench test, no belts, no rail.** Motors on the drivers, drivers on the
   PSU, Arduino on USB. Jog each axis. Confirm direction and that nothing
   gets hot enough to be uncomfortable to hold.
2. **Fix the mirrored Y motor** (section 2) with the motors still on the
   bench, coupled to nothing.
3. **Verify the servo pin** (section 4) before it is buried in the drag chain.
4. **Mount motors, fit belts, tension them.** Belt tension: a plucked belt
   should give a clear low note, not a flap. The 180 cm X-run needs the
   tensioner; it will sag without one.
5. **Limit switches: read state manually** with `?` before enabling homing.
6. **Enable homing** (`$22=1`), then `$H`. Stand at the E-stop / PSU switch.
7. **Square check.** Jog to draw a 150 mm test square, measure both diagonals
   with a tape. Equal diagonals means the frame is square. If not, fix the
   frame - no software setting corrects a rhombus.
8. **Calibrate steps/mm.** Measure the test square's sides. If a commanded
   150 mm comes out as 148, new value = 80 x (150/148). Set `$100` and `$101`.
9. **Then** raise acceleration. Start at `$120=200 / $121=100` and increase
   until you see missed steps, then back off 30%.

### GRBL starting config

```
$100=80     ; X steps/mm      (recalibrate in step 8)
$101=80     ; Y steps/mm
$110=5000   ; X max rate mm/min
$111=5000   ; Y max rate mm/min
$120=200    ; X accel mm/s^2  - start low
$121=100    ; Y accel mm/s^2  - lower, it is lifting the rail
$130=1700   ; X max travel    - matches work_area_width_mm
$131=1100   ; Y max travel    - matches work_area_height_mm
$22=1       ; homing enabled
$20=1       ; soft limits on, once $130/$131 are trusted
```

`$3` (direction invert) and `$23` (homing direction invert) are set
empirically during step 6-7. There is no point predicting them - they depend
on which way you physically mounted each motor. Jog, look, flip the bit.

---

## 6. Corrections to `hardware_plan.md`

These are real errors in the current doc, not nitpicks. Each one costs money
or time if followed as written.

1. **Phase 4 step 3 says "insert TMC2209 drivers into X, Y and A slots."**
   Stale - commit `5c5f9b9` moved the design to TB6600 but only updated
   `CLAUDE.md`. TB6600s are external bricks and do not fit the sockets.
   The block diagram has the same problem: it draws the TB6600s inside the
   shield.

2. **BOM says "GT2 Pulley, 20-tooth, 5 mm bore".** 5 mm is the NEMA **17**
   shaft. NEMA 23 shafts are 6.35 mm or 8 mm depending on the model. Ordering
   5 mm bore pulleys means three pulleys that will not fit. Confirm the shaft
   diameter on the exact motor listing and order the matching bore.
   (Idler bore stays 5 mm - those ride on M5 bolts, which is correct.)

3. **BOM says 5 idler pulleys, "2 for Y-axis top (counterweight side)".**
   Counterweights were dropped. You need **3**: one at the bottom of each
   vertical rail, one at the far end of the horizontal rail.

4. **Phase 4 step 9 says "connect 12 V PSU".** Everywhere else the doc
   correctly specifies 24 V, and the NEMA 23 torque argument depends on 24 V.
   12 V would work but lose a large fraction of torque at speed - which is
   exactly the margin being spent on skipping counterweights.

5. **BOM lists 1 compression spring.** Use **2**, one per guide rod. A single
   spring off the shuttle's centreline cocks it on the rods and it binds.

6. **"Wire servo -> SpnEn pin".** SpnEn is D12, the digital enable, not the
   PWM output. See section 4.

7. **"Each NEMA 23 at peak: ~3 A per phase x 24 V = 72 W", giving 216 W
   total.** Wrong arithmetic: 3 A is the *phase* current, not the current
   drawn off the 24 V rail. The driver is a switching regulator, so bus
   current is well below phase current. Real figure is ~90 W typical and
   ~150 W peak across three motors (working shown under "Motor power").
   The error is in the safe direction and the 360 W PSU choice is unchanged,
   but it matters if anyone later argues for a smaller supply from it.

### One thing that does check out

The counterweight-free claim is sound. A NEMA 23 at 1 Nm through a 20T GT2
pulley (pitch radius ~6.4 mm) produces roughly 157 N of belt force, about
16 kg per motor, 32 kg across the two Y motors, against an X-rail assembly of
3-5 kg. That is a large margin. The stated consequence is also real: **cut
the power and the rail drops.** Do not put anything, including a hand,
under it during commissioning.
