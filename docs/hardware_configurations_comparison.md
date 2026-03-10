# ArtBot: Hardware Configuration Analysis

Every design choice — motion architecture, motor, drive system, pen mechanism, controller — has trade-offs. This document evaluates all viable options for a **180x120cm vertical whiteboard plotter** and explains why each was accepted or rejected.

---

## 1. Motion Architecture (The Big Decision)

This is the single most important choice. It determines everything else.

### Option A: Polargraph / V-Plotter (Cable-Hung Gondola)

```
  Motor ●─────────────────────────────● Motor
        \                             /
         \    cable/belt             /
          \                         /
           \     ┌─────┐          /
            \    │ Pen  │        /
             \   │Gondola│      /
              \  └─────┘     /
               \            /
                ~~~~~~~~~~~~
```

**How it works**: Two motors at the top corners hold a "gondola" (pen holder) via cables, chains, or timing belts. Gravity pulls the gondola down; motor tension positions it. The pen is always at the intersection of two cable arcs.

**Real-world examples**:
- [Makelangelo](https://github.com/MarginallyClever/Makelangelo-software) — the most popular open-source polargraph, uses Marlin firmware on Arduino Mega
- [Maslow CNC](https://www.maslowcnc.com/) — wall-mounted CNC router using the same principle but with a router instead of a pen (Maslow4 uses 4 belts instead of 2 chains)
- [Penelope by David Bliss](https://davidbliss.com/2021/09/13/penelope/) — clean DIY polargraph build
- [Stringent ($15 Wall Plotter)](https://www.hackster.io/fredrikstridsman/stringent-the-15-wall-plotter-d965ca)
- Countless Instructables builds ([example](https://www.instructables.com/Vertical-Plotter/), [example](https://www.instructables.com/SIMPLEST-Arduino-Vertical-Plotter/))

**Pros**:
- Cheapest option ($15–$100 in parts)
- Simplest to build (2 motors, some string/belt, done)
- Scales to ANY size trivially (just use longer cables)
- Minimal frame needed (just two mounting points)
- Huge community and software support

**Cons**:
- **Accuracy collapses at bottom corners**: The math is non-linear. When the gondola is near the bottom, both cables are nearly vertical — small motor movements create large position errors. The Jacobian of the coordinate transform shows resolution drops dramatically below the motor line. Most polargraph builders recommend a **15% margin on all sides** — on your 180x120cm board that eats ~27cm per side, leaving only ~126x90cm usable.
- **No precision for multi-color**: If you ever want pen switching (draw outline, switch pen, fill color), the gondola can't return to the exact same position reliably. Cable stretch, wind, and oscillation make registration impossible.
- **Gondola swings**: Fast direction changes cause the pen to pendulum on the cables. You must draw SLOW. Penelope's builder reported issues "especially when drawing near the bottom of the page and when drawing curves."
- **Cable stretch is cumulative**: Over a long drawing (30+ minutes), the cables warm up and stretch microscopically. Your drawing drifts.
- **Z-axis is awkward**: Lifting a pen on a swinging gondola is mechanically messy.

**VERDICT: REJECTED**
- Not because it's bad — polargraphs are excellent for artistic/sketchy work
- Rejected because we need precision for future multi-color, and the accuracy loss at corners wastes ~30% of our drawing area
- If budget were the only constraint, this would be the choice

---

### Option B: CoreXY / H-Bot

```
  Motor ●━━━━━belt━━━━━━━━━━━━━━━━━━━● Idler
        ┃                              ┃
  belt  ┃    ┌──────────────────┐      ┃ belt
        ┃    │   Pen Carriage   │      ┃
        ┃    └──────────────────┘      ┃
        ┃                              ┃
  Idler ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● Motor
```

**How it works**: Two stationary motors work in tandem through a continuous belt loop. Moving both motors the same direction = X movement. Moving them opposite directions = Y movement. The pen carriage rides at the intersection of two belt paths.

**Real-world examples**:
- [Stefan van Seggelen's Large CoreXY Plotter](https://www.stefanvanseggelen.com/plotter.html) — one of the few large-format CoreXY builds, uses Klipper firmware
- [MidTbot](https://github.com/bdring/midTbot_esp32) — small CoreXY pen plotter
- [PlotteRXY](https://github.com/jamescarruthers/PlotteRXY)
- Most modern 3D printers (Voron, Bambu Lab) use CoreXY but at 30x30cm, not 180cm

**Pros**:
- Both motors are stationary (no moving motor weight)
- Very fast — motors don't move, so inertia is low
- Excellent for small-to-medium machines (<60cm)

**Cons**:
- **Belt length is the killer**: For a 180x120cm machine, each belt loop is approximately 2×(180+120) = 600cm. CoreXY uses TWO belts, so total belt path is ~12 meters. Standard 6mm GT2 belt stretches measurably over 6+ meters, causing positional drift.
- **Calibration nightmare**: At this scale, getting both belt paths tensioned identically is nearly impossible. Uneven tension = the pen drifts diagonally ("racking").
- **Stefan van Seggelen's build** (the only documented large CoreXY plotter) used 15mm steel-core GT2 belts to combat stretch — these are expensive and hard to source.
- **Complex belt routing**: The belt crosses over itself in CoreXY. At 180cm, routing this cleanly without the belt rubbing on itself is a real challenge.
- **H-Bot variant is worse**: H-Bot uses a single belt (simpler) but introduces a rotational torque on the carriage during diagonal moves, causing skew.

**VERDICT: REJECTED**
- CoreXY is the best architecture for machines under ~60cm
- At 180cm, belt stretch and tensioning make it impractical for a first-time build
- The one person who built a large CoreXY plotter needed steel-core belts and Klipper firmware — beyond our team's experience level

---

### Option C: Standard Cartesian (Single Y Motor)

```
  ┌─────────────────────────────────────────┐
  │                                         │
  │  Motor [Y] ─── Belt ─── [X-Rail]        │
  │              (one side)                  │
  │                                         │
  └─────────────────────────────────────────┘
```

**How it works**: One motor drives the vertical movement (Y), one drives horizontal (X). Standard 3D printer layout (Ender 3, Prusa, etc.).

**Pros**:
- Simplest control logic (one motor per axis, no cloning needed)
- Cheapest motor setup (only 2 NEMA 17s)
- Tons of documentation from 3D printer community

**Cons**:
- **Racking**: With only one Y motor driving a 180cm rail from one side, the far end of the rail lags behind. Imagine pushing a long plank from one end — it pivots. This causes the pen to draw rhombuses instead of rectangles.
- **Torque requirements**: One motor must lift the entire ~3-5kg X-rail assembly against gravity. Even with counterweights, the single-point drive creates uneven forces.
- **Not used in any large-format machine**: Every large CNC (even desktop-sized ones like the X-Carve) uses dual Y motors for exactly this reason.

**VERDICT: REJECTED**
- Fine for machines under 50cm
- At 180cm, single-side drive causes unacceptable racking
- No one builds large-format machines this way

---

### Option D: Dual-Y Cartesian (Our Choice)

```
  Motor ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━● Motor
  Y-Left│           X-Rail (180cm)              │Y-Right
        │      ┌────────────────────┐           │
        │      │  [Motor X] [Pen]  │ ◄── rides  │
        │      └────────────────────┘   on rail  │
        │                                        │
        ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
      Idler                                    Idler
```

**How it works**: Two synchronized motors (one on each side) move the horizontal X-rail up and down. A third motor drives the pen carriage left and right along that rail. NEMA 23 motors provide enough torque to drive the rail directly against gravity without counterweights.

**Real-world examples**:
- [OpenBuilds ACRO System](https://builds.openbuilds.com/tags/acro/) — community builds using this exact pattern
- [iDraw H A0/A1](https://uunatek.com/collections/large-format-size-drawing-robots) — commercial large-format plotter, uses rack-and-pinion variant of this layout, ±0.02mm precision
- [Hackaday 3D-Printed Pen Plotter](https://hackaday.com/2019/08/26/3d-printed-pen-plotter-is-as-big-as-you-need-it-to-be/) — "as big as you need it to be"
- [OpenBuilds Pen Plotter](https://builds.openbuilds.com/builds/pen-plotter.10615/) — Arduino Uno R4 + CNC Shield, Bluetooth control
- Every large CNC router (Shapeoko, X-Carve, WorkBee) uses dual-Y

**Pros**:
- **Anti-racking**: Both sides of the rail move simultaneously → rail stays perfectly level
- **Proven at scale**: This is how every serious large-format CNC machine works
- **Simple control**: Arduino + CNC Shield's A-axis jumper clones Y to both motors. Standard GRBL handles it natively with `#define ENABLE_DUAL_AXIS`.
- **No counterweights needed**: NEMA 23 motors have enough torque to drive the rail directly against gravity
- **Pen switching ready**: Rigid rail means the pen can return to exact coordinates → multi-color possible in the future
- **Short belt runs**: Each belt is only ~260cm (up one side, down the other). Much less stretch than CoreXY's 12m.
- **Repairable**: If one motor/belt/driver fails, you replace that one component. No complex system interdependencies.

**Cons**:
- More expensive than polargraph (3 motors vs 2, more rail)
- Dual Y motors must be wired correctly (one coil reversed) or they'll fight each other
- Heavier frame than polargraph
- X-rail will drop on power loss (no counterweight safety net)

**VERDICT: ACCEPTED**
- Best balance of precision, scalability, simplicity, and future-proofing
- iDraw H proves this architecture works commercially at A0+ sizes
- GRBL + CNC Shield natively support dual-Y with minimal config

---

### Option E: Rack and Pinion (Commercial Alternative)

**How it works**: Instead of belts, a toothed gear ("pinion") meshes with a toothed rail ("rack") bolted along the extrusion.

**Real-world example**: iDraw H A0 uses this for ±0.02mm precision.

**Why we're not using it**:
- Rack and pinion hardware for 180cm is significantly more expensive
- Requires precision-machined racks
- Less community documentation for DIY builds
- GT2 belt at our scale gives us 80 steps/mm (0.0125mm resolution) — more than enough when the pen tip is 0.5–1.0mm wide

**VERDICT: REJECTED (not worth the cost for our accuracy needs)**

---

## 2. Drive Transmission (Belts vs Screws vs Cable)

### GT2 Timing Belt (Our Choice)

| Property | Value |
|----------|-------|
| Pitch | 2mm |
| Typical width | 6mm (ours) or 10mm |
| Stretch | ~0.2% under normal load |
| Speed | Fast (3000–5000 mm/min easy) |
| Noise | Moderate |
| Self-locking on power loss | NO — rail will drop when motors are unpowered |
| Cost | ~$5–10 for 10m roll |

**Why chosen**: Fast, cheap, widely available, well-documented. The stretch is manageable at our belt lengths (~260cm per Y-axis run). Every 3D printer uses GT2.

### Lead Screw (ACME or Trapezoidal)

| Property | Value |
|----------|-------|
| Pitch | 2mm or 8mm (T8 common) |
| Stretch | Essentially zero |
| Speed | Slow (500–1500 mm/min typical) |
| Noise | Moderate to loud |
| Self-locking on power loss | YES — gravity cannot back-drive a lead screw |
| Cost | ~$20–30 per 120cm rod |

**Why rejected**:
- **Speed**: At 500mm/min on a 1.8m machine, moving corner to corner takes ~3.6 minutes. A complex drawing would take hours.
- **Weight**: Two 120cm steel lead screws add significant mass
- **Whip**: Long lead screws (>60cm) can vibrate/whip at higher RPM. You'd need a supported screw, which is expensive.
- The self-locking advantage is nice but lead screw speed is too slow for our machine size.

### Ball Screw

| Property | Value |
|----------|-------|
| Accuracy | Excellent (0.01mm) |
| Speed | Fast (similar to belt) |
| Self-locking | NO (too efficient, will back-drive) |
| Cost | $100–300 per 120cm screw |

**Why rejected**: Extremely expensive at 120cm+ lengths. Overkill for a pen plotter. Does not self-lock (same gravity problem as belts, but costs 10x more).

### Cable / Fishing Line / Chain

Used by polargraphs and Maslow CNC. Already covered in the polargraph section.

**Why rejected**: Stretch, elasticity, and the inability to push (cables can only pull). Not suitable for rigid Cartesian motion.

### Beaded Chain (Makelangelo-style)

**Why rejected**: Better than fishing line (doesn't stretch) but the chain links introduce micro-backlash. Chains also jump teeth under high acceleration. Good for polargraphs, wrong for Cartesian.

**VERDICT**: GT2 timing belt wins on speed, cost, and community support. NEMA 23 holding torque keeps the rail in position during operation; rail drop on power loss is acceptable for a pen plotter.

---

## 3. Motor Selection

### NEMA 17

| Property | Value |
|----------|-------|
| Frame size | 42mm × 42mm |
| Holding torque | 40–65 Ncm (typical high-torque models) |
| Weight | ~280g |
| Current | 1.2–2.0A per phase |
| Voltage | 12V typical |
| Step angle | 1.8° (200 steps/rev) |
| Cost | ~$8–15 each |

**Why rejected**:
- Insufficient torque to drive the Y-axis against gravity without counterweights
- Would require a counterweight system (pulleys, cables, weight calibration) adding complexity
- Compatible with cheaper drivers (TMC2209) but the counterweight trade-off isn't worth it

### NEMA 23 (Our Choice)

| Property | Value |
|----------|-------|
| Frame size | 57mm × 57mm |
| Holding torque | 100–300 Ncm |
| Weight | ~600-1000g |
| Current | 2.0–4.0A per phase |
| Voltage | 24V typical |
| Step angle | 1.8° (200 steps/rev) |
| Cost | ~$20–40 each |

**Why chosen**:
- **Eliminates counterweights**: Enough torque to drive the Y-axis directly against gravity, vastly simplifying the mechanical build
- **Simpler assembly**: No pulleys, cables, or weight calibration needed
- **Reliable holding**: Holding torque keeps X-rail in position during drawing
- Requires TB6600 drivers (TMC2209 insufficient) and 24V PSU, but the mechanical simplification is worth the electronics cost
- The added weight of NEMA 23 on the X-rail (~600g for X motor) is acceptable given the Y motors' torque

### NEMA 14

| Property | Value |
|----------|-------|
| Frame size | 35mm × 35mm |
| Holding torque | 10–20 Ncm |

**Why rejected**: Too weak. Even with counterweights, accelerating a 180cm rail from rest requires more torque than NEMA 14 provides. Belt friction alone might stall these.

### Servo Motors (Closed-Loop)

**Why rejected**: Expensive ($50+ each), require dedicated controllers, overkill for this application. Open-loop steppers are fine when belt tension is correct and acceleration is tuned conservatively. Closed-loop steppers (like NEMA 17 with encoder) are a possible future upgrade if we see missed steps.

**VERDICT**: NEMA 23. The extra torque eliminates counterweights entirely, making the build much simpler.

---

## 4. Stepper Drivers

### TMC2209

| Property | Value |
|----------|-------|
| Max current | 2.8A RMS |
| Microstepping | Up to 1/256 (we use 1/16) |
| Noise | Near-silent (StealthChop mode) |
| Stall detection | Yes (sensorless homing possible) |
| Interface | Step/Dir (drop-in for CNC Shield) |
| Cost | ~$3–5 each |

**Why rejected**: Max current of ~2A RMS is insufficient for most NEMA 23 motors which need 2.5-4A per phase. Would work with NEMA 17 but we chose NEMA 23 to eliminate counterweights.

### TB6600 (Our Choice)

| Property | Value |
|----------|-------|
| Max current | 4.0A per phase |
| Microstepping | Up to 1/32 |
| Noise | Moderate |
| Interface | Step/Dir (external driver, wired to CNC Shield) |
| Cost | ~$8–12 each |

**Why chosen**: Supports the higher current draw of NEMA 23 motors. External form factor (not StepStick) but still controlled via Step/Dir signals from the CNC Shield. Widely used in CNC router builds with NEMA 23.

### A4988

| Property | Value |
|----------|-------|
| Max current | 2A (1A without heatsink) |
| Microstepping | Up to 1/16 |
| Noise | LOUD |
| Cost | ~$1–2 each |

**Why rejected**: Extremely noisy. Audible whining/screeching during motor movement. The noise difference between A4988 and TMC2209 is dramatic — like comparing a dial-up modem to silence. For a machine that might run for 30+ minutes on a drawing, noise matters.

### DRV8825

| Property | Value |
|----------|-------|
| Max current | 2.2A (1.5A without heatsink) |
| Microstepping | Up to 1/32 |
| Noise | Loud (slightly better than A4988) |
| Cost | ~$2–3 each |

**Why rejected**: Still noisy. The 1/32 microstepping sounds appealing but provides negligible real-world benefit over 1/16 for a pen plotter (the pen tip is 500x larger than the step resolution at 1/16). TMC2209's StealthChop is worth the extra $1–2 per driver.

**VERDICT**: TB6600. Required for NEMA 23 current draw. Less silent than TMC2209 but necessary trade-off for eliminating counterweights.

---

## 5. Pen Lift (Z-Axis) Mechanism

### SG90 Micro Servo (Our Choice)

| Property | Value |
|----------|-------|
| Weight | ~9g |
| Torque | 1.8 kg-cm |
| Speed | 0.1s per 60° |
| Power | 5V (from Arduino/CNC Shield) |
| Cost | ~$1–2 |
| Control | PWM signal |

**Why chosen**: Lightest option, simplest to control, cheapest. The pen up/down action only needs two positions (binary). A servo does this perfectly. The SG90's 1.8kg-cm torque is more than enough to retract a pen against a light spring.

**How it works on a vertical board**: Since gravity pulls the pen AWAY from the board (not toward it), we use a compression spring that pushes the pen toward the board. The servo arm retracts the pen when we want "pen up." When the servo releases, the spring pushes the pen into the board.

### Solenoid

| Property | Value |
|----------|-------|
| Weight | 30–80g |
| Speed | 5–10ms (very fast) |
| Power | 12V, high current draw |
| Cost | ~$5–10 |

**Why rejected**:
- **Thumps the board**: A solenoid snaps on/off — it's binary but violent. The impact vibrates the pen and leaves dots at every pen-down event
- **Power hungry**: Draws significant current while engaged (continuously, not just on transition)
- **Heavier**: 3–8x heavier than an SG90, and this weight rides on the moving carriage

### Stepper Motor (Z-axis)

| Property | Value |
|----------|-------|
| Weight | 200g+ |
| Precision | Excellent (continuous pressure control) |
| Cost | ~$10+ plus another driver |

**Why rejected**:
- **Way too heavy**: Adding 200g to the pen carriage increases inertia, causes the X-rail to sag at the carriage position, and requires stronger Y motors
- **Needs another driver**: CNC Shield only has 4 driver slots (X, Y, A-clone, and Z). Using Z for a stepper pen means losing the ability to use Z for anything else
- **Overkill**: We don't need variable pressure control — we need binary pen up/down

**VERDICT**: SG90 servo. 9 grams, $1, two positions, job done.

---

## 6. Controller

### Arduino Uno + CNC Shield V3 + GRBL (Our Choice)

**Why chosen**:
- GRBL is the de facto standard for 3-axis CNC control
- Real-time motor pulse generation with microsecond precision
- Look-ahead path planning (smooths curves at firmware level)
- Native dual-Y axis support (`ENABLE_DUAL_AXIS` compile flag)
- CNC Shield V3 has a built-in A-axis clone jumper
- Massive community, every problem has been solved before

### Arduino Mega + Marlin

**Why not**: Marlin is designed for 3D printers (temperature control, extruder management). It can run polargraph kinematics (Makelangelo uses it) but is overkill for a pen plotter. GRBL is leaner and faster for pure motion control.

### ESP32 + FluidNC

**Why not yet**: FluidNC is the modern successor to GRBL — runs on ESP32, has WiFi, supports more axes, and has modular kinematic configs. It's technically superior but newer, with a smaller community. We could upgrade to this later. [Jason Webb's grbl-mega-wall-plotter](https://github.com/jasonwebb/grbl-mega-wall-plotter) was archived in 2024 with a note recommending FluidNC for future builds.

### Raspberry Pi (alone)

**Why rejected**: Not a real-time system. Linux has no guarantee on timing precision — motor pulses would jitter, causing wavy lines. The Pi is great as a **sender** (streams G-Code to the Arduino) but cannot replace it as a **controller**.

**VERDICT**: Arduino Uno + GRBL for v1. Optional upgrade path to ESP32 + FluidNC later.

---

## 7. Rail Profiles (Frame)

### V-Slot 2040 for X-Rail (Our Choice)

The horizontal rail spans 180cm and carries the pen carriage + X motor + servo. It's the most structurally critical component.

| Profile | Cross Section | Moment of Inertia (Iy) | Weight/m | Deflection at 180cm, 1kg center load |
|---------|--------------|----------------------|----------|-------------------------------------|
| 2020 | 20×20mm | ~0.7 cm⁴ | ~0.5 kg | ~4mm (UNACCEPTABLE) |
| 2040 | 20×40mm | ~3.3 cm⁴ | ~0.9 kg | ~0.9mm (acceptable) |
| 4040 | 40×40mm | ~7.0 cm⁴ | ~1.6 kg | ~0.4mm (excellent) |

**2020 rejected**: At 180cm span with even a 500g carriage at center, a 2020 will visibly bow. Your drawing will have a subtle curve in the middle of every horizontal line.

**4040 is better but**: Heavier (adds ~1.2kg to the rail assembly = heavier counterweight needed), more expensive, and harder to source in exact lengths.

**2040 chosen**: 4x stiffer than 2020, half the weight of 4040. Add a flat aluminum backing strip (3mm × 30mm × 180cm) bolted to the back for extra rigidity. Total cost: ~$5 extra.

### V-Slot 2020 for Y-Rails and Frame

The vertical rails (120cm) carry much less load (just the wheels rolling on them) and don't span freely — they're bolted to the frame at both ends. 2020 is sufficient.

**VERDICT**: 2040 for X-rail (with stiffener), 2020 for everything else.

---

## Summary: Final Configuration

| Component | Choice | Why |
|-----------|--------|-----|
| **Architecture** | Dual-Y Cartesian | Anti-racking, precision, pen-switch ready |
| **Drive (X & Y)** | GT2 Timing Belt + 20T Pulley | Fast, cheap, adequate accuracy at our belt lengths |
| **Y-Axis** | Dual motors, no counterweights | NEMA 23 torque handles gravity directly |
| **Motors** | 3× NEMA 23 (>100Ncm) | Enough torque to skip counterweights |
| **Drivers** | 3× TB6600 | Supports NEMA 23 current (up to 4A) |
| **Pen Lift** | SG90 Servo + Spring | 9g, $1, binary pen up/down |
| **Controller** | Arduino Uno + CNC Shield V3 + GRBL | Real-time, proven, native dual-Y support |
| **X-Rail** | 2040 V-Slot + stiffener | Best rigidity-to-weight ratio at 180cm |
| **Y-Rails / Frame** | 2020 V-Slot | Sufficient for supported spans |
| **PSU** | 24V 15A (Mean Well or equiv) | Headroom for 3 NEMA 23 motors + servo |
| **Homing** | 3× Microswitch (NO) | Reliable, cheap, GRBL-native |

---

## Sources

- [Makelangelo Software (GitHub)](https://github.com/MarginallyClever/Makelangelo-software)
- [Makelangelo vs Polargraph](https://www.marginallyclever.com/2015/08/makelangelo-vs-polargraph/)
- [How to Fix 9 Common Polargraph Drawing Problems](https://www.marginallyclever.com/2014/10/how-to-fix-9-common-polargraph-drawing-problems/)
- [Polargraph Mathematics (nexp.pt)](https://www.nexp.pt/vbot.html)
- [Penelope: A Vertical Pen Plotter (David Bliss)](https://davidbliss.com/2021/09/13/penelope/)
- [Stefan van Seggelen Large CoreXY Plotter](https://www.stefanvanseggelen.com/plotter.html)
- [CoreXY Belt Tensioning (Dr. Rehorst)](https://drmrehorst.blogspot.com/2018/08/corexy-mechanism-layout-and-belt.html)
- [Maslow CNC (Wikipedia)](https://en.wikipedia.org/wiki/Maslow_CNC)
- [Maslow CNC Review (Jay's Technical Talk)](https://www.summet.com/blog/2018/06/12/maslow-cnc-hanging-router-review/)
- [Jason Webb's GRBL Mega Wall Plotter (GitHub, archived)](https://github.com/jasonwebb/grbl-mega-wall-plotter)
- [iDraw H A0 Large Format Plotter](https://uunatek.com/products/uuna-tek%C2%AE-idraw-h-a0-size-drawing-robot-drawing-machine-homework-machine-calligraphy-plotter-handwriting-robot-pen-plotter-laser-engraver)
- [OpenBuilds Pen Plotter](https://builds.openbuilds.com/builds/pen-plotter.10615/)
- [3D-Printed Pen Plotter (Hackaday)](https://hackaday.com/2019/08/26/3d-printed-pen-plotter-is-as-big-as-you-need-it-to-be/)
- [GRBL Dual Axis Issues (GitHub)](https://github.com/gnea/grbl/issues/797)
- [GRBL with Arduino CNC Shield Guide](https://www.diyengineers.com/2023/01/05/grbl-with-arduino-cnc-shield-complete-guide/)
- [How to Setup GRBL (HowToMechatronics)](https://howtomechatronics.com/tutorials/how-to-setup-grbl-control-cnc-machine-with-arduino/)
- [Belts vs Leadscrews in CNC Design](http://blanch.org/belts-vs-screws-in-cnc-design/)
- [Lead Screw vs Belt Drive (PBC Linear)](https://pbclinear.com/blog/2020/february/lead-screw-or-belt-drives)
- [NEMA 17 vs NEMA 23 (SSS Motors)](https://sss-motors.com/nema-17-vs-nema-23-stepper-motor/)
- [TMC2208 vs TMC2209 (Xecor)](https://www.xecor.com/blog/tmc2208-vs-tmc2209)
- [DRV8825 vs A4988 (Xecor)](https://www.xecor.com/blog/drv8825-vs-a4988)
- [Stepper Driver Comparison (MakerShop)](https://makershop.co/stepper-driver-comparison-3d-printer-upgrade/)
- [CNC Pen Lift (Instructables)](https://www.instructables.com/CNC-Pen-Lift-1/)
- [V-Slot Deflection Calculator (OpenBuilds)](https://builds.openbuilds.com/threads/how-to-calculate-v-slot%C2%AE-deflection.4881/)
- [T-Slot Deflection Calculator (Vention)](https://vention.io/tools/calculators/deflection)
- [How to Build a Wall Hanging Drawing Robot (Liz Melchor)](https://lizmelchor.com/wall-robot/?v=7d0db380a5b9)
- [Building a Polargraph Pen Plotter (stefan.wtf)](https://stefan.wtf/p/penplotter)
- [Open-Source Vertical Plotter (Open Electronics)](https://www.open-electronics.org/how-to-make-an-opensource-vertical-plotter/)
- [Stringent $15 Wall Plotter (Hackster)](https://www.hackster.io/fredrikstridsman/stringent-the-15-wall-plotter-d965ca)
- [Pen Plotters Overview (Matt Widmann)](https://mattwidmann.net/notes/pen-plotters/)
- [FluidNC Kinematics (Wiki)](http://wiki.fluidnc.com/en/config/kinematics)
