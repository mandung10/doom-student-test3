"""CLASS BUSTER 학교판 - 총을 학용품으로 바꾼 무기/아이템/발사체 스프라이트 (3D 원시도형 렌더링, GPLv2)."""
import math
import numpy as np
from PIL import Image, ImageDraw
from sprites3d import ell, box, cap, rot_x, rot_y, rot_z, transform, render, crop

D = math.radians
SKIN, SLV, CUFF = '#f2c39a', '#f4f6ff', '#4a7fe0'
YEL, PINK, SIL, WOODC = '#ffd23a', '#ff9fb8', '#c8ccd4', '#e8b878'

def hand(x, y, z, s=1.0):
    g = np.sign(x) or 1
    return [ell((x, y, z), (7.5 * s, 6.5 * s, 10 * s), SKIN), ell((x - g * 4, y + 3, z + 9), (3, 3, 5), SKIN), ell((x + g * 1, y + 4, z + 11), (3, 3, 5), SKIN), ell((x - g * 8, y + 1, z + 3), (2.6, 2.8, 4.5), SKIN)]
def sleeve(x0, y0, z0, x1, y1, z1, r=7.6): return [cap((x0, y0, z0), (x1, y1, z1), r, SLV, emit=.2), ell((x1, y1, z1), (r + 1.2, r + 1.2, 3.2), CUFF, emit=.1)]
def arms(lx, ly, lz, rx, ry, rz):
    lx, rx = lx * .85, rx * .85
    return hand(lx, ly, lz + 6, 1.35) + hand(rx, ry, rz + 6, 1.35) + sleeve(lx * 1.5, ly - 8, lz - 26, lx * 1.1, ly - 1, lz - 8) + sleeve(rx * 1.5, ry - 8, rz - 26, rx * 1.1, ry - 1, rz - 8)

def tilt(prims, deg=0.0, dz=0.0, dy=0.0):
    M = rot_x(D(-deg)); return transform(prims, M, (0, dy, dz))

def pencil(c=YEL, L=60, r=7.6, z0=0.0, x=0.0, y=0.0):
    p = [cap((x, y, z0), (x, y, z0 + L), r, c), cap((x, y, z0 + L * .22), (x, y, z0 + L * .26), r + .3, '#e24a4a'),
         ell((x, y, z0 + L + 5), (r * .86, r * .86, 11), WOODC), ell((x, y, z0 + L + 14), (r * .36, r * .36, 5), '#3a3a44'),
         cap((x, y, z0 - 1), (x, y, z0 + 5), r + .5, SIL), ell((x, y, z0 - 5), (r, r, 5.5), PINK)]
    return p

def w_pistol(f):
    k = [0, 7, 4, 2, 0][f]
    body = tilt(pencil(L=58) , deg=k * 1.8, dz=-k, dy=0)
    return body + arms(-9, -6, 4, 9, -6, 4)
def w_shotgun(f):
    pump = [0, 10, 18, 8][f]; k = [0, 6, 3, 1][f]
    stripes = [cap((0, 0, 8 + i * 10), (0, 0, 14 + i * 10), 9.2, '#ff5a6a' if i % 2 else '#fff6f0') for i in range(5)]
    tube = [cap((0, 0, 0), (0, 0, 64), 8.6, '#fff6f0')] + stripes + [cap((0, 0, 62), (0, 0, 70), 10.5, '#ffd23a')]
    for i in range(7):
        a = i * math.pi / 3.5; tube.append(ell((math.cos(a) * 7, math.sin(a) * 7 + 2, 75 + (i % 3) * 3), (2.6, 2.6, 5), ['#ff5a8a', '#4ab0ff', '#ffe040', '#5adb7a'][i % 4], emit=.6))
    grip = [box((0, -8.5, 26 + pump), (11, 5, 9), '#2f9be0'), box((0, -8.5, 26 + pump), (11.6, 1.5, 9.6), '#7cc8ff')]
    return tilt(tube + grip, deg=k * 1.6, dz=-k) + arms(-12, -9, 24 + pump, 11, -8, 2)
