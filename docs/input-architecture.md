# Input architecture — PSP controls in 4 personalities

Updated: 2026-10-15.  Status: architecture + protocol fixed;
electrical tap details blocked on U14 (button FPC measurement).

## 1. Problem

The stock button FPC feeds the PSP motherboard.  Four personalities
must all see the controls, without duplicating hardware:

1. ARK/native — PSP MB must receive the raw signals (unchanged).
2. Linux / FullereneOS / PocketJS — OPi must receive them, but the
   PSP MB may be powered OFF (system-architecture §5), so the FPC
   must be read by something independent of the PSP MB.

## 2. Architecture (decided)

```
button FPC ──> interposer PCB ── straight-through ──> PSP MB FPC
                    │
                    └ high-Z sense taps (one per net)
                          └ CH32V203 supervisor MCU
                                ├ passive matrix observation
                                ├ mode FSM + boot strap (sysarch §5)
                                └ UART 115200 8N1 ──> OPi UART0 (40pin 8/10)
```

- Straight-through contact paths: pressed-button latency in ARK mode
  stays exactly stock (0 added).
- Sense taps are series 100 kΩ + ESD diode into the MCU — the MCU
  never drives the PSP MB nets (high-Z always).  When the PSP MB is
  off, its side of the matrix is unpowered; the MCU's taps still see
  column pull states through the interposer, but the **matrix scan
  comes from the PSP MB** — without it there is no scan to observe.
  Therefore the MCU **runs its own scan** when PSP MB power is off:
  it drives one row at a time (through the interposer's isolated
  drive FETs, only enabled in OPi-only modes) and reads columns.
  In ARK mode drive FETs are tri-stated and it observes only.
- Analog stick: two pots from a railed reference; MCU samples via its
  ADC (3.3 V rail independent of PSP MB state) and passes the raw
  values through; in OPi-only modes the MCU supplies the stick
  reference from its own 3.3 V rail (relay-or via the interposer).
  U14 measurement must confirm the stick's reference rail location.

## 3. UART protocol (v1, frozen for rev-1 hardware)

Fixed 12-byte frame, 10 ms period, no handshake (loss-tolerant):

| byte | content |
|---|---|
| 0 | 0xA5 sync |
| 1 | seq (wraps) |
| 2 | buttons A: bit0 SELECT bit1 L bit2 R bit3 START bit4 UP bit5 RIGHT bit6 DOWN bit7 LEFT |
| 3 | buttons B: bit0 TRIANGLE bit1 CIRCLE bit2 CROSS bit3 SQUARE bit4 HOME bit5 HOLD bit6 WLAN-up bit7 VOL+ |
| 4 | buttons C: bit0 VOL- bit1..7 reserved 0 |
| 5 | right trigger (reserved, 0) |
| 6-7 | stick X (uint16 LE, 0=left, 2048=mid, 4095=right) |
| 8-9 | stick Y (uint16 LE, 0=up, 4095=down) |
| 10 | mode latch echo (0-3) |
| 11 | 0x5A^seq^b2^b3^b4^b5^b6..b9 XOR checksum |

Linux side: 200-line userspace reader (uinput).  PocketJS/Fullerene:
same frames off the UART device.  ARK side: not used (pass-through).

## 4. MCU choice (decided, with reasoning)

**CH32V203 (QFN-28 4×4 mm)** — JLCPCB Basic-adjacent, ~$0.40-0.60,
RISC-V, 2× USART, 12-bit ADC, 62 kB flash (mode latch + scan code
fits trivially), 20 kB SRAM.  RP2040 rejected: 2× price, 2× size, and
nothing in this role needs USB or PIO.  CH32V003 would fit the scan
loop but lacks the flash headroom for the FSM + flash-latch + UART
 bootloader updates; V203 is the floor with margin.

## 5. Open items

- U14: FPC pin count, matrix row/col map, pull locations, stick
  reference rail.  Blocks the interposer schematic, nothing else.
- ESD plan: FPC carries human-touchable buttons — interposer needs
  TVS on row/col taps (PESD5V0-class, 0402).
- Hold switch + WLAN slider are mechanical-only in stock; decide in
  schematic phase whether they route through the MCU (they should —
  bits already in the frame).
