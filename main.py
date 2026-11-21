"""The World in One Day -- Saturday 21 November 2026.

A program that draws one newspaper front page summing up the world's
news of Saturday 21 November 2026 and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Python standard library only: no Pillow, no network, no randomness.
Every run writes the exact same bytes (1024x1024 PNG).

Stories (all reported on 21 November 2026):
  Lead. Russian missiles and drones strike Kyiv in the war's biggest
     aerial assault in weeks: three bridges hit, at least nine dead,
     Austrian and Dutch embassy buildings damaged.
  1. COP31 climate talks in Antalya run into overtime; the draft deal
     drops every mention of fossil fuels and Panama threatens to block it.
  2. Cyclone Akvan crosses the Odisha coast near Gopalpur; about
     300,000 people moved to safety.
  3. JPMorgan, Visa and Mastercard report cyberattacks on third-party
     vendors; core payment networks unaffected.
  4. Mongolia's parliament approves President Khurelsukh Ukhnaa's
     resignation; an early election within four months.
  5. The EU completes a disbursement of nearly 8 billion euros to
     Ukraine, its largest-ever single payment.
  6. Sport: Nicholls 175 not out and Phillips 118 lift New Zealand
     to 368; Jaiswal 85 and Rahul 52 not out take India to 159 for 1.
Footer: 21 November is World Television Day.
"""

import hashlib
import os
import struct
import sys
import zlib

# ------------------------------------------------------------------ font --
# A 5x7 pixel font, drawn from scratch for this entry. Each glyph is
# seven rows of five pixels; "#" is on, "." is off. Capitals, digits
# and a small set of punctuation. Lowercase input is folded to upper
# case (the font is capitals-only).

FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "*": (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
}

# --------------------------------------------------------------- colours --
PAPER = (248, 244, 233)   # cream newsprint
INK = (22, 22, 22)        # near-black
RED = (166, 30, 30)       # lead-story red
BLUE = (29, 78, 137)      # section blue
GOLD = (150, 110, 20)     # footer gold
GREY = (120, 116, 106)    # rules
LIGHT = (238, 232, 216)   # card background