def w_chain(f):
    rot = [0, 30][f % 2]; k = [0, 3][f % 2]
    cols = ['#ff4a4a', '#ff9a30', '#ffd23a', '#4acb6a', '#3aa0ff', '#a05aff']
    pr = [cap((0, 0, 0), (0, 0, 40), 12, '#8d93a0'), cap((0, 0, 38), (0, 0, 44), 13.2, '#4a505c'), box((0, -12, 12), (9, 8, 14), '#5a6070')]
    for i in range(6):
        a = D(rot + i * 60); x, y = math.cos(a) * 8.4, math.sin(a) * 8.4
        pr += [cap((x, y, 30), (x, y, 78), 4.0, cols[i]), ell((x, y, 84), (3.3, 3.3, 8), WOODC), ell((x, y, 91), (1.4, 1.4, 3), '#3a3a44')]
    return tilt(pr, deg=k, dz=-k * .5) + arms(-12, -8, 22, 12, -10, 2)
def w_rocket(f):
    k = [0, 5][f % 2]
    cone = [cap((0, 0, 0), (0, 0, 36), 13, '#6fb4ff'), cap((0, 0, 34), (0, 0, 52), 17, '#8fd0ff'), cap((0, 0, 50), (0, 0, 58), 19, '#ffd23a'),
            cap((0, 0, 8), (0, 0, 14), 13.6, '#ff5a6a'), cap((0, 0, 22), (0, 0, 28), 13.6, '#ff5a6a'), box((0, -14, 12), (8, 8, 12), '#4a80c8')]
    plane = [box((0, 3, 60 + 6), (12, .8, 9), '#ffffff'), box((0, 6, 62), (1, 5, 12), '#e8eef8')] if f == 0 else []
    return tilt(cone + plane, deg=k * 1.4, dz=-k) + arms(-14, -8, 20, 12, -10, 2)
def w_plasma(f):
    k = [0, 4][f % 2]
    pr = [ell((0, -2, 22), (11, 11, 34), '#ff7ab0'), ell((0, 11, 20), (9, 7, 26), '#9fe0ff', emit=.35), cap((0, 0, 50), (0, 0, 68), 4.2, '#ffd23a'),
          ell((0, 0, 70), (3, 3, 3), '#ffffff'), box((0, -14, 14), (7, 8, 11), '#3a8fe0')]
    return tilt(pr, deg=k * 1.2, dz=-k) + arms(-12, -10, 22, 11, -10, 0)
def w_bfg(f):
    k = [0, 0, 6][min(f, 2)]
    pr = [cap((0, 0, 0), (0, 0, 28), 8.5, '#ff5a6a'), cap((0, 0, 26), (0, 0, 46), 14, '#fff6f0'), cap((0, 0, 44), (0, 0, 62), 21, '#ff5a6a'), cap((0, 0, 60), (0, 0, 66), 23, '#ffd23a'),
          ell((0, 0, 60), (15, 15, 2), '#ffe9a0', emit=.5), box((0, -12, 6), (6, 9, 10), '#4a505c')]
    return tilt(pr, deg=k, dz=-k) + arms(-14, -10, 14, 12, -11, -2)
def w_saw(f):
    sh = [0, 2, 0, 3][f]; sp = [0, 20, 0, 40][f]
    pr = [box((0, 0, 20), (18, 12, 24), '#ffd23a'), box((0, 10, 22), (14, 2, 18), '#ffeb8a'), cap((0, -2, 46), (0, -2, 70), 3, SIL)]
    for i in range(8):
        a = D(sp + i * 45); pr.append(ell((math.cos(a) * 11, -2 + math.sin(a) * 11, 66), (3.5, 3.5, 1.4), '#c8ccd4'))
    pr.append(cap((0, -2, 64), (0, -2, 68), 9, '#e8e8f0'))
    return tilt(pr, deg=0, dz=0, dy=sh) + arms(-16, -8, 8, 17, -10, 8)
