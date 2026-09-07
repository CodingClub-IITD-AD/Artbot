# ArtBot — Shopping List

Everything needed to build the machine, with what to search for and where.
Single-pen build (one black Sharpie, no pen changer).

**On the links:** these are *search* links, not deep product links. That is
deliberate — product URLs rot, and a dead link in a procurement doc wastes
someone's afternoon. Searches always resolve and always show today's price.
Where a specific supplier is named, their existence was checked; the individual
product pages were not, so confirm stock before promising anyone a date.

Prices are indicative. **USD ≈ AED × 0.27** (AED is pegged at 3.6725).

---

## 0. Read this before ordering anything

Three mistakes in here will cost real money:

1. **The GT2 pulley bore must match the motor shaft.** NEMA 23 shafts are
   **6.35 mm or 8 mm** depending on model. The old BOM said 5 mm — that is the
   NEMA **17** shaft. Order 5 mm bore and you get three pulleys that do not fit.
   *Read the motor listing, then order the matching bore.*

2. **The whiteboard must be MAGNETIC.** Most cheap boards are melamine on MDF
   and hold no magnet at all. The listing must say magnetic, and ideally
   porcelain or ceramic steel rather than melamine. If it is not magnetic you
   cannot hold paper on it and you have lost the keepable-output mode entirely.

3. **Order extrusion CUT TO LENGTH.** Every supplier does it and their ends are
   square. A hacksawn 1800 mm piece is not, and an out-of-square frame draws
   parallelograms that no software setting will fix.

Also: **you need 3 idlers, not 5**, and **2 springs, not 1**. Both errors are in
the old `hardware_plan.md`.

---

## 1. Structure — aluminium extrusion

All V-slot, 6 mm slot, anodised. **Order cut to length.**

| Cut | Profile | Qty | Purpose |
|---|---|---|---|
| 1200 mm | 2020 | 2 | Vertical uprights (the Y rails) |
| 1760 mm | 2020 | 2 | Top and bottom cross members |
| **1800 mm** | **2040** | **1** | **The moving X rail — 2040, not 2020** |
| 700 mm | 2020 | 2 | Riser legs |
| 1760 mm | 2020 | 1 | Base tie |
| 430 mm | 2020 | 2 | Front toes |
| 1150 mm | 2020 | 2 | Rear braces |

**Total ≈ 12.3 m of 2020 + 1.8 m of 2040. Order 14 m of 2020** to cover waste.

Cross members are 1760 because they sit *between* the uprights, giving an outer
envelope of exactly 1800.

The X rail is **2040 and not negotiable** — a 2020 over an 1800 mm span visibly
bows and every horizontal line gets a curve in it.

