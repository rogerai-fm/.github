"""Compose the org-profile banner: Flux art remapped to the mono ramp + one red beacon + wordmark.

Run from this folder with Pillow, and with fonts/ holding JetBrainsMono-Regular.ttf and static
Space Grotesk Bold/Medium instances (from the site's variable woff2 via fontTools.varLib.instancer).
Writes banner-light.png and banner-dark.png; copy them to profile/assets/.
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

SRC = "source-art.png"  # Flux flux1-dev-fp8, seed 37, 1600x528
BEACON = (1276, 89)
RED = (0xE0, 0x23, 0x1C)
F = "fonts/"

THEMES = {
    # ramp: (darkest, lightest) the luminance is mapped onto; text colors per theme
    "light": dict(ramp=((0x15, 0x14, 0x0F), (0xFB, 0xFB, 0xFA)), ink=(0x15, 0x14, 0x0F),
                  sub=(0x33, 0x31, 0x2B), mute=(0x6B, 0x68, 0x5F)),
    "dark": dict(ramp=((0x08, 0x08, 0x06), (0x2E, 0x2C, 0x27)), ink=(0xF4, 0xF4, 0xF2),
                 sub=(0xD8, 0xD7, 0xD2), mute=(0x9A, 0x96, 0x8C)),
}


def ramp(lum, lo, hi):
    lut = []
    for c in range(3):
        lut += [round(lo[c] + (hi[c] - lo[c]) * i / 255) for i in range(256)]
    return Image.merge("RGB", [lum] * 3).point(lut)


def mark(d, x, y, s, ink):
    """The ((on air)) monogram from web/src/logo.svg, scaled from its 32-unit box."""
    k = s / 32
    P = lambda pts: [(x + px * k, y + py * k) for px, py in pts]
    d.polygon(P([(4, 6), (13, 6), (13, 10.5), (8.5, 10.5), (8.5, 21.5), (13, 21.5), (13, 26), (4, 26)]), fill=ink)
    d.polygon(P([(28, 6), (19, 6), (19, 10.5), (23.5, 10.5), (23.5, 21.5), (19, 21.5), (19, 26), (28, 26)]), fill=ink)
    r = 5 * k
    d.ellipse([x + 16 * k - r, y + 16 * k - r, x + 16 * k + r, y + 16 * k + r], fill=RED)


def spaced(d, xy, text, font, fill, track):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track


def build(theme, out):
    t = THEMES[theme]
    lum = ImageOps.autocontrast(Image.open(SRC).convert("L"), cutoff=0.5)
    im = ramp(lum, *t["ramp"]).convert("RGB")
    d = ImageDraw.Draw(im)
    # The beacon: one crisp dot in the logo's red, over the art's own lamp.
    bx, by = BEACON
    d.ellipse([bx - 10, by - 7, bx + 10, by + 13], fill=RED)

    x0 = 96
    spaced(d, (x0 + 2, 64), "LOCAL MODELS  ·  INFERENCE NETWORK  ·  ON AIR",
           ImageFont.truetype(F + "JetBrainsMono-Regular.ttf", 23), t["mute"], 2.4)
    mark(d, x0 - 8, 112, 112, t["ink"])
    d.text((x0 + 118, 104), "RogerAI", font=ImageFont.truetype(F + "SpaceGrotesk-Bold.ttf", 108), fill=t["ink"])
    d.text((x0 + 2, 248), "A two-way radio for GPUs.",
           font=ImageFont.truetype(F + "SpaceGrotesk-Medium.ttf", 44), fill=t["sub"])
    im.save(out, optimize=True)


if __name__ == "__main__":
    for theme in sys.argv[1:] or THEMES:
        build(theme, f"banner-{theme}.png")
        print("wrote", f"banner-{theme}.png")