def w_fist(f):
    ext = [0, 40, 24, 8][f]
    book = [box((0, 0, 14 + ext), (16, 4, 22), '#ff6a5a'), box((0, 0, 14 + ext), (15, 4.6, 21), '#fff6f0'), box((-15, 0, 14 + ext), (2.5, 5, 22), '#c8402e'), box((0, 4.6, 14 + ext), (11, .5, 8), '#ffd23a')]
    return book + arms(-14, -3, 10 + ext * .6, 14, -3, 10 + ext * .6)

W_MODELS = {'PUNG': (w_fist, 'ABCD'), 'PISG': (w_pistol, 'ABCDE'), 'SHTG': (w_shotgun, 'ABCD'), 'CHGG': (w_chain, 'AB'), 'MISG': (w_rocket, 'AB'),
            'PLSG': (w_plasma, 'AB'), 'BFGG': (w_bfg, 'ABC'), 'SAWG': (w_saw, 'ABCD')}
WSHIFT = {'PUNG': {'A': 0, 'B': -18, 'C': -10, 'D': -4}, 'PISG': {'A': 0, 'B': 4, 'C': 2, 'D': 6, 'E': 10}, 'SHTG': {'A': 0, 'B': 4, 'C': 18, 'D': 10},
          'CHGG': {'A': 0, 'B': 2}, 'MISG': {'A': 0, 'B': 3}, 'PLSG': {'A': 0, 'B': 2}, 'BFGG': {'A': 0, 'B': 0, 'C': 4}, 'SAWG': {'A': 0, 'B': 1, 'C': 0, 'D': 1}}
SCALE = {'PUNG': 1.3, 'PISG': 1.5, 'SHTG': 1.25, 'CHGG': 1.15, 'MISG': 1.1, 'PLSG': 1.3, 'BFGG': 1.05, 'SAWG': 1.2}

def weapon_rgba(pre, letter):
    fn, letters = W_MODELS[pre]
    f = letters.index(letter) if letter in letters else 0
    prims = fn(f)
    prims = transform(prims, np.eye(3) * SCALE[pre])
    rgba, ox, oy = render(prims, yaw_deg=180, pitch_deg=32, ambient=.62)
    rgba, ox, oy = crop(rgba, ox, oy)
    return rgba