**Where:**
- **[Extrusion and CNC](https://extrusionandcnc.com/)** — Sharjah, delivers UAE-wide.
  140+ profile sizes. Homepage shows finished kits, so **phone them for raw
  extrusion**: +971 50 658 0398 / support@extrusionandcnc.com
- **[Dinco](https://dinco.ae/aluminium-extruded-sections/)** — warehouses in Abu Dhabi, Dubai, Sharjah. 25+ years.
- **[SupplyVan](https://supplyvan.com/extrusion-t-slot-profile-20-series-aluminium-1220mm.html)** — online, next-day. Stocks 20-series and 40-series.
- [Amazon.ae search](https://www.amazon.ae/s?k=v-slot+aluminium+extrusion+2020+2040)
- [AliExpress](https://www.aliexpress.com/w/wholesale-v-slot-2020-aluminium-extrusion.html) — cheapest, 2-5 week lead time. **Order first if you go this route.**

**Also:** aluminium flat bar **30 × 3 × 1800 mm**, 1 off — the rail stiffener.
Any hardware shop. Halves rail sag for about $8, **but only if you bolt it every
~150 mm** so it acts compositely. Bolted at the ends only it does nothing.

---

## 2. The board

**Magnetic whiteboard, 1800 × 1200 mm.** That is a stock size (metric 6ft × 4ft).

Requirements:
- **Magnetic** — steel or porcelain core, *not* melamine on MDF
- **Porcelain / ceramic steel** surface if you can afford it. Melamine ghosts and
  wears through; you will draw on this thousands of times
- **Aluminium framed** with rigid backing — flatness matters more for you than
  for a normal user, since a bowed board changes pen pressure across the sheet
- Skip glass boards: magnets barely hold and they are heavy

**Weight is a design input: 20-25 kg.** It is the heaviest thing on the machine
and it all hangs off the A-frame. Check the shipping weight before you buy.

**Where (all deliver Abu Dhabi):**
- [Quick Office](https://quickoffice.ae/) — carries Magnetoplan 180×120, free next-day
- [Altimus Office](https://www.altimus.ae/collections/magnetic-whiteboards)
- [Office One](https://www.officeoneuae.com/collections/magnetic-white-boards-planners)
- [Cognition UAE](https://cognitionuae.com/)
- [Office Flux](https://www.officeflux.com/office-supplies/whiteboards-flipchart/magnetic-whiteboard)
- [Penta Industries](https://penta-indust.com/ceramic-board/) — ceramic boards, custom sizes, will quote

**~AED 650-950 (~$180-260).** The single biggest line item.

---

## 3. Motion

| Item | Spec that matters | Qty |
|---|---|---|
| **NEMA 23 stepper** | 1.9 N·m holding, 3.0 A/phase, 1.8°, **56.4 mm frame, 76 mm long**, bolt circle 47.14 mm sq, boss Ø38.1, **shaft Ø8 mm**. Floor is 1.2 N·m | 3 |
| **GT2 pulley, 20T** | 2 mm pitch, 6 mm belt, **bore = your motor shaft** | 3 |
| **GT2 idler, 20T** | Toothed, bearings, 5 mm bore (rides on M5 bolts) | **3** |
| **GT2 belt** | 6 mm wide, 2 mm pitch, **fibreglass core**, open ended, 10 m | 1 roll |
| **Gantry plate** | OpenBuilds Mini-V style, 20 mm M5 hole grid | 3 |
| **V-wheel kit** | Delrin/POM + 2 bearings + precision spacer | 12 |
| **Eccentric spacers** | For wheel preload | 6 |
| **Belt tensioner** | Spring idler, adjustable | 3 |
| **Guide rod** | Ø8 mm ground steel, 60 mm (printer rod offcut) | 2 |
| **Compression spring** | ~0.2 N/mm, Ø10 OD, 20 mm free, clears an 8 mm rod | **2** |

**Why 20 teeth matters:** 20T × 2 mm = 40 mm of belt per revolution, which is
what makes `steps_per_mm: 80` correct at 16 microsteps. Change the tooth count
and `$100`/`$101` change with it.

**Belt lengths:** X run ≈ 3.8 m, each Y run ≈ 2.6 m. 10 m covers it.

**Where:**
- [Amazon.ae — NEMA 23](https://www.amazon.ae/s?k=nema+23+stepper+motor+1.9nm+3a) ·
  [GT2 pulley 20T](https://www.amazon.ae/s?k=gt2+pulley+20+teeth+8mm+bore) ·
  [GT2 belt 6mm](https://www.amazon.ae/s?k=gt2+timing+belt+6mm+open+ended+10m) ·
  [V-wheel](https://www.amazon.ae/s?k=openbuilds+v+wheel+kit+delrin)
- [AliExpress — NEMA 23](https://www.aliexpress.com/w/wholesale-nema-23-stepper-motor-1.9nm.html) ·
  [V-slot gantry plate](https://www.aliexpress.com/w/wholesale-v-slot-gantry-plate-mini-v.html)
- **StepperOnline** (omc-stepperonline.com) — the reference catalogue for stepper specs; spec against their datasheets even if you buy elsewhere. *Their site blocks automated checks, so I could not confirm it responds — open it in a browser.*
- **OpenBuilds** (openbuilds.com) — canonical for V-wheels, gantry plates and eccentric spacers; their part naming is what AliExpress clones copy, so use it to search. *Did not respond to an automated check — open it in a browser.*

---

## 4. Electronics

| Item | Spec | Qty |
|---|---|---|
| **Stepper driver** | TB6600 (4.0 A, 9-42 V) **or DM542** (4.2 A, 20-50 V, smoother, ~$15 more each) | 3 |
| **PSU** | **24 V**, 15 A, 360 W, enclosed, screw terminal | 1 |
| **Arduino Uno R3** | ATmega328P | 1 |
| **CNC Shield V3** | Signal breakout only | 1 |
| **SG90 servo** | 9 g, 5 V PWM | 1 + 2 spare |
| **Limit switch** | V-153 / KW12 lever microswitch, NO | 2 |
| **Drag chain** | 10 × 15 mm, 2 m | 1 |
| **Wire** | 22 AWG stranded, 4-core for motors | ~10 m |

**24 V, not 12 V.** The whole no-counterweight argument depends on torque at
speed, and that needs the higher voltage.

**The drivers do not plug into the CNC Shield.** TB6600 and DM542 are both
external bricks wired off the shield's socket header pins. Leave all four
sockets empty.

**TB6600 vs DM542 is an open call.** Wiring is identical, so this decides
nothing else and can be made at checkout. DM542 is a digital driver with
anti-resonance: smoother, quieter and cooler, about **$45 more across three**.
For a two-hour run with an audience standing next to the machine that is the
cheapest real improvement available. TB6600 works and nothing in the design
breaks. Full comparison and the two DM542 buying gotchas (RMS vs peak current
columns, clone quality) are in `docs/wiring_and_assembly.md` section 2.

**On motor torque:** 1.9 N·m is comfortable, **1.2 N·m is the real floor**, and
NEMA 23 is a frame size not a torque rating, so a 1.5 N·m unit is a fine
substitute and shares every bracket and pulley. Derivation in
`docs/wiring_and_assembly.md` section 1a.

**Where:**
- [Amazon.ae — TB6600](https://www.amazon.ae/s?k=tb6600+stepper+driver) · [DM542](https://www.amazon.ae/s?k=dm542+stepper+driver) ·
  [24V 15A PSU](https://www.amazon.ae/s?k=24v+15a+power+supply+360w) ·
  [Arduino Uno + CNC shield](https://www.amazon.ae/s?k=arduino+uno+cnc+shield+v3) ·
  [SG90](https://www.amazon.ae/s?k=sg90+micro+servo) ·
  [drag chain](https://www.amazon.ae/s?k=cable+drag+chain+10x15)
- **Worth a look:** [CNC kits bundling 3× NEMA 23 + TB6600 + 24 V PSU](https://www.amazon.ae/s?k=nema+23+tb6600+kit+cnc+3+axis)
  — often cheaper than buying separately, and you get matched parts. **Check the
  motor torque and shaft diameter before assuming it fits.**
- [Noon](https://www.noon.com/uae-en/search/?q=arduino%20cnc%20shield) for local stock

---

## 5. Pen, paper, consumables

| Item | Spec | Qty |
|---|---|---|
| **Sharpie Fine Point, black** | **~12 mm barrel** — the CAD default is 17 mm, change `pen_d` | pack of 12 |
| Neodymium disc magnets | **20-25 mm dia, 3-5 mm thick** — not office magnets | 8-12 |
| Paper | A0 (1189 × 841) or a roll cut to size | as needed |
| Dry-erase markers | For commissioning — wipe and retry, free iterations | few |
| PETG filament | **PETG, not PLA** — PLA creeps under a sustained spring load | ~300 g |

Ordinary ferrite office magnets creep downward under their own weight over a
two-hour run. Neodymium or nothing.

**Ink is your #1 failure mode over 2 hours.** Budget a feed-hold pen swap around
the 90 minute mark, and test one pen against a long plot beforehand so you know
exactly when it fades.

- [Sharpie](https://www.amazon.ae/s?k=sharpie+fine+point+black+pack) ·
  [neodymium discs](https://www.amazon.ae/s?k=neodymium+magnets+20mm+disc) ·
  [PETG](https://www.amazon.ae/s?k=petg+filament+1.75mm)

---

## 6. Fasteners

| Item | Qty |
|---|---|
| M5 T-nuts (drop-in, 6 mm slot) | **100** |
| M5 bolts, 8 / 10 / 20 mm mix | 100 |
| 90° corner brackets, 20-series | 12 |
| L-brackets for board retention | 8 |
| M3 bolts + nuts (carriage, servo) | 30 |

**Buy more T-nuts than you think you need.** Everyone runs out of T-nuts.

**Never drill the whiteboard.** It sits inside the extrusion rectangle, resting
on the bottom cross member, held by L-brackets that clamp the board's own
aluminium frame. Reversible, and you have not wrecked an AED 800 board.

- [Amazon.ae — M5 T-nuts](https://www.amazon.ae/s?k=m5+t+nut+2020+aluminium+extrusion) ·
  [corner brackets](https://www.amazon.ae/s?k=2020+aluminium+extrusion+corner+bracket)

---

## 7. Order in this sequence

So you can build while later shipments are still in transit:

1. **Extrusion + board** — longest lead time, and everything bolts to them.
   If buying from AliExpress, order *today*; 2-5 weeks will eat your semester.
2. **Motion** — wheels, plates, eccentrics, belt, pulleys, idlers, tensioners
3. **Motors** — 3 × NEMA 23 + mounting brackets. **Record the shaft diameter
   the moment they arrive and order pulleys to match** (or order pulleys with
   them once you know the model)
4. **Electronics** — drivers, PSU, Arduino, shield, switches, drag chain
5. **Pen and consumables** — last, cheap, available anywhere

### Budget

| | USD | AED |
|---|---|---|
| Whiteboard | $180-260 | 660-955 |
| Everything else | $340-570 | 1250-2090 |
| **Total** | **$520-830** | **1900-3050** |

---

## 8. What was and wasn't verified

**Checked:** all supplier sites in sections 1 and 2 exist and serve
Abu Dhabi. Search URLs are constructed, so they always resolve.

**Not checked:** individual product pages, live stock, and today's prices.
Two candidate links were checked and one 404'd, which is exactly why this
document uses searches instead of deep links.

**Also not verified:** whether the specific board carried by any of the office
suppliers is porcelain or melamine. **Ask them directly — it is the single
spec that determines whether the paper mode works at all.**

---

## Related

- `docs/wiring_and_assembly.md` — pin-level wiring, corrected for TB6600
- `cad/artbot_cad.py` → `cad/out/artbot_assembly.step` — full CAD assembly
- `viz/mockup-v2.html` — interactive 3D model with clickable parts
