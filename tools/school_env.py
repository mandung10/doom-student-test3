"""CLASS BUSTER 학교판 - 벽 텍스처 / 바닥·천장 / 하늘을 밝은 학교 그림으로 만드는 생성기 (GPLv2)."""
import re, zlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTP = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
_fc = {}
def font(sz):
    if sz not in _fc:
        try: _fc[sz] = ImageFont.truetype(FONTP, sz, index=1)
        except Exception: _fc[sz] = ImageFont.load_default()
    return _fc[sz]

def rng_for(name): return np.random.default_rng(zlib.crc32(name.encode()))
def U8(a): return np.clip(a, 0, 255).astype(np.uint8)
def dim(c, f): return tuple(int(max(0, min(255, v * f))) for v in c)
def finish(im, rng, grain=5, vgrad=0.0):
    a = np.asarray(im, float)
    a += rng.normal(0, grain, a.shape[:2])[..., None]
    if vgrad:
        a *= (1 + vgrad * (np.linspace(0.5, -0.5, a.shape[0]))[:, None, None])
    return U8(a)

PASTELS = [(252, 240, 200), (196, 236, 208), (176, 214, 248), (255, 208, 176), (255, 246, 160), (222, 200, 248), (255, 200, 214), (200, 240, 236)]
BRIGHT = [(60, 120, 235), (235, 70, 70), (250, 200, 40), (60, 190, 90), (250, 140, 40), (160, 90, 220)]
WOOD = (196, 140, 80)

