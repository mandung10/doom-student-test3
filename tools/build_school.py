#!/usr/bin/env python3
"""CLASS BUSTER 학교판 빌더: classbuster.wad -> 밝은 학교 팔레트 + 학교 벽/바닥/하늘 + 학용품 무기·아이템.
usage: python3 build_school.py ../classbuster.wad ../classbuster_school.wad"""
import sys, struct, time, re, warnings
import numpy as np
from scipy.spatial import cKDTree
from sklearn.cluster import MiniBatchKMeans
warnings.filterwarnings('ignore')
from wadlib import Wad, decode_picture, encode_picture
import school_env as E
import school_items as S
from sprites3d import render, crop, transform, rot_y, rot_x

rng = np.random.default_rng(7)
t0 = time.time()
def log(*a): print(round(time.time() - t0, 1), *a, flush=True)

def looks_like_patch(d):
    if len(d) < 12: return False
    w, h, lo, to = struct.unpack('<hhhh', d[:8])
    if not (0 < w <= 1024 and 0 < h <= 512) or abs(lo) > 2048 or abs(to) > 2048: return False
    if len(d) < 8 + 4 * w: return False
    offs = struct.unpack('<%dI' % w, d[8:8 + 4 * w])
    if min(offs) < 8 + 4 * w or max(offs) >= len(d): return False
    try:
        for x in range(0, w, max(1, w // 6)):
            p = offs[x]; n = 0
            while d[p] != 0xff:
                p += d[p + 1] + 4; n += 1
                if n > 300 or p >= len(d): return False
        decode_picture(d)
    except Exception: return False
    return True

def main(src, dst):
    w = Wad(src)
    old_pal = np.frombuffer(w.get('PLAYPAL')[:768], np.uint8).reshape(256, 3).astype(int)
    lump = {}
    for l in w.lumps: lump.setdefault(l[0], l[1])
    # ---------------- textures: composite originals (for masks), generate school art
    pn = w.get('PNAMES'); n = struct.unpack('<i', pn[:4])[0]
    PN = [pn[4 + 8 * i:12 + 8 * i].rstrip(b'\0').decode().upper() for i in range(n)]
    def parse(tx):
        if not tx: return []
        c = struct.unpack('<i', tx[:4])[0]; out = []
        for o in struct.unpack('<%di' % c, tx[4:4 + 4 * c]):
            nm = tx[o:o + 8].rstrip(b'\0').decode().upper(); mk, wd, ht, cd, pc = struct.unpack('<ihhih', tx[o + 8:o + 22])
            out.append((nm, wd, ht, [struct.unpack('<hhhhh', tx[o + 22 + 10 * k:o + 32 + 10 * k]) for k in range(pc)]))
        return out
    T1, T2 = parse(w.get('TEXTURE1')), parse(w.get('TEXTURE2'))
    art = {}  # patch name -> (rgb, mask)
    texrows = []
    cnt = 0
    for tl in (T1, T2):
        rows = []
        for nm, wd, ht, ps in tl:
            can = np.zeros((ht, wd, 3), np.uint8); mask = np.zeros((ht, wd), bool)
            for ox, oy, pi, _, _ in ps:
                d = lump.get(PN[pi])
                if d is None: continue
                try: idx, m, _, _ = decode_picture(d)
                except Exception: continue
                h2, w2 = idx.shape; x0, y0 = max(ox, 0), max(oy, 0); x1, y1 = min(ox + w2, wd), min(oy + h2, ht)
                if x1 <= x0 or y1 <= y0: continue
                sub = old_pal[idx[y0 - oy:y1 - oy, x0 - ox:x1 - ox]]; mm = m[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
                can[y0:y1, x0:x1][mm] = sub[mm]; mask[y0:y1, x0:x1] |= mm
            masked = mask.mean() < .97
            rgb, mk = E.make_texture(nm, wd, ht, masked, None, (can, mask) if masked else None)
            assert rgb.shape[:2] == (ht, wd), (nm, rgb.shape, wd, ht)
            pname = 'CBT%05d' % cnt; cnt += 1
            art[pname] = (rgb, mk if mk is not None else np.ones((ht, wd), bool))
            rows.append((nm, wd, ht, pname))
        texrows.append(rows)
    log('textures', cnt)
    # ---------------- flats
    flats = {}
    fi, fj = w.index('F_START'), w.index('F_END')
    for li in range(fi + 1, fj):
        nm, d = w.lumps[li]
        if len(d) == 4096 and nm != 'F_SKY1' and not nm.endswith(('START', 'END')): flats[nm] = E.make_flat(nm)
    log('flats', len(flats))
    # ---------------- sprites: weapons, items, projectiles, bursts
    sp_new = {}  # lump name -> (rgba, leftoff, topoff)
    i0, j0 = w.index('S_START'), w.index('S_END')
    spn = [w.lumps[i][0] for i in range(i0 + 1, j0)]
    wtip = {}
    for pre, (fn, letters) in S.W_MODELS.items():
        for nm in spn:
            if nm[:4] == pre and nm[4] in letters:
                a = S.weapon_rgba(pre, nm[4]); h, wd = a.shape[:2]
                sh = S.WSHIFT[pre].get(nm[4], 0)
                sp_new[nm] = (a, wd // 2 - 159, h - 168 - sh)
                if nm[4] == 'A': wtip[pre] = 200 - h
    flashmap = {'PISF': 'PISG', 'SHTF': 'SHTG', 'CHGF': 'CHGG', 'MISF': 'MISG', 'PLSF': 'PLSG', 'BFGF': 'BFGG'}
    for nm in spn:
        pre = nm[:4]
        if pre in flashmap:
            k = ord(nm[4]) - 65; sz = int(30 + 8 * (k % 3) + (14 if pre in ('SHTF', 'MISF', 'BFGF') else 0))
            a = S.star((sz, sz), ['#ffe040', '#fff6b0', '#ffffff'], 10, .5, seed=k + 3)
            tip = wtip.get(flashmap[pre], 90)
            sp_new[nm] = (a, sz // 2 - 159, 32 - (tip - sz // 3) - 0)
        elif pre in S.ITEMS and pre != 'BAR1':
            fr = ord(nm[4]) - 65
            a, ox, oy = S.item_rgba(pre, fr if pre in ('SOUL', 'MEGA', 'PINV', 'BON1', 'BON2', 'PINS', 'PSTR') else 0)
            sp_new[nm] = (a, a.shape[1] // 2, a.shape[0] - 2)
        elif pre == 'BAR1':
            a, ox, oy = S.item_rgba('BAR1'); sp_new[nm] = (a, a.shape[1] // 2, a.shape[0] - 2)
        elif pre == 'MISL' and nm[4] == 'A':
            r = int(nm[5]); prims = S.i_plane_proj(); prims = transform(prims, np.eye(3) * 2.0)
            a, ox, oy = render(prims, yaw_deg=-(r - 1) * 45, pitch_deg=10); a, ox, oy = crop(a, ox, oy)
            sp_new[nm] = (a, a.shape[1] // 2, a.shape[0] // 2)
        elif pre in ('MISL', 'PLSE', 'BFE1', 'BFE2', 'BEXP') and not (pre == 'MISL' and nm[4] == 'A'):
            k = ord(nm[4]) - 65; big = {'MISL': 34, 'PLSE': 26, 'BFE1': 48, 'BFE2': 56, 'BEXP': 40}[pre]
            sz = int(big * (0.55 + 0.22 * min(k, 3)))
            cols = ['#8fd0ff', '#d8f0ff', '#ffffff'] if pre == 'PLSE' else ['#ff7ab0', '#ffd23a', '#ffffff']
            a = S.star((sz, sz), cols, 12, .45, seed=k + 11); sp_new[nm] = (a, sz // 2, sz // 2 + 2)
        elif pre in ('PLSS', 'BFS1'):
            prims = S.i_balloon_proj() if pre == 'PLSS' else S.i_bfg_proj(); prims = transform(prims, np.eye(3) * (1.5 if pre == 'PLSS' else 1.6))
            a, ox, oy = render(prims, yaw_deg=0, pitch_deg=8); a, ox, oy = crop(a, ox, oy)
            sp_new[nm] = (a, a.shape[1] // 2, a.shape[0] // 2)
    log('sprites new', len(sp_new))
    # ---------------- palette from pooled colours
    pools = []
    def addpool(rgb, wgt):
        flat = rgb.reshape(-1, 3)
        k = min(len(flat), 30000)
        pools.append((flat[rng.choice(len(flat), k, replace=False)], wgt))
    for rgb, mk in art.values(): addpool(rgb[mk] if mk.any() else rgb, 3)
    for v in flats.values(): addpool(v, 3)
    for a, _, _ in sp_new.values():
        px = a[a[..., 3] > 128][:, :3]
        if len(px): addpool(px, 2)
    for nm, d in w.lumps:
        if nm in sp_new or not looks_like_patch(d): continue
        idx, m, _, _ = decode_picture(d)
        if m.any(): addpool(old_pal[idx[m]].astype(np.uint8), 1)
    pts, wts = [], []
    for px, wg in pools:
        for sc, f in ((1.0, 1.0), (.74, .22), (.55, .12)):
            sel = px[rng.random(len(px)) < min(1, wg * f * .35)]
            pts.append((sel * sc)); 
    P = np.concatenate(pts).astype(np.float32)
    log('palette samples', len(P))
    km = MiniBatchKMeans(n_clusters=250, random_state=1, n_init=3, batch_size=8192, max_iter=60).fit(P)
    cen = km.cluster_centers_.clip(0, 255).round().astype(int)
    extra = np.array([[0, 0, 0], [255, 255, 255], [255, 0, 0], [0, 0, 255], [255, 255, 0], [0, 255, 0]])
    pal = np.concatenate([extra, cen])[:256]
    pal = pal.astype(int)
    wq = np.array([1.7, 2.0, 1.4])
    tree = cKDTree(pal * wq)
    def qidx(rgb):
        flat = np.asarray(rgb).reshape(-1, 3).astype(float)
        return tree.query(flat * wq)[1].reshape(np.asarray(rgb).shape[:-1]).astype(np.uint8)
    lut = tree.query(old_pal * wq)[1].astype(np.uint8)
    log('palette done')
    # PLAYPAL
    pals = [pal]
    for k in range(1, 9): a = k * .1; pals.append((pal * (1 - a) + np.array([255, 0, 0]) * a).round())
    for k in range(1, 5): a = k * .125; pals.append((pal * (1 - a) + np.array([215, 186, 69]) * a).round())
    pals.append((pal * .875 + np.array([0, 255, 0]) * .125).round())
    w.set('PLAYPAL', b''.join(np.clip(p, 0, 255).astype(np.uint8).tobytes() for p in pals))
    # COLORMAP (brighter than original: darkest light level still 44%)
    cm = bytearray()
    amb = np.array([60, 80, 140.])
    for i in range(32):
        s = 1 - .56 * (i / 31) ** 1.1
        tgt = pal * s + amb * (1 - s) * .22
        cm += qidx(np.clip(tgt, 0, 255)).tobytes()
    lum = (pal * [.3, .59, .11]).sum(1)
    inv = np.clip(255 - lum, 0, 255)
    cm += qidx(np.stack([inv, inv, inv], 1)).tobytes()
    cm += bytes(256)
    w.set('COLORMAP', bytes(cm))
    # ---------------- re-encode all existing pictures to the new palette
    replaced = set(sp_new)
    nrec = 0
    p_i, p_j = w.index('P_START'), w.index('P_END')
    for li, (nm, d) in enumerate(w.lumps):
        if p_i < li < p_j or nm in replaced or nm in ('PLAYPAL', 'COLORMAP'): continue
        if fi < li < fj: continue
        if looks_like_patch(d):
            idx, m, lo, to = decode_picture(d)
            w.lumps[li][1] = encode_picture(lut[idx], m, lo, to); nrec += 1
    log('re-encoded pictures', nrec)
    # new sprites
    for nm, (a, lo, to) in sp_new.items():
        a = np.asarray(a); mk = a[..., 3] >= 128
        w.set(nm, encode_picture(qidx(a[..., :3]), mk, int(lo), int(to)))
    # flats
    for nm, rgb in flats.items(): w.set(nm, qidx(rgb).tobytes())
    # ---------------- textures: new patch lumps + TEXTURE1/2 + PNAMES
    del_range = [l for l in range(p_i + 1, p_j) if not w.lumps[l][0].endswith(('START', 'END'))]
    for l in reversed(del_range): del w.lumps[l]
    pos = w.index('P_START') + 1
    names = []
    for pname, (rgb, mk) in art.items():
        w.lumps.insert(pos, [pname, encode_picture(qidx(rgb), mk, 0, 0)]); pos += 1; names.append(pname)
    w.set('PNAMES', struct.pack('<i', len(names)) + b''.join(n.encode().ljust(8, b'\0') for n in names))
    pid = {n: i for i, n in enumerate(names)}
    def texlump(rows):
        nn = len(rows); body = bytearray(); offs = []; base = 4 + 4 * nn
        for nm, wd, ht, pname in rows:
            offs.append(base + len(body))
            body += nm.encode()[:8].ljust(8, b'\0') + struct.pack('<ihhih', 0, wd, ht, 0, 1) + struct.pack('<hhhhh', 0, 0, pid[pname], 1, 0)
        return struct.pack('<i', nn) + struct.pack('<%di' % nn, *offs) + bytes(body)
    w.set('TEXTURE1', texlump(texrows[0]))
    if texrows[1]: w.set('TEXTURE2', texlump(texrows[1]))
    w.save(dst)
    log('wrote', dst)

if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