def star(rgba_size, colors, pts=10, r1=0.5, spokes=True, seed=0):
    w, h = rgba_size; im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy = w / 2, h / 2; R = min(w, h) / 2 - 1
    rng = np.random.default_rng(seed)
    poly = [(cx + math.cos(i * math.pi / pts) * (R if i % 2 == 0 else R * r1), cy + math.sin(i * math.pi / pts) * (R if i % 2 == 0 else R * r1)) for i in range(pts * 2)]
    d.polygon(poly, fill=colors[0]); d.polygon([(cx + (x - cx) * .6, cy + (y - cy) * .6) for x, y in poly], fill=colors[1])
    d.ellipse((cx - R * .22, cy - R * .22, cx + R * .22, cy + R * .22), fill=colors[2])
    for i in range(int(R // 3)):
        a = rng.random() * 6.28; rr = R * (.5 + rng.random() * .5); c = ['#ff5a8a', '#4ab0ff', '#ffe040', '#5adb7a'][i % 4]
        d.rectangle((cx + math.cos(a) * rr, cy + math.sin(a) * rr, cx + math.cos(a) * rr + 2, cy + math.sin(a) * rr + 2), fill=c)
    return np.asarray(im)

# ---------------------------------------------------------------- pickups / items (ground sprites)
def i_clip():  # 연필 한 묶음
    return [cap((-3 + i * 3, 0, -9), (-3 + i * 3, 0, 9), 2.2, c) for i, c in enumerate(['#ff4a4a', YEL, '#4a9aff'])] + [ell((-3 + i * 3, 0, 12), (1.6, 1.6, 3.5), WOODC) for i in range(3)] + [cap((-6, -1, 1), (6, -1, 1), 2.6, '#ff7a3a')]
def i_ammo():  # 연필 상자
    return [box((0, 0, 0), (12, 4, 8), '#ffd23a'), box((0, 4, 0), (12, .6, 8), '#ffeb8a')] + [cap((-8 + i * 4, 4.5, -6), (-8 + i * 4, 4.5, 9), 1.5, c) for i, c in enumerate(['#ff4a4a', '#4a9aff', '#5adb7a', '#ff9a30', '#a05aff', '#ff5a8a'])]
def i_shel():  # 색종이 폭죽 2개
    return [cap((-4, 0, -6), (-4, 0, 6), 3, '#ff5a6a'), cap((4, 0, -6), (4, 0, 6), 3, '#4a9aff'), ell((-4, 0, 8), (3.4, 3.4, 2), '#ffd23a'), ell((4, 0, 8), (3.4, 3.4, 2), '#ffd23a')]
def i_sbox():
    return [box((0, 0, 0), (12, 5, 7), '#ff7ab0'), box((0, 5, 0), (11, .6, 6), '#fff6f0')] + [cap((-8 + i * 5.3, 0, 7), (-8 + i * 5.3, 0, 13), 2.4, c) for i, c in enumerate(['#ffd23a', '#4a9aff', '#5adb7a', '#ff4a4a'])]
def i_rock():  # 종이비행기
    return [box((0, 0, 0), (9, .9, 8), '#ffffff'), box((0, 2.4, -1), (.9, 3, 8), '#dfe8f8'), box((0, 0, 7), (3, .9, 3), '#eef3fb')]
def i_brok():
    return [box((0, 0, 0), (13, 5, 7), '#6fb4ff'), box((0, 5, 0), (12, .6, 6), '#fff6f0'), box((0, 6, 1), (8, .9, 6), '#ffffff')]
def i_cell():  # 물풍선
    return [ell((0, 0, 0), (7, 8, 7), '#4ab0ff', emit=.15), ell((-2, 2, 2), (2, 2, 2), '#c8ecff'), ell((0, -8, 0), (2, 3, 2), '#2a80d8')]
def i_celp():
    return [ell((-6, 0, 0), (6, 7, 6), '#4ab0ff'), ell((6, 0, 0), (6, 7, 6), '#ff7ab0'), ell((0, 0, 8), (6, 7, 6), '#ffd23a')]
def i_pencilgun(c):
    return [cap((-14, 0, 0), (14, 0, 0), 4, c), ell((17, 0, 0), (5, 3.6, 3.6), WOODC), ell((20, 0, 0), (2, 1.5, 1.5), '#3a3a44'), ell((-17, 0, 0), (3.8, 3.8, 3.8), PINK)]
def i_mgun():
    return [cap((-14, 0, 2 * i - 4), (14, 0, 2 * i - 4), 2.6, c) for i, c in enumerate(['#ff4a4a', '#ff9a30', YEL, '#4acb6a', '#3aa0ff'])] + [cap((-6, 0, -6), (-6, 0, 8), 2.5, '#6a7080')]
def i_shot():
    return [cap((-14, 0, 0), (12, 0, 0), 4, '#fff6f0'), cap((-8, 0, 0), (-4, 0, 0), 4.5, '#ff5a6a'), cap((2, 0, 0), (6, 0, 0), 4.5, '#ff5a6a'), cap((12, 0, 0), (16, 0, 0), 5.5, '#ffd23a'), box((-4, -3, 0), (5, 2, 3), '#2f9be0')]
def i_laun():
    return [cap((-12, 0, 0), (8, 0, 0), 5.5, '#6fb4ff'), cap((8, 0, 0), (16, 0, 0), 8, '#ffd23a'), box((-4, -5, 0), (3, 3, 3), '#4a80c8')]
def i_plas():
    return [ell((0, 0, 0), (11, 5, 5), '#ff7ab0'), ell((0, 5, 0), (8, 3, 4), '#9fe0ff'), cap((10, 0, 0), (17, 0, 0), 2.4, '#ffd23a')]
def i_bfug():
    return [cap((-14, 0, 0), (-4, 0, 0), 3.5, '#ff5a6a'), cap((-4, 0, 0), (8, 0, 0), 6.5, '#fff6f0'), cap((8, 0, 0), (17, 0, 0), 9.5, '#ff5a6a')]
def i_csaw():  # 전동 연필깎이
    return [box((0, 0, 0), (9, 5, 7), '#ffd23a'), ell((10, 0, 0), (1.5, 8, 8), '#c8ccd4'), box((0, 5, 0), (6, .6, 4), '#ffeb8a')]
def i_bpak():
    return [ell((0, 0, 0), (11, 13, 8), '#ff7a30'), ell((0, -4, 7), (8, 6, 3), '#d85a18'), cap((-8, -10, 2), (-8, 10, 2), 1.6, '#fff6f0'), cap((8, -10, 2), (8, 10, 2), 1.6, '#fff6f0')]
def i_arm1():  # 초록 책가방
    return [ell((0, 0, 0), (11, 14, 7), '#3aaa5a'), ell((0, -4, 7), (8, 6, 3), '#2a8a44'), ell((0, 10, 2), (4, 2, 3), '#ffd23a')]
def i_arm2():  # 파란 책가방
    return [ell((0, 0, 0), (11, 14, 7), '#3a7ae0'), ell((0, -4, 7), (8, 6, 3), '#2a5ab8'), ell((0, 10, 2), (4, 2, 3), '#ff5a6a')]
def i_bon1():  # 우유 팩
    return [box((0, 0, 0), (5, 9, 5), '#f4fbff'), box((0, 0, 5.2), (5.1, 9.1, .6), '#4ab0ff'), box((0, 10, 0), (5, 2, 5), '#f4fbff'), ell((0, 0, 6), (2.5, 3, 1.2), '#ff5a6a')]
def i_bon2():  # 학사모
    return [box((0, 3, 0), (11, .9, 11), '#2a2e40'), cap((0, -3, 0), (0, 3, 0), 6.5, '#2a2e40'), cap((9, 3, 9), (9, -6, 10), .6, '#ffd23a'), ell((9, -7, 10), (1.5, 2.5, 1.5), '#ffd23a')]
def i_stim():  # 사과
    return [ell((0, 0, 0), (7, 7, 7), '#ff4a3a'), ell((-2, 2, 4), (1.8, 1.8, 1.8), '#ffd0c8'), cap((0, 7, 0), (1, 11, 0), .9, '#6a4a2a'), ell((4, 10, 0), (3, 1.2, 2), '#4acb6a')]
def i_medi():  # 구급상자
    return [box((0, 0, 0), (13, 8, 5), '#ffffff'), box((0, 0, 5.2), (3, 6, .5), '#ff3a3a'), box((0, 0, 5.2), (9, 2, .5), '#ff3a3a'), cap((-5, 9, 0), (5, 9, 0), 1.4, '#9aa0aa')]
def i_soul():  # 100점 별 구슬
    return [ell((0, 0, 0), (9, 9, 9), '#ffd23a', emit=.45), ell((-3, 3, 5), (3, 3, 3), '#fff9d0', emit=.8)] + [ell((math.cos(i * 1.256) * 11, math.sin(i * 1.256) * 11, 0), (2.5, 2.5, 2.5), '#fff6c0', emit=.8) for i in range(5)]
def i_mega():
    return [ell((0, 0, 0), (10, 10, 10), '#ff7ab0', emit=.4), ell((-3, 3, 5), (3, 3, 3), '#fff0f8', emit=.8)]
def i_pinv():  # 별 배지
    return [ell((0, 0, 0), (9, 9, 2.5), '#ffd23a', emit=.4), ell((0, 0, 2.2), (6, 6, 1), '#fff4b0', emit=.7)] + [ell((math.cos(i * 1.2566 + 1.57) * 9, math.sin(i * 1.2566 + 1.57) * 9, 0), (3, 3, 2.5), '#ffd23a', emit=.4) for i in range(5)]
def i_pstr():  # 비타민 병
    return [cap((0, -6, 0), (0, 5, 0), 5.5, '#ff9a30'), cap((0, 5, 0), (0, 8, 0), 3.5, '#fff6f0'), box((0, -1, 5.6), (4, 3, .4), '#ffffff')]
def i_pins():
    return [ell((0, 0, 0), (9, 9, 9), '#bfe8ff', emit=.5), ell((-3, 3, 5), (3, 3, 3), '#ffffff', emit=.9)]
def i_suit():  # 노란 우비
    return [ell((0, 0, 0), (10, 13, 5), '#ffd23a'), cap((-12, 8, 0), (-6, 0, 0), 3, '#ffd23a'), cap((12, 8, 0), (6, 0, 0), 3, '#ffd23a'), ell((0, 12, 2), (5, 4, 4), '#ffc21a')]
def i_pmap():  # 학교 지도
    return [box((0, 0, 0), (11, 8, .8), '#fff6dc'), box((-5, 0, .9), (.6, 8, .4), '#8a6a3a'), box((0, 0, .9), (.6, 8, .4), '#8a6a3a'), box((3, 2, 1), (3, 2, .3), '#5adb7a'), box((-3, -3, 1), (3, 2, .3), '#4ab0ff')]
def i_pvis():  # 손전등
    return [cap((-10, 0, 0), (6, 0, 0), 3.6, '#3a8fe0'), cap((6, 0, 0), (12, 0, 0), 5.4, '#ffd23a'), ell((13, 0, 0), (1.5, 4, 4), '#ffffe0', emit=.9)]
def i_card(c):
    return [box((0, 0, 0), (7, 9, 1), '#fffaf0'), box((0, 3, 1.1), (6, 1.5, .3), c), box((0, -3, 1.1), (3, 3, .3), '#aab4c8'), cap((0, 9, 0), (0, 14, 0), .8, c), ell((0, 15, 0), (2.5, 1.5, 1), c)]
def i_key(c):
    return [ell((0, 6, 0), (5, 5, 1.6), c), ell((0, 6, 0), (2, 2, 2), '#2a2e40'), cap((0, 2, 0), (0, -10, 0), 1.6, c), box((2, -8, 0), (2, 1, 1.4), c), box((2, -4, 0), (2, 1, 1.4), c)]
def i_balloon_proj():
    return [ell((0, 0, 0), (7, 8, 7), '#4ab0ff', emit=.4), ell((-2, 2, 3), (2, 2, 2), '#e8f8ff', emit=.9), ell((0, -8, 0), (1.6, 2.4, 1.6), '#2a80d8', emit=.4)]
def i_plane_proj():
    return [box((0, 0, 0), (7, .8, 6), '#ffffff'), box((0, 1.8, -1), (.8, 2.4, 6), '#e0e8f8'), box((0, 0, 7), (2.4, .8, 3), '#eef3fb')]
def i_bfg_proj():
    return [ell((0, 0, 0), (12, 12, 12), '#ffd23a', emit=.6), ell((-3, 3, 7), (4, 4, 4), '#fffbd8', emit=.9)] + [ell((math.cos(i * 1.0472) * 13, math.sin(i * 1.0472) * 13, 0), (2.5, 2.5, 2.5), ['#ff5a8a', '#4ab0ff', '#5adb7a'][i % 3], emit=.8) for i in range(6)]
def i_bucket():  # 페인트 통
    return [cap((0, -7, 0), (0, 6, 0), 8, '#4ab0ff'), cap((0, 6, 0), (0, 8, 0), 8.6, '#ffffff'), ell((0, 9, 0), (6.5, 2, 6.5), '#ff7ab0'), cap((-8, 7, 0), (8, 7, 0), .8, SIL)]

ITEMS = {
    'CLIP': i_clip, 'AMMO': i_ammo, 'SHEL': i_shel, 'SBOX': i_sbox, 'ROCK': i_rock, 'BROK': i_brok, 'CELL': i_cell, 'CELP': i_celp,
    'MGUN': i_mgun, 'SHOT': i_shot, 'LAUN': i_laun, 'PLAS': i_plas, 'BFUG': i_bfug, 'CSAW': i_csaw, 'BPAK': i_bpak, 'ARM1': i_arm1, 'ARM2': i_arm2,
    'BON1': i_bon1, 'BON2': i_bon2, 'STIM': i_stim, 'MEDI': i_medi, 'SOUL': i_soul, 'MEGA': i_mega, 'PINV': i_pinv, 'PSTR': i_pstr, 'PINS': i_pins,
    'SUIT': i_suit, 'PMAP': i_pmap, 'PVIS': i_pvis, 'BKEY': lambda: i_card('#3a7ae0'), 'YKEY': lambda: i_card('#ffc21a'), 'RKEY': lambda: i_card('#ff4a4a'),
    'BSKU': lambda: i_key('#3a7ae0'), 'YSKU': lambda: i_key('#ffc21a'), 'RSKU': lambda: i_key('#ff4a4a'), 'BAR1': i_bucket,
}
ITEM_VIEW = {'CLIP': (0, 18), 'AMMO': (0, 20), 'SHEL': (0, 18), 'SBOX': (0, 20), 'ROCK': (0, 30), 'BROK': (0, 20), 'CELL': (0, 18), 'CELP': (0, 18), 'MGUN': (0, 40), 'SHOT': (0, 40), 'LAUN': (0, 40),
             'PLAS': (0, 40), 'BFUG': (0, 40), 'CSAW': (0, 36), 'PMAP': (0, 60), 'BKEY': (0, 10), 'YKEY': (0, 10), 'RKEY': (0, 10), 'BSKU': (0, 8), 'YSKU': (0, 8), 'RSKU': (0, 8), 'SUIT': (0, 50), 'BON2': (0, 36)}
ISCALE = {'CLIP': 1.5, 'AMMO': 1.4, 'SHEL': 1.5, 'SBOX': 1.4, 'ROCK': 1.5, 'BROK': 1.4, 'CELL': 1.5, 'CELP': 1.4, 'BPAK': 1.4, 'ARM1': 1.5, 'ARM2': 1.5, 'BON1': 1.5, 'BON2': 1.5, 'STIM': 1.6, 'MEDI': 1.4,
          'SOUL': 1.5, 'MEGA': 1.8, 'PINV': 1.6, 'PSTR': 1.5, 'PINS': 1.5, 'SUIT': 1.4, 'PMAP': 1.5, 'PVIS': 1.5, 'BKEY': 1.5, 'YKEY': 1.5, 'RKEY': 1.5, 'BSKU': 1.5, 'YSKU': 1.5, 'RSKU': 1.5,
          'MGUN': 1.6, 'SHOT': 1.5, 'LAUN': 1.5, 'PLAS': 1.6, 'BFUG': 1.5, 'CSAW': 1.6, 'BAR1': 1.7}

def item_rgba(pre, frame=0):
    prims = ITEMS[pre]()
    s = ISCALE.get(pre, 1.5)
    prims = transform(prims, np.eye(3) * s)
    yaw, pit = ITEM_VIEW.get(pre, (0, 18))
    if pre in ('BKEY', 'YKEY', 'RKEY', 'BSKU', 'YSKU', 'RSKU', 'PMAP'): pit = 12
    if pre in ('MGUN', 'SHOT', 'LAUN', 'PLAS', 'BFUG', 'CSAW'): prims = transform(prims, rot_x(D(-70)))  # lay flat, show top
    if pre in ('SOUL', 'MEGA', 'PINV', 'BON1', 'BON2', 'PINS', 'PSTR') and frame:
        prims = transform(prims, rot_y(D(frame * 90)))
    rgba, ox, oy = render(prims, yaw_deg=0, pitch_deg=pit if pre not in ('MGUN', 'SHOT', 'LAUN', 'PLAS', 'BFUG', 'CSAW') else 8)
    return crop(rgba, ox, oy)