def poster(d, w, h, rng, x=None, y=None):
    pw, ph = int(rng.integers(14, 24)), int(rng.integers(16, 28))
    x = int(rng.integers(4, max(5, w - pw - 3))) if x is None else x
    y = int(rng.integers(8, max(9, int(h * .36)))) if y is None else y
    col = BRIGHT[int(rng.integers(len(BRIGHT)))]
    d.rectangle((x, y, x + pw, y + ph), fill=(255, 255, 250), outline=dim(col, .7))
    k = int(rng.integers(4))
    cx, cy = x + pw // 2, y + ph // 2
    if k == 0: d.ellipse((cx - 5, cy - 6, cx + 5, cy + 4), fill=col)
    elif k == 1: d.polygon([(cx, cy - 7), (cx + 2, cy - 2), (cx + 7, cy - 2), (cx + 3, cy + 1), (cx + 5, cy + 7), (cx, cy + 3), (cx - 5, cy + 7), (cx - 3, cy + 1), (cx - 7, cy - 2), (cx - 2, cy - 2)], fill=col)
    elif k == 2: d.rectangle((cx - 6, cy - 6, cx + 6, cy), fill=col)
    else: d.polygon([(cx - 6, cy + 5), (cx, cy - 6), (cx + 6, cy + 5)], fill=col)
    for ly in range(y + ph - 8, y + ph - 2, 3): d.line((x + 3, ly, x + pw - 3, ly), fill=(150, 150, 160))
    d.rectangle((x + pw // 2 - 2, y - 1, x + pw // 2 + 2, y + 1), fill=(240, 200, 60))

def paint_wall(w, h, rng, c=None, rail=True, deco=True):
    c = c or PASTELS[int(rng.integers(len(PASTELS)))]
    im = Image.new('RGB', (w, h), c); d = ImageDraw.Draw(im)
    if h >= 64 and rail:
        ry = int(h * .58)
        d.rectangle((0, ry, w, h), fill=dim(c, .8))
        for x in range(0, w, 8): d.line((x, ry + 4, x, h - 8), fill=dim(c, .66))
        d.rectangle((0, ry, w, ry + 2), fill=(252, 250, 240)); d.line((0, ry + 3, w, ry + 3), fill=dim(c, .6))
        d.rectangle((0, h - 6, w, h), fill=(168, 112, 66)); d.line((0, h - 7, w, h - 7), fill=(120, 78, 44))
    if deco and h >= 96 and w >= 64 and rng.random() < .55: poster(d, w, h, rng)
    if deco and h >= 96 and w >= 128 and rng.random() < .5: poster(d, w, h, rng)
    return finish(im, rng, 4, .05)

def brick(w, h, rng):
    base = [(214, 120, 90), (226, 150, 100), (200, 110, 84), (232, 170, 120)][int(rng.integers(4))]
    im = Image.new('RGB', (w, h), (246, 236, 220)); d = ImageDraw.Draw(im)
    for r in range(0, h // 8 + 1):
        for c in range(-1, w // 16 + 2):
            x, y = c * 16 + (r & 1) * 8, r * 8
            f = .86 + rng.random() * .26
            col = dim(base, f)
            d.rectangle((x + 1, y + 1, x + 15, y + 7), fill=col)
            d.line((x + 1, y + 1, x + 15, y + 1), fill=dim(col, 1.15))
            d.line((x + 1, y + 7, x + 15, y + 7), fill=dim(col, .8))
    return finish(im, rng, 5)

def lockers(w, h, rng):
    cols = [(70, 130, 235), (235, 80, 80), (250, 205, 50), (70, 195, 100), (250, 150, 60), (150, 100, 225)]
    base = cols[int(rng.integers(len(cols)))]
    im = Image.new('RGB', (w, h), dim(base, .55)); d = ImageDraw.Draw(im)
    lw = 16 if w % 16 == 0 else max(8, w // 2)
    for x0 in range(0, w, lw):
        col = dim(base, .92 + .12 * rng.random())
        d.rectangle((x0 + 1, 1, x0 + lw - 2, h - 2), fill=col, outline=dim(base, .6))
        d.line((x0 + 2, 2, x0 + lw - 3, 2), fill=dim(col, 1.2))
        for k in range(4): d.line((x0 + 3, 7 + k * 3, x0 + lw - 4, 7 + k * 3), fill=dim(base, .55))
        for k in range(3): d.line((x0 + 3, h - 14 + k * 3, x0 + lw - 4, h - 14 + k * 3), fill=dim(base, .55))
        d.rectangle((x0 + lw - 6, h // 2 - 4, x0 + lw - 4, h // 2 + 3), fill=(240, 240, 235), outline=(90, 90, 90))
        d.rectangle((x0 + 4, h // 2 - 14, x0 + lw - 8, h // 2 - 9), fill=(250, 250, 240))
    return finish(im, rng, 4, .04)

def chalkboard(w, h, rng):
    im = Image.new('RGB', (w, h), (214, 168, 110)); d = ImageDraw.Draw(im)
    m = 4
    d.rectangle((m, m, w - m - 1, h - m - 8), fill=(40, 98, 78), outline=(120, 80, 40))
    d.rectangle((m + 1, m + 1, w - m - 2, h - m - 9), outline=(60, 120, 96))
    d.rectangle((m - 1, h - 9, w - m, h - 5), fill=(168, 112, 66))
    for i in range(3):
        d.rectangle((m + 6 + i * 9, h - 11, m + 11 + i * 9, h - 9), fill=[(250, 250, 240), (255, 220, 90), (250, 160, 190)][i])
    T = ['E=mc²', '1+1=2', 'ABC', '가나다', 'π≈3.14', 'H₂O', '★', '5×5', 'a²+b²', 'Hello']
    fs = max(9, min(18, (h - 20) // 3))
    for k in range(2 if h < 100 else 3):
        t = T[int(rng.integers(len(T)))]
        d.text((m + 5 + int(rng.integers(0, max(1, w // 3))), m + 2 + k * (fs + 4)), t, font=font(fs), fill=(244, 244, 232))
    return finish(im, rng, 3)

def corkboard(w, h, rng):
    a = np.zeros((h, w, 3)) + np.array([206, 154, 98]) + rng.normal(0, 14, (h, w, 1))
    im = Image.fromarray(U8(a)); d = ImageDraw.Draw(im)
    cols = [(255, 255, 245), (255, 240, 140), (170, 220, 255), (255, 190, 210), (200, 255, 200)]
    for k in range(max(2, w * h // 800)):
        pw, ph = int(rng.integers(12, 24)), int(rng.integers(14, 26))
        x, y = int(rng.integers(2, max(3, w - pw - 2))), int(rng.integers(2, max(3, h - ph - 2)))
        c = cols[k % len(cols)]
        d.rectangle((x, y, x + pw, y + ph), fill=c, outline=(150, 110, 80))
        for ly in range(y + 4, y + ph - 2, 3): d.line((x + 2, ly, x + pw - 3 - (ly * 7) % 6, ly), fill=(110, 110, 150))
        d.ellipse((x + pw // 2 - 1, y - 1, x + pw // 2 + 2, y + 2), fill=(230, 50, 50))
    d.rectangle((0, 0, w - 1, h - 1), outline=(140, 88, 44), width=3)
    return np.asarray(im)

def tiles(w, h, rng):
    a, b = [((246, 248, 250), (176, 218, 245)), ((252, 246, 224), (255, 200, 150)), ((240, 250, 240), (170, 226, 190))][int(rng.integers(3))]
    im = Image.new('RGB', (w, h), (200, 205, 210)); d = ImageDraw.Draw(im)
    for y in range(0, h, 16):
        for x in range(0, w, 16):
            c = a if ((x // 16 + y // 16) % 4) else b
            d.rectangle((x + 1, y + 1, x + 15, y + 15), fill=c)
            d.line((x + 1, y + 1, x + 14, y + 1), fill=dim(c, 1.1)); d.line((x + 1, y + 15, x + 15, y + 15), fill=dim(c, .85))
    return finish(im, rng, 3)

def window(w, h, rng):
    im = Image.new('RGB', (w, h), (250, 244, 224)); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 6, 8, w - 7, h - 24
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        d.line((x0, y, x1, y), fill=(int(120 + 90 * t), int(190 + 50 * t), 250))
    d.ellipse((x1 - 20, y0 + 4, x1 - 6, y0 + 18), fill=(255, 235, 110))
    for k in range(2):
        cx, cy = x0 + 8 + int(rng.integers(0, max(1, (x1 - x0) - 30))), y0 + 12 + k * 14
        for dx, r in ((0, 6), (7, 8), (15, 6)): d.ellipse((cx + dx - r, cy - r // 2, cx + dx + r, cy + r // 2 + 2), fill=(255, 255, 255))
    d.rectangle((x0, y0, x1, y1), outline=(150, 100, 60), width=3)
    d.line(((x0 + x1) // 2, y0, (x0 + x1) // 2, y1), fill=(150, 100, 60), width=2); d.line((x0, (y0 + y1) // 2, x1, (y0 + y1) // 2), fill=(150, 100, 60), width=2)
    d.rectangle((x0 - 3, y1 + 1, x1 + 3, y1 + 5), fill=(190, 130, 76))
    d.rectangle((0, h - 6, w, h), fill=(168, 112, 66))
    return finish(im, rng, 3)

def bookshelf(w, h, rng):
    im = Image.new('RGB', (w, h), (176, 118, 66)); d = ImageDraw.Draw(im)
    C = [(235, 70, 70), (70, 130, 235), (70, 195, 100), (250, 205, 50), (160, 100, 225), (255, 255, 245), (250, 150, 60)]
    sh = 24
    for r in range(0, h // sh + 1):
        y = r * sh; p = 3
        while p < w - 4:
            bw = int(rng.integers(3, 8)); bh = int(rng.integers(sh - 9, sh - 3)); c = C[int(rng.integers(len(C)))]
            d.rectangle((p, y + sh - 4 - bh, p + bw, y + sh - 4), fill=c, outline=dim(c, .65))
            d.line((p + 1, y + sh - 4 - bh + 3, p + bw - 1, y + sh - 4 - bh + 3), fill=(255, 255, 255))
            p += bw + 1
        d.rectangle((0, y + sh - 3, w, y + sh), fill=(122, 78, 40))
    return finish(im, rng, 3)

def woodpanel(w, h, rng):
    im = Image.new('RGB', (w, h), WOOD); d = ImageDraw.Draw(im)
    pw = 16 if w % 16 == 0 else 8
    for x in range(0, w, pw):
        c = dim(WOOD, .9 + .2 * rng.random())
        d.rectangle((x, 0, x + pw - 1, h), fill=c); d.line((x, 0, x, h), fill=dim(c, .7))
        for k in range(6):
            gx = x + int(rng.integers(2, pw - 2)); d.line((gx, int(rng.integers(0, h)), gx, int(rng.integers(0, h))), fill=dim(c, .85))
    return finish(im, rng, 4)

def computer(w, h, rng):
    im = Image.new('RGB', (w, h), (232, 238, 244)); d = ImageDraw.Draw(im)
    mw, mh = 28, 22
    for y in range(4, h - mh - 12, mh + 14):
        for x in range(4, w - mw, mw + 6):
            d.rectangle((x, y, x + mw, y + mh), fill=(70, 74, 86), outline=(40, 42, 50))
            sc = [(90, 200, 250), (130, 230, 150), (255, 220, 110), (250, 150, 190)][int(rng.integers(4))]
            d.rectangle((x + 2, y + 2, x + mw - 2, y + mh - 2), fill=sc)
            for k in range(3): d.line((x + 4, y + 5 + k * 5, x + 4 + int(rng.integers(6, mw - 10)), y + 5 + k * 5), fill=(255, 255, 255))
            d.rectangle((x + mw // 2 - 3, y + mh + 1, x + mw // 2 + 3, y + mh + 5), fill=(120, 124, 136))
            d.rectangle((x + 3, y + mh + 6, x + mw - 3, y + mh + 9), fill=(190, 194, 204))
    d.rectangle((0, h - 6, w, h), fill=(168, 112, 66))
    return finish(im, rng, 3)

def pipes(w, h, rng):
    im = paint_wall(w, h, rng, rail=False, deco=False); d = ImageDraw.Draw(Image.fromarray(im)); img = Image.fromarray(im); d = ImageDraw.Draw(img)
    for k, y in enumerate(range(12, h - 8, 24)):
        c = BRIGHT[(k + int(rng.integers(6))) % 6]
        d.rectangle((0, y, w, y + 8), fill=c); d.line((0, y + 1, w, y + 1), fill=dim(c, 1.3)); d.line((0, y + 7, w, y + 7), fill=dim(c, .7))
        for x in range(8, w, 32): d.rectangle((x, y - 2, x + 4, y + 10), fill=(220, 220, 225), outline=(120, 120, 130))
    return np.asarray(img)

def marble(w, h, rng):
    a = np.zeros((h, w, 3)) + np.array([238, 236, 230])
    im = Image.fromarray(U8(a)); d = ImageDraw.Draw(im)
    for k in range(7):
        x = int(rng.integers(0, w)); pts = [(x, 0)]
        for y in range(8, h + 8, 8): x += int(rng.integers(-6, 7)); pts.append((x, y))
        d.line(pts, fill=(176, 186, 200), width=1)
    return finish(im, rng, 4, .04)

def mats(w, h, rng):
    c = BRIGHT[int(rng.integers(6))]
    im = Image.new('RGB', (w, h), dim(c, .6)); d = ImageDraw.Draw(im)
    for y in range(0, h, 32):
        for x in range(0, w, 32):
            f = .95 + .12 * rng.random(); col = dim(c, f)
            d.rounded_rectangle((x + 1, y + 1, x + 31, y + 31), 5, fill=col)
            d.line((x + 4, y + 3, x + 28, y + 3), fill=dim(col, 1.25))
            d.ellipse((x + 14, y + 14, x + 18, y + 18), fill=dim(c, .7))
    return finish(im, rng, 4)

def mascot(w, h, rng):
    im = paint_wall(w, h, rng, rail=True, deco=False); img = Image.fromarray(im); d = ImageDraw.Draw(img)
    r = min(w, h * 0.5) * 0.36; cx, cy = w // 2, int(h * .34)
    for k in range(12):
        a = k * math.pi / 6; d.polygon([(cx + math.cos(a - .12) * r, cy + math.sin(a - .12) * r), (cx + math.cos(a) * r * 1.5, cy + math.sin(a) * r * 1.5), (cx + math.cos(a + .12) * r, cy + math.sin(a + .12) * r)], fill=(255, 200, 40))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 224, 70), outline=(230, 150, 20), width=2)
    d.ellipse((cx - r * .45, cy - r * .3, cx - r * .2, cy), fill=(60, 40, 20)); d.ellipse((cx + r * .2, cy - r * .3, cx + r * .45, cy), fill=(60, 40, 20))
    d.arc((cx - r * .5, cy - r * .1, cx + r * .5, cy + r * .6), 20, 160, fill=(200, 60, 40), width=2)
    d.ellipse((cx - r * .8, cy + r * .1, cx - r * .5, cy + r * .35), fill=(255, 160, 140)); d.ellipse((cx + r * .5, cy + r * .1, cx + r * .8, cy + r * .35), fill=(255, 160, 140))
    return np.asarray(img)

def door(w, h, rng, color=None, kind='single'):
    c = color or [(214, 150, 84), (84, 160, 220), (96, 190, 110)][int(rng.integers(3))]
    im = Image.new('RGB', (w, h), dim(c, .62)); d = ImageDraw.Draw(im)
    leaves = 2 if (kind == 'double' or w >= 128) else 1
    lw = w // leaves
    for L in range(leaves):
        x0 = L * lw
        d.rectangle((x0 + 3, 2, x0 + lw - 4, h - 1), fill=c, outline=dim(c, .55))
        d.line((x0 + 4, 3, x0 + lw - 5, 3), fill=dim(c, 1.25))
        gx0, gx1 = x0 + lw // 2 - 9, x0 + lw // 2 + 9
        d.rectangle((gx0, 8, gx1, 8 + max(16, h // 3)), fill=(170, 220, 250), outline=(250, 250, 245), width=2)
        d.line(((gx0 + gx1) // 2, 8, (gx0 + gx1) // 2, 8 + max(16, h // 3)), fill=(250, 250, 245))
        d.rectangle((x0 + lw - 12, h // 2 + 2, x0 + lw - 8, h // 2 + 6), fill=(236, 220, 120), outline=(120, 100, 40))
        d.rectangle((x0 + lw // 2 - 8, h // 2 + 8, x0 + lw // 2 + 8, h // 2 + 16), fill=(250, 250, 240), outline=dim(c, .6))
        d.text((x0 + lw // 2 - 6, h // 2 + 6), '%d-%d' % (1 + int(rng.integers(3)), 1 + int(rng.integers(9))), font=font(9), fill=(60, 60, 70))
        d.rectangle((x0 + 5, h - 22, x0 + lw - 6, h - 4), fill=dim(c, .88), outline=dim(c, .6))
    d.rectangle((0, 0, w, 1), fill=(250, 250, 240))
    return finish(im, rng, 3)

def doorframe(w, h, rng, color):
    im = Image.new('RGB', (w, h), color); d = ImageDraw.Draw(im)
    for y in range(0, h, 8): d.line((0, y, w, y + 3), fill=dim(color, 1.2))
    d.line((0, 0, 0, h), fill=dim(color, 1.35)); d.line((w - 1, 0, w - 1, h), fill=dim(color, .6))
    return finish(im, rng, 3)

def light(w, h, rng):
    a = np.zeros((h, w, 3)) + np.array([255, 252, 220])
    im = Image.fromarray(U8(a)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=(220, 220, 205)); d.rectangle((1, 1, w - 2, h - 2), outline=(255, 255, 240))
    return finish(im, rng, 2)

def stripes(w, h, rng):
    im = Image.new('RGB', (w, h), (255, 215, 60)); d = ImageDraw.Draw(im)
    for k in range(-h, w + h, 16): d.polygon([(k, h), (k + 8, h), (k + 8 + h, 0), (k + h, 0)], fill=(70, 70, 90))
    return finish(im, rng, 3)

def column(w, h, rng):
    c = PASTELS[int(rng.integers(len(PASTELS)))]
    xs = np.linspace(-1, 1, w)[None, :, None]
    a = np.zeros((h, w, 3)) + np.array(c, float); a *= (1.15 - .45 * np.abs(xs - .2) ** 1.5)
    im = Image.fromarray(U8(a)); d = ImageDraw.Draw(im)
    for y in (6, h - 10): d.rectangle((0, y, w, y + 4), fill=dim(c, .75))
    return finish(np.asarray(im), rng, 3) if False else np.asarray(im)

def step(w, h, rng):
    im = Image.new('RGB', (w, h), (196, 140, 84)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 2), fill=(250, 215, 60)); d.rectangle((0, h - 2, w, h), fill=(140, 96, 56))
    return finish(im, rng, 4)

def plat(w, h, rng):
    im = Image.new('RGB', (w, h), (110, 170, 240)); d = ImageDraw.Draw(im)
    d.rectangle((2, 2, w - 3, h - 3), outline=(250, 250, 245), width=3)
    for k in range(3): d.polygon([(w // 2, 18 + k * 30), (w // 2 - 12, 34 + k * 30), (w // 2 + 12, 34 + k * 30)], fill=(255, 220, 60))
    return finish(im, rng, 3)

def switch(w, h, rng, on):
    im = Image.new('RGB', (w, h), (240, 244, 248)); d = ImageDraw.Draw(im)
    d.rectangle((1, 1, w - 2, h - 2), outline=(150, 156, 170), width=2)
    cx, cy = w // 2, h // 2
    d.rounded_rectangle((cx - w // 4, cy - h // 6, cx + w // 4, cy + h // 6), 6, fill=(60, 70, 96), outline=(30, 34, 48))
    ly = cy - h // 8 if on else cy + h // 8
    d.line((cx, cy, cx, ly), fill=(40, 40, 50), width=max(3, w // 10))
    d.ellipse((cx - w // 9, ly - w // 9, cx + w // 9, ly + w // 9), fill=(70, 210, 90) if on else (235, 60, 60))
    d.ellipse((cx - 4, 6, cx + 4, 14), fill=(80, 240, 110) if on else (255, 70, 60))
    return finish(im, rng, 2)

def exit_sign(w, h, rng):
    im = Image.new('RGB', (w, h), (36, 160, 80)); d = ImageDraw.Draw(im)
    d.rectangle((1, 1, w - 2, h - 2), outline=(240, 250, 240), width=2)
    fs = max(8, min(22, h // 2 + 2)); t = '출구 EXIT' if w >= 48 else 'EXIT'
    bb = d.textbbox((0, 0), t, font=font(fs)); d.text(((w - (bb[2] - bb[0])) // 2, (h - (bb[3] - bb[1])) // 2 - bb[1]), t, font=font(fs), fill=(255, 255, 255))
    return np.asarray(im)

def exitdoor(w, h, rng):
    a = door(w, h, rng, (70, 190, 100)); im = Image.fromarray(a); d = ImageDraw.Draw(im)
    d.rectangle((w // 2 - 24, 4, w // 2 + 24, 20), fill=(30, 140, 70), outline=(250, 250, 245), width=2)
    d.text((w // 2 - 20, 4), '출구', font=font(14), fill=(255, 255, 255))
    return np.asarray(im)

def flow(w, h, rng, phase, name):
    pal = [(120, 190, 255), (190, 235, 255), (255, 255, 255), (150, 215, 255)]
    if name.startswith(('FIRE', 'ROCK')): pal = [(255, 120, 150), (255, 210, 80), (130, 220, 130), (130, 170, 255)]
    if name.startswith(('BLOD', 'SLAD', 'DBRAIN', 'GST')): pal = [(190, 150, 255), (255, 160, 210), (255, 235, 130), (140, 230, 200)]
    im = Image.new('RGB', (w, h), pal[0]); d = ImageDraw.Draw(im)
    off = phase * (h // 4)
    for x in range(0, w, 4):
        c = pal[(x // 4) % len(pal)]
        for y in range(-16, h + 16, 16):
            yy = (y + off + (x * 7) % 16) % (h + 16) - 8
            d.rectangle((x, yy, x + 2, yy + 9), fill=c)
    return finish(im, rng, 3)

def mesh(w, h, rng, avg=None):
    return None  # handled by recolor in builder

def sky(w, h, rng):
    t = np.linspace(0, 1, h)[:, None, None]
    top, bot = np.array([70, 150, 240.]), np.array([200, 232, 255.])
    a = top * (1 - t) + bot * t + np.zeros((h, w, 3))
    def pn(fx, fy, seed):
        r = np.random.default_rng(seed); g = r.random((fy + 1, fx))
        g = np.concatenate([g, g[:, :1]], 1)
        xs = np.linspace(0, fx, w, endpoint=False); ys = np.linspace(0, fy, h)
        x0 = xs.astype(int); fxr = (xs - x0)[None, :]; y0 = np.minimum(ys.astype(int), fy - 1); fyr = (ys - y0)[:, None]
        sx = fxr * fxr * (3 - 2 * fxr); sy = fyr * fyr * (3 - 2 * fyr)
        v00 = g[y0][:, x0]; v10 = g[y0][:, x0 + 1]; v01 = g[y0 + 1][:, x0]; v11 = g[y0 + 1][:, x0 + 1]
        return (v00 * (1 - sx) + v10 * sx) * (1 - sy) + (v01 * (1 - sx) + v11 * sx) * sy
    cl_ = pn(4, 3, 1) * .6 + pn(8, 5, 2) * .3 + pn(16, 9, 3) * .1
    cm = np.clip((cl_ - .5) * 3.2, 0, 1) * (1 - np.abs(np.linspace(-1, 1, h))[:, None] ** 3 * .6)
    a = a * (1 - cm[..., None]) + np.array([255, 255, 255.]) * cm[..., None]
    im = Image.fromarray(U8(a)); d = ImageDraw.Draw(im)
    for k in range(9):  # distant hills + school building
        x0 = int(k * w / 9)
        d.ellipse((x0 - 20, h - 26 - (k * 7) % 9, x0 + w // 9 + 24, h + 20), fill=(110, 200, 120))
    bx = w // 3
    d.rectangle((bx, h - 40, bx + 64, h - 12), fill=(250, 235, 205), outline=(210, 170, 130)); d.rectangle((bx + 24, h - 54, bx + 40, h - 40), fill=(250, 235, 205), outline=(210, 170, 130))
    d.polygon([(bx - 2, h - 40), (bx + 66, h - 40), (bx + 32, h - 52)], fill=(220, 90, 70)) if False else None
    for wx in range(bx + 6, bx + 60, 12): d.rectangle((wx, h - 34, wx + 6, h - 26), fill=(150, 205, 245))
    d.rectangle((0, h - 14, w, h), fill=(100, 190, 100))
    return np.asarray(im)

# ------------------------------------------------------------------ flats (64x64)
def f_tile(rng, a=(250, 244, 226), b=(176, 218, 245), size=32):
    im = Image.new('RGB', (64, 64), (190, 196, 200)); d = ImageDraw.Draw(im)
    for y in range(0, 64, size):
        for x in range(0, 64, size):
            c = a if ((x + y) // size) % 2 == 0 else b
            d.rectangle((x + 1, y + 1, x + size - 1, y + size - 1), fill=c)
            d.line((x + 1, y + 1, x + size - 2, y + 1), fill=dim(c, 1.08))
    return finish(im, rng, 3)
def f_wood(rng, base=WOOD):
    im = Image.new('RGB', (64, 64), base); d = ImageDraw.Draw(im)
    for i in range(0, 64, 8):
        c = dim(base, .88 + .24 * rng.random()); d.rectangle((0, i, 63, i + 7), fill=c); d.line((0, i + 7, 63, i + 7), fill=dim(c, .62))
        for k in range(2): x = int(rng.integers(0, 64)); d.line((x, i, x, i + 7), fill=dim(c, .62))
        for k in range(4): x = int(rng.integers(0, 60)); d.line((x, i + 3, x + 6, i + 3), fill=dim(c, .9))
    return finish(im, rng, 3)
def f_parquet(rng):
    im = Image.new('RGB', (64, 64), WOOD); d = ImageDraw.Draw(im)
    for by in range(0, 64, 16):
        for bx in range(0, 64, 16):
            hor = ((bx + by) // 16) % 2 == 0; c = dim(WOOD, .9 + .2 * rng.random()); d.rectangle((bx, by, bx + 15, by + 15), fill=c)
            for k in range(0, 16, 4): d.line(((bx, by + k) if hor else (bx + k, by), (bx + 15, by + k) if hor else (bx + k, by + 15)), fill=dim(c, .7))
    return finish(im, rng, 3)
def f_carpet(rng, c):
    a = np.zeros((64, 64, 3)) + np.array(c, float) + rng.normal(0, 9, (64, 64, 1))
    im = Image.fromarray(U8(a)); d = ImageDraw.Draw(im)
    for k in range(0, 64, 16): d.rectangle((k + 6, 6, k + 9, 9), fill=dim(c, 1.25)); d.rectangle((k + 14, 38, k + 17, 41), fill=dim(c, 1.25))
    return np.asarray(im)
def f_grass(rng):
    a = np.zeros((64, 64, 3)) + np.array([96, 196, 84.]) + rng.normal(0, 10, (64, 64, 1))
    im = Image.fromarray(U8(a)); d = ImageDraw.Draw(im)
    for k in range(60):
        x, y = int(rng.integers(0, 64)), int(rng.integers(0, 64)); d.line((x, y, x + int(rng.integers(-2, 3)), y - 3), fill=(130, 225, 100))
    for k in range(5):
        x, y = int(rng.integers(2, 60)), int(rng.integers(2, 60)); d.ellipse((x, y, x + 2, y + 2), fill=(255, 250, 200))
    return np.asarray(im)
def f_track(rng):
    a = np.zeros((64, 64, 3)) + np.array([230, 118, 80.]) + rng.normal(0, 8, (64, 64, 1))
    im = Image.fromarray(U8(a)); d = ImageDraw.Draw(im); d.rectangle((0, 28, 63, 31), fill=(250, 250, 245))
    return np.asarray(im)
def f_gym(rng):
    im = Image.fromarray(f_wood(rng, (232, 184, 110))); d = ImageDraw.Draw(im); d.rectangle((0, 30, 63, 33), fill=(250, 250, 245)); d.arc((10, 8, 54, 52), 0, 360, fill=(70, 130, 235), width=2)
    return np.asarray(im)
def f_sand(rng):
    a = np.zeros((64, 64, 3)) + np.array([246, 224, 160.]) + rng.normal(0, 8, (64, 64, 1)); return U8(a)
def f_pavers(rng):
    im = Image.new('RGB', (64, 64), (204, 196, 186)); d = ImageDraw.Draw(im)
    for y in range(0, 64, 16):
        for x in range(-8, 64, 16):
            xx = x + (y // 16 % 2) * 8; c = dim((232, 214, 190), .9 + .18 * rng.random()); d.rectangle((xx + 1, y + 1, xx + 14, y + 14), fill=c)
    return finish(im, rng, 3)
def f_ceil(rng, lit=True):
    im = Image.new('RGB', (64, 64), (246, 244, 236)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 63, 63), outline=(206, 206, 198)); d.line((0, 32, 63, 32), fill=(214, 214, 206)); d.line((32, 0, 32, 63), fill=(214, 214, 206))
    for k in range(18): x, y = int(rng.integers(2, 60)), int(rng.integers(2, 60)); d.point((x, y), fill=(200, 200, 192))
    if lit: d.rectangle((8, 24, 56, 40), fill=(255, 254, 224), outline=(255, 255, 250))
    return finish(im, rng, 2)
def f_lamp(rng):
    im = Image.new('RGB', (64, 64), (255, 253, 226)); d = ImageDraw.Draw(im); d.rectangle((0, 0, 63, 63), outline=(236, 232, 190), width=3); d.rectangle((6, 6, 57, 57), outline=(255, 255, 245))
    return finish(im, rng, 2)
def f_liquid(rng, kind, ph):
    c0, c1 = {'water': ((90, 170, 250), (200, 235, 255)), 'slime': ((130, 235, 110), (230, 255, 150)), 'sauce': ((255, 150, 50), (255, 230, 100)), 'ink': ((90, 110, 240), (170, 190, 255)), 'jelly': ((196, 176, 250), (236, 226, 255))}[kind]
    ys, xs = np.mgrid[0:64, 0:64] / 64.0 * 2 * math.pi
    v = np.sin(xs * 2 + ph * math.pi / 2) + np.sin(ys * 3 - ph * math.pi / 2 + xs) + np.sin((xs + ys) * 2 + ph * math.pi / 2)
    t = (v + 3) / 6; a = np.array(c0)[None, None] * (1 - t[..., None]) + np.array(c1)[None, None] * t[..., None]
    return U8(a)

def classify_flat(name):
    n = name
    if n.startswith('NUKAGE'): return ('liquid', 'slime', int(n[-1]) - 1)
    if n.startswith(('FWATER', 'SWATER')): return ('liquid', 'water', int(n[-1]) - 1)
    if n.startswith('LAVA'): return ('liquid', 'sauce', int(n[-1]) - 1)
    if n.startswith('BLOOD'): return ('liquid', 'ink', int(n[-1]) - 1)
    m = re.match(r'SLIME(\d\d)$', n)
    if m:
        k = int(m.group(1)); return ('liquid', 'slime' if k <= 4 else 'water' if k <= 8 else 'jelly', (k - 1) % 4)
    m = re.match(r'RROCK(\d\d)$', n)
    if m and 5 <= int(m.group(1)) <= 8: return ('liquid', 'water', int(m.group(1)) - 5)
    if n.startswith('CEIL'): return ('ceil', zlib.crc32(n.encode()) % 3)
    if 'LITE' in n or n in ('FLAT17', 'FLAT22', 'FLAT23'): return ('lamp',)
    if n.startswith('GRASS') or n == 'GRNROCK': return ('grass',)
    return ('floor', zlib.crc32(n.encode()) % 10)

def make_flat(name):
    rng = rng_for(name); c = classify_flat(name)
    if c[0] == 'liquid': return f_liquid(rng, c[1], c[2])
    if c[0] == 'ceil': return f_ceil(rng, lit=c[1] != 2)
    if c[0] == 'lamp': return f_lamp(rng)
    if c[0] == 'grass': return f_grass(rng)
    k = c[1]
    return [lambda: f_tile(rng), lambda: f_wood(rng), lambda: f_tile(rng, (252, 236, 200), (255, 196, 160), 16), lambda: f_carpet(rng, (90, 150, 230)),
            lambda: f_parquet(rng), lambda: f_gym(rng), lambda: f_track(rng), lambda: f_pavers(rng), lambda: f_carpet(rng, (236, 110, 120)), lambda: f_sand(rng)][k]()

# ------------------------------------------------------------------ wall textures
DOORS = re.compile(r'(DOOR|^DR|^SPCDOOR|^ZDOOR|^METALDR|^TNTDOOR|^M_.DOOR)')
def make_texture(name, w, h, masked, avg, orig=None):
    """returns (rgb HxWx3 uint8, mask HxW bool or None)."""
    rng = rng_for(name); n = name
    if n.startswith('SW1') or n.startswith('SW2'): return switch(w, h, rng, n[2] == '2'), None
    if n.startswith('SKY'): return sky(w, h, rng), None
    m = re.match(r'(BLODGR|SLADRIP|BLODRIP|FIREMAG|FIREBLU|FIRELAV|FIREWAL|GSTFONT|ROCKRED|BFALL|SFALL|WFALL|DBRAIN)\w*?(\d)?$', n)
    if m: return flow(w, h, rng, int(m.group(2) or 0), n), None
    if masked and orig is not None:
        rgb, mk = orig
        lum = rgb.mean(-1, keepdims=True) / 255.0
        c = BRIGHT[zlib.crc32(n.encode()) % 6]
        out = U8(np.array(c)[None, None] * (.55 + .7 * lum))
        return out, mk
    if n.startswith('EXITSIGN') or n.startswith('PNK4EXIT'): return exit_sign(w, h, rng), None
    if n.startswith('EXITDOOR'): return exitdoor(w, h, rng), None
    if w <= 16 and h >= 64:
        col = (120, 160, 240) if 'BLU' in n else (250, 210, 50) if 'YEL' in n else (235, 80, 80) if 'RED' in n else (240, 200, 90) if n.startswith('LITE') else (214, 168, 110)
        return doorframe(w, h, rng, col), None
    if h <= 32 and n.startswith('STEP'): return step(w, h, rng), None
    if h <= 24: return exit_sign(w, h, rng) if n.startswith('NUKE') else step(w, h, rng), None
    if DOORS.search(n) and w >= 32 and h >= 64:
        col = (84, 140, 235) if 'BLU' in n else (250, 210, 50) if ('YEL' in n or n.startswith('M_Y')) else (235, 80, 80) if ('RED' in n or n.startswith('M_R')) else None
        return door(w, h, rng, col, 'double' if w >= 128 else 'single'), None
    if n.startswith('PLAT'): return plat(w, h, rng), None
    if n.startswith(('LITE', 'TEKLITE')) or 'LITE' in n: return light(w, h, rng), None
    if n.startswith(('COMP', 'TEKWALL', 'M_TEC', 'TEKGREN', 'TEKBRON', 'SPACEW', 'MODWALL')): return computer(w, h, rng), None
    if 'PIPE' in n: return pipes(w, h, rng), None
    if 'MARB' in n: return marble(w, h, rng), None
    if n.startswith(('SUPPORT', 'PILLAR', 'EGSUPRT', 'COLUMN')): return column(w, h, rng), None
    if n.startswith(('PANBOOK', 'PANCASE')): return bookshelf(w, h, rng), None
    if n.startswith(('GRAYWARN', 'GRAYRED')): return stripes(w, h, rng), None
    if re.search(r'(SKIN|FAC|SKUL|DUDE|SK_|BODY|ZZWOLF|SKIN)', n): return mascot(w, h, rng), None
    if re.search(r'(BRICK|BRIK|BRBRK|BIGBRIK|MOSBRI|STUCCO)', n) and w % 16 == 0: return brick(w, h, rng), None
    if re.search(r'(WOOD|ZIM|PANEL)', n): return woodpanel(w, h, rng), None
    if n.startswith('PANBLUE'): return paint_wall(w, h, rng, (176, 214, 248)), None
    r = (zlib.crc32(n.encode()) >> 3) % 100
    if r < 28: return paint_wall(w, h, rng), None
    if r < 42 and w % 16 == 0: return lockers(w, h, rng), None
    if r < 54: return mats(w, h, rng), None
    if r < 64 and w % 16 == 0: return tiles(w, h, rng), None
    if r < 74 and w >= 64 and h >= 64: return chalkboard(w, h, rng), None
    if r < 84 and w >= 64 and h >= 96: return window(w, h, rng), None
    if r < 92 and w >= 32 and h >= 48: return corkboard(w, h, rng), None
    if r < 96 and w >= 64 and h >= 96: return mascot(w, h, rng), None
    return paint_wall(w, h, rng), None