class Canvas:
    """An RGB pixel buffer with tiny drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color):
        import math
        for deg in range(360):
            a = math.radians(deg)
            self.set(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)), color)

    def arc(self, cx, cy, r, a0, a1, color):
        import math
        for deg in range(a0, a1 + 1):
            a = math.radians(deg)
            self.set(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)), color)

    def text_width(self, text, scale):
        return len(text) * (5 * scale + scale)

    def text(self, text, x, y, scale, color):
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale

    def text_centred(self, text, cx, y, scale, color):
        self.text(text, cx - self.text_width(text, scale) // 2, y, scale, color)

    def wrap(self, text, max_width, scale):
        """Greedy word wrap; returns a list of lines."""
        unit = 6 * scale
        lines = []
        for para in text.split("\n"):
            line = ""
            for word in para.split(" "):
                trial = word if not line else line + " " + word
                if len(trial) * unit <= max_width or not line:
                    line = trial
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)
        return lines


# ----------------------------------------------------------------- icons --
def icon_burst(cv, cx, cy, r, color):
    """Explosion starburst for the lead story."""
    import math
    for k in range(12):
        a = math.radians(k * 30)
        x1 = cx + int(0.45 * r * math.cos(a))
        y1 = cy + int(0.45 * r * math.sin(a))
        x2 = cx + int(r * math.cos(a))
        y2 = cy + int(r * math.sin(a))
        cv.line(x1, y1, x2, y2, color)
    cv.disc(cx, cy, r // 3, color)


def icon_globe(cv, cx, cy, r, color):
    cv.ring(cx, cy, r, color)
    cv.hline(cx - r, cy, 2 * r, color)
    cv.arc(cx, cy, r // 2, 200, 340, color)
    cv.arc(cx, cy, r // 2, 20, 160, color)
    cv.vline(cx, cy - r, 2 * r, color)


def icon_cyclone(cv, cx, cy, r, color):
    for k, rr in enumerate((r, int(r * 0.7), int(r * 0.45))):
        cv.arc(cx, cy, rr, 40 + k * 60, 300 + k * 60, color)


def icon_shield(cv, x, y, s, color):
    pts = [(x + s // 2, y), (x + s, y + s // 4), (x + s, y + s // 2),
           (x + s // 2, y + s), (x, y + s // 2), (x, y + s // 4)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        cv.line(a[0], a[1], b[0], b[1], color)
    # lightning bolt inside
    cv.line(x + s // 2 + 2, y + s // 4, x + s // 2 - 3, y + s // 2, color)
    cv.line(x + s // 2 - 3, y + s // 2, x + s // 2 + 3, y + s // 2, color)
    cv.line(x + s // 2 + 3, y + s // 2, x + s // 2 - 2, y + 3 * s // 4, color)


def icon_ballot(cv, x, y, s, color):
    cv.rect(x, y + s // 3, s, 2 * s // 3, color)
    cv.rect(x + 2, y + s // 3 + 2, s - 4, 2 * s // 3 - 4, PAPER)
    cv.hline(x + s // 4, y + s // 6, s // 2, color)
    cv.line(x + s // 4, y + s // 2, x + s // 2, y + 2 * s // 3, color)
    cv.line(x + s // 2, y + 2 * s // 3, x + 3 * s // 4, y + s // 3 + 4, color)


def icon_eu_stars(cv, cx, cy, r, color):
    import math
    for k in range(12):
        a = math.radians(k * 30 - 90)
        cv.disc(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)), 3, color)


def icon_cricket(cv, x, y, s, color):
    cv.line(x + 4, y + s - 4, x + s - 6, y + 6, color)
    cv.line(x + 6, y + s - 4, x + s - 4, y + 8, color)
    cv.disc(x + s - 8, y + s - 8, 6, color)


# ---------------------------------------------------------------- content --
LEAD_HEAD = "KYIV UNDER FIRE"
LEAD_SUB = "RUSSIA'S BIGGEST AERIAL ASSAULT IN WEEKS"
LEAD_BODY = (
    "Russian missiles and drones hit the capital overnight. Three bridges "
    "were struck and at least nine people were killed. Austrian and Dutch "
    "embassy buildings were damaged. France called for a UN Security "
    "Council meeting.")

CARDS = [
    ("CLIMATE", BLUE, icon_globe,
     "CLIMATE TALKS RUN INTO OVERTIME",
     "Draft deal in Antalya drops every mention of fossil fuels. Panama "
     "threatens to block consensus. Next summit: Addis Ababa, 2027."),
    ("WEATHER", BLUE, icon_cyclone,
     "CYCLONE AKVAN HITS ODISHA",
     "The storm crosses the coast near Gopalpur with heavy rain and "
     "strong winds. About 300,000 people were moved to safety."),
    ("TECH", BLUE, icon_shield,
     "BANKS REPORT VENDOR CYBERATTACK",
     "JPMorgan, Visa and Mastercard say outside suppliers were hit. "
     "The firms say core payment networks were not affected."),
    ("ASIA", BLUE, icon_ballot,
     "MONGOLIA'S PRESIDENT QUITS",
     "Parliament approves Khurelsukh Ukhnaa's resignation, the first by "
     "a sitting president. An early election must be called within "
     "four months."),
    ("EUROPE", BLUE, icon_eu_stars,
     "EU SENDS KYIV ITS BIGGEST AID YET",
     "Brussels completes a disbursement of nearly 8 billion euros to "
     "Ukraine, its largest-ever single payment."),
    ("SPORT", BLUE, icon_cricket,
     "INDIA FIGHT BACK IN WELLINGTON",
     "Nicholls 175 not out and Phillips 118 lift New Zealand to 368. "
     "Jaiswal 85 and Rahul 52 not out take India to 159 for 1."),
]

FOOTER = "21 NOVEMBER IS WORLD TELEVISION DAY"
SOURCES = ("SOURCES: AP, REUTERS, CRICBUZZ, JAGRAN JOSH - "
           "ALL STORIES REPORTED 21 NOVEMBER 2026")


def draw():
    W, H = 1024, 1024
    cv = Canvas(W, H, PAPER)
    mx = 36  # margin

    # ------------------------------------------------------------ masthead --
    cv.text_centred("THE WORLD IN ONE DAY", W // 2, 30, 6, INK)
    cv.hline(mx, 96, W - 2 * mx, INK)
    cv.hline(mx, 100, W - 2 * mx, INK)
    cv.text_centred("SATURDAY 21 NOVEMBER 2026", W // 2, 112, 2, RED)
    cv.text_centred("ONE IMAGE - SEVEN STORIES", W // 2, 134, 1, GREY)
    cv.hline(mx, 158, W - 2 * mx, INK)

    # ---------------------------------------------------------- lead story --
    ly, lh = 176, 190
    cv.rect(mx, ly, 8, lh, RED)
    cv.text(LEAD_HEAD, mx + 24, ly + 8, 4, INK)
    cv.text(LEAD_SUB, mx + 24, ly + 48, 2, RED)
    body_w = W - 2 * mx - 24 - 150
    lines = cv.wrap(LEAD_BODY, body_w, 2)
    y = ly + 78
    for ln in lines:
        cv.text(ln, mx + 24, y, 2, INK)
        y += 22
    icon_burst(cv, W - mx - 62, ly + lh // 2, 52, RED)

    # ------------------------------------------------------------ grid ------
    gy = 386
    cw, chh, gap = 466, 168, 20
    for idx, (tag, color, icon, head, body) in enumerate(CARDS):
        col, row = idx % 2, idx // 2
        x = mx + col * (cw + gap)
        y = gy + row * (chh + gap)
        cv.rect(x, y, cw, chh, LIGHT)
        cv.rect(x, y, cw, 3, color)
        cv.text(tag, x + 14, y + 12, 1, color)
        head_lines = cv.wrap(head, cw - 28 - 56, 2)
        hy = y + 32
        for ln in head_lines[:2]:
            cv.text(ln, x + 14, hy, 2, INK)
            hy += 22
        body_lines = cv.wrap(body, cw - 28, 1)
        by = hy + 6
        for ln in body_lines[:4]:
            cv.text(ln, x + 14, by, 1, INK)
            by += 13
        if icon is icon_globe:
            icon(cv, x + cw - 34, y + 40, 24, color)
        elif icon is icon_cyclone:
            icon(cv, x + cw - 34, y + 40, 24, color)
        elif icon is icon_eu_stars:
            icon(cv, x + cw - 34, y + 40, 20, color)
        else:
            icon(cv, x + cw - 58, y + 16, 44, color)

    # -------------------------------------------------------------- footer --
    fy = 940
    cv.hline(mx, fy, W - 2 * mx, INK)
    cv.text_centred(FOOTER, W // 2, fy + 12, 2, GOLD)
    cv.text_centred(SOURCES, W // 2, fy + 40, 1, GREY)
    return cv


# -------------------------------------------------------------------- png --
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def to_png(cv):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = draw()
    png = to_png(cv)
    assert png[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG magic"
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes, sha256 %s)"
          % (path, len(png), hashlib.sha256(png).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
