"""Static SVG pictures of the M-VAVE FM-1 for the course pages.

Everything is drawn at build time, so the pictures show even where the page
runs without JavaScript (a phone's file preview). Elements carry data-k
(a key) and data-i (a note's index) so the page's player can light them.
"""
import html
import re

WHITES = ['F3', 'G3', 'A3', 'B3', 'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F5', 'G5']
# black key, the white key on its left, the label printed on the FM-1 under it
BLACKS = [('F#3', 0, 'OP1'), ('G#3', 1, 'OP2'), ('A#3', 2, 'OP3'), ('C#4', 4, 'OP4'), ('D#4', 5, 'OP5'),
          ('F#4', 7, 'OP6'), ('G#4', 8, 'PIT'), ('A#4', 9, 'GLO'), ('C#5', 11, 'MONO'), ('D#5', 12, 'POLY'),
          ('F#5', 14, '')]
SYL = {'C': 'до', 'D': 'ре', 'E': 'ми', 'F': 'фа', 'G': 'соль', 'A': 'ля', 'B': 'си'}


def letter_syl(k):
    """'E4' -> 'E/ми', 'F#4' -> 'F#/фа♯': the letter first, the syllable after it."""
    sharp = '#' in k
    return '%s%s/%s%s' % (k[0], '#' if sharp else '', SYL[k[0]], '♯' if sharp else '')
BASE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
LETTERS = 'CDEFGAB'
SCALES = {
    'MAJ': [0, 2, 4, 5, 7, 9, 11], 'MIN': [0, 2, 3, 5, 7, 8, 10], 'DOR': [0, 2, 3, 5, 7, 9, 10],
    'PHRY': [0, 1, 3, 5, 7, 8, 10], 'LYD': [0, 2, 4, 6, 7, 9, 11], 'MIX': [0, 2, 4, 5, 7, 9, 10],
    'HARM': [0, 2, 3, 5, 7, 8, 11], 'MPEN': [0, 3, 5, 7, 10], 'PEN': [0, 2, 4, 7, 9],
}
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

KW = 36                     # white key pitch in the keyboard picture
DRUM_SHORT = ['KICK', 'KCK2', 'SNR', 'CLAP', 'HAT', 'OHAT', 'PHAT', 'RIM', 'SNR2', 'LTOM', 'HTOM', 'CRSH', 'RIDE', 'SHKR', 'CONG', 'BELL']
DRUM_RU = ['бочка', 'боч.2', 'малый', 'хлоп', 'хэт', 'откр', 'пед.', 'рим', 'мал.2', 'том↓', 'том↑', 'крэш', 'райд', 'шейк', 'конга', 'ковб.']


def esc(s):
    return html.escape(str(s), quote=True)


def key_no(name):
    return WHITES.index(name) + 1 if name in WHITES else None


def black_label(name):
    for b, _, lab in BLACKS:
        if b == name:
            return lab
    return ''


def midi(name):
    m = re.fullmatch(r'([A-G])(#?)(\d)', name)
    return 12 * (int(m.group(3)) + 1) + BASE[m.group(1)] + (1 if m.group(2) else 0)


def white_midi(name, scale='MAJ'):
    """A white key in KEYS = WHITE, KEY C: the scale degree it walks to (C4 = the root)."""
    if scale == 'MAJ':
        return midi(name)
    sc = SCALES[scale]
    idx = LETTERS.index(name[0]) + 7 * (int(name[1]) - 4)
    octv, deg = divmod(idx, len(sc))
    return 60 + 12 * octv + sc[deg]


def chord_keys(root, scale='MAJ', kind='TRIAD'):
    """The notes (midi) SLOOP's chord mode plays on a white key, and their names."""
    sc = SCALES[scale]
    idx = LETTERS.index(root[0]) + 7 * (int(root[1]) - 4)
    steps = {'TRIAD': [0, 2, 4], '7TH': [0, 2, 4, 6], 'SUS4': [0, 3, 4], 'POWER': [0, 4, 7]}[kind]
    out = []
    for s in steps:
        octv, deg = divmod(idx + s, len(sc))
        out.append(60 + 12 * octv + sc[deg])
    return out


FLAT_NAMES = ['C', 'D♭', 'D', 'E♭', 'E', 'F', 'G♭', 'G', 'A♭', 'A', 'B♭', 'B']


def midi_name(m):
    return '%s%d' % (NOTE_NAMES[m % 12], m // 12 - 1)


# ---------------------------------------------------------------- keyboard
def pill(cx, cy, label):
    """A white badge that grows with its label (1, IV, 4↓, до…)."""
    w = max(24, 8 * len(str(label)) + 10)
    return ('<rect class="badge" x="%.1f" y="%d" width="%d" height="24" rx="12"/>'
            '<text class="bt" x="%d" y="%d">%s</text>' % (cx - w / 2, cy - 12, w, cx, cy + 5, esc(label)))


def key_x(name):
    """The centre of a key in the keyboard picture."""
    if name in WHITES:
        return 4 + KW * WHITES.index(name) + KW // 2
    for b, left, _ in BLACKS:
        if b == name:
            return 4 + KW * (left + 1)
    raise ValueError('no key %s' % name)


def keyboard(hl=None, ghost=(), mode='notes', steps_lit=(), caption=None, play_keys=False, marks=()):
    """The FM-1 keyboard: 11 black keys over 16 white ones, as on the device.

    hl: {key name: label} keys to press (label shown in a badge; '' = no badge)
    ghost: key names that sound too (outlined), e.g. the notes of a chord
    mode 'steps': the white keys are steps 1-16 (the SEQ layer), steps_lit lit
    """
    hl = hl or {}
    W = KW * 16 + 8
    H = 214
    rows = {}                       # mark rows: brackets under the keys, a new row when they would overlap
    placed = []
    for a, b, lab in marks:
        x1, x2 = sorted((key_x(a), key_x(b)))
        half = 3.6 * len(lab) + 6         # the label is often wider than its bracket
        mid = (x1 + x2) / 2
        e1, e2 = min(x1 - 10, mid - half), max(x2 + 10, mid + half)
        r = 0
        while any(rr == r and e1 < px2 and e2 > px1 for rr, px1, px2 in placed):
            r += 1
        placed.append((r, e1, e2))
        rows.setdefault(r, []).append((x1, x2, lab))
    if mode == 'steps':
        H = 186                     # no note names under the keys
    base = H + 8
    if rows:
        H += 8 + 30 * len(rows)
    p = ['<svg class="fm1 kbd%s" viewBox="0 0 %d %d" role="img" aria-label="%s">' % (
        ' playable' if play_keys else '', W, H, esc(caption or 'Клавиатура FM-1'))]
    p.append('<rect class="dev" x="0" y="0" width="%d" height="%d" rx="18"/>' % (W, H))
    # black row
    for name, left, lab in BLACKS:
        cx = 4 + KW * (left + 1)
        cls = 'key blk'
        if name in hl:
            cls += ' on'
        elif name in ghost:
            cls += ' ghost'
        p.append('<g class="%s" data-k="%s"><rect x="%d" y="10" width="%d" height="70" rx="15"/>'
                 '<rect class="slot" x="%d" y="22" width="4" height="26" rx="2"/>'
                 '<text class="lab" x="%d" y="70">%s</text>' % (cls, name, cx - 15, 30, cx - 2, cx, esc(lab)))
        if name in hl and hl[name]:
            p.append(pill(cx, 36, hl[name]))
        p.append('</g>')
    # white row
    for i, name in enumerate(WHITES):
        x = 4 + KW * i
        cx = x + KW // 2
        n = i + 1
        notes_like = mode in ('notes', 'drums')
        lit = (mode == 'steps' and n in steps_lit) or (notes_like and name in hl)
        cls = 'key wht'
        if lit:
            cls += ' on'
        elif notes_like and name in ghost:
            cls += ' ghost'
        if n in (1, 5, 9, 13):
            cls += ' mark'
        p.append('<g class="%s" data-k="%s" data-n="%d"><rect x="%d" y="90" width="%d" height="84" rx="15"/>'
                 '<rect class="slot" x="%d" y="104" width="4" height="40" rx="2"/>' % (cls, name, n, x + 2, KW - 4, cx - 2))
        badge = None
        if notes_like and name in hl and hl[name]:
            badge = hl[name]
        if badge:
            p.append(pill(cx, 124, badge))
        p.append('<text class="num" x="%d" y="166">%d</text></g>' % (cx, n))
        if mode == 'drums':
            p.append('<text class="nm dr" x="%d" y="196">%s</text>' % (cx, DRUM_SHORT[i]))
            p.append('<text class="syl dr" x="%d" y="209">%s</text>' % (cx, DRUM_RU[i]))
        elif mode == 'notes':
            p.append('<text class="nm" x="%d" y="196">%s</text>' % (cx, name))
            p.append('<text class="syl" x="%d" y="209">%s</text>' % (cx, SYL[name[0]]))

    for r, items in rows.items():
        y = base + 30 * r
        for x1, x2, lab in items:
            if x1 == x2:
                x1, x2 = x1 - 10, x2 + 10
            p.append('<path class="mk" d="M%d %d v-7 H%d v7"/>' % (x1, y, x2))
            p.append('<text class="mt" x="%d" y="%d">%s</text>' % ((x1 + x2) / 2, y + 17, esc(lab)))
    p.append('</svg>')
    out = ''.join(p)
    if caption:
        out = '<figure class="pic">%s<figcaption>%s</figcaption></figure>' % (out, caption)
    else:
        out = '<figure class="pic">%s</figure>' % out
    return out


# ---------------------------------------------------------------- panel
PANEL = {
    # name: (kind, cx, cy, label)
    'MASTER': ('knob', 52, 58, 'MASTER'), 'SELECT': ('knob', 136, 58, 'SELECT'),
    'PRESETS': ('knob', 52, 150, 'PRESETS'), 'ALGORITHM': ('knob', 136, 150, 'ALGORITHM'),
    'OCT-': ('btn', 52, 222, 'OCT−'), 'OCT+': ('btn', 128, 222, 'OCT+'),
    'KNOB1': ('knob', 402, 58, 'KNOB1'), 'KNOB2': ('knob', 470, 58, 'KNOB2'),
    'KNOB3': ('knob', 538, 58, 'KNOB3'), 'KNOB4': ('knob', 606, 58, 'KNOB4'),
}
for _i, _n in enumerate(['FX', 'SEL', 'ENV', 'LFO', 'EDIT', 'GLO']):
    PANEL[_n] = ('btn', 392 + _i * 45, 142, _n)
for _i, _n in enumerate(['HOME', 'SAVE', 'ARP', 'SEQ', 'PLAY', 'REC']):
    PANEL[_n] = ('btn', 392 + _i * 45, 196, 'PLAY/STOP' if _n == 'PLAY' else _n)


def panel(hl=None, caption=None, screen=None):
    """The top of the FM-1: knobs, screen and buttons, the asked ones lit and numbered."""
    hl = hl or {}
    W, H = 650, 250
    p = ['<svg class="fm1 panel" viewBox="0 0 %d %d" role="img" aria-label="%s">' % (W, H, esc(caption or 'Панель FM-1'))]
    p.append('<rect class="dev" x="0" y="0" width="%d" height="%d" rx="20"/>' % (W, H))
    # screen
    p.append('<rect class="scr" x="196" y="20" width="160" height="150" rx="14"/>')
    lines = screen or ['SLOOP']
    for i, t in enumerate(lines[:6]):
        p.append('<text class="st" x="208" y="%d">%s</text>' % (44 + i * 22, esc(t)))
    p.append('<rect class="pad" x="368" y="112" width="276" height="122" rx="14"/>')
    for name, (kind, cx, cy, lab) in PANEL.items():
        on = name in hl
        cls = 'ctl %s%s' % (kind, ' on' if on else '')
        if kind == 'knob':
            p.append('<g class="%s"><circle cx="%d" cy="%d" r="19"/><line x1="%d" y1="%d" x2="%d" y2="%d"/>'
                     '<text class="cl" x="%d" y="%d">%s</text></g>' % (cls, cx, cy, cx, cy - 6, cx, cy - 17,
                                                                        cx, cy - 27 if name.startswith('KNOB') or name in ('MASTER', 'SELECT') else cy - 27, esc(lab)))
        else:
            w = 40 if name not in ('OCT-', 'OCT+') else 62
            h = 40 if name not in ('OCT-', 'OCT+') else 30
            fs = ' small' if len(lab) > 4 else ''
            p.append('<g class="%s"><rect x="%d" y="%d" width="%d" height="%d" rx="9"/>'
                     '<text class="bl%s" x="%d" y="%d">%s</text></g>' % (cls, cx - w // 2, cy - h // 2, w, h, fs, cx, cy + 4,
                                                                         esc('PLAY' if name == 'PLAY' else lab)))
    for name, (kind, cx, cy, lab) in PANEL.items():   # badges last: nothing may cover them
        if name in hl and hl[name]:
            lab = str(hl[name])
            half = max(24, 8 * len(lab) + 10) // 2
            if kind == 'knob':
                bx, by = cx, cy + 32
            else:
                bx, by = cx + max(10, half - 14), cy - 22
            bx = min(bx, W - half - 2)
            p.append(pill(bx, by, lab))
    p.append('</svg>')
    return '<figure class="pic">%s%s</figure>' % (''.join(p), '<figcaption>%s</figcaption>' % caption if caption else '')


# ---------------------------------------------------------------- notes / staff
def parse_notes_ex(text):
    """'E4 E4 F4 G4 | G4- E4. D4/ C4*3 G3*4~ r' -> [(key or None, beats, slide)], bar lines ignored.

    '-' adds a beat, '/' halves, '.' adds half (dotted), '*N' is N sixteenth steps,
    '~' slides into the next note (the 808 glide), 'r' is a rest."""
    out = []
    for tok in text.split():
        if tok == '|':
            continue
        m = re.fullmatch(r'([A-G]#?\d|r)(?:\*(\d+))?(-*)(/?)(\.?)(~?)', tok)
        if not m:
            raise ValueError('bad note token %r' % tok)
        if m.group(2):
            beats = int(m.group(2)) / 4
        else:
            beats = 1 + len(m.group(3))
            if m.group(4):
                beats = 0.5
            if m.group(5):
                beats *= 1.5
        out.append((None if m.group(1) == 'r' else m.group(1), beats, bool(m.group(6))))
    return out


def parse_notes(text):
    return [(k, b) for k, b, _ in parse_notes_ex(text)]


def staff(notes, per_line=2, first_index=0):
    """Treble staff (no clef drawn: C4 sits on the first ledger line), 4/4, bars of 4 beats.
    Under each note: the FM-1 key number and the syllable."""
    LS = 12                  # line spacing
    bars, cur, acc = [], [], 0
    for i, (k, b) in enumerate(notes):
        cur.append((i + first_index, k, b))
        acc += b
        if acc >= 4 - 1e-9:
            bars.append(cur)
            cur, acc = [], 0
    if cur:
        bars.append(cur)
    systems = [bars[i:i + per_line] for i in range(0, len(bars), per_line)]
    out = []
    for si, sysb in enumerate(systems):
        unit = 30
        width = 46 + sum(sum(max(unit * b, 24) for _, _, b in bar) + 14 for bar in sysb) + 6
        top = 34
        bottom = top + 4 * LS        # E4 line
        steps_here = [LETTERS.index(k[0]) + 7 * (int(k[-1]) - 4) for bar in sysb for _, k, _ in bar if k]
        low = min(steps_here + [2])
        # a low note (and its stem going down) must not reach the key numbers
        drop = max(0, int((2 - low) * LS / 2) + (36 if low >= 6 else 0) - 14) if low < 2 else 0
        nums = bottom + 40 + drop
        H = nums + 38
        p = ['<svg class="staff" viewBox="0 0 %d %d" role="img" aria-label="Ноты">' % (width, H)]
        for li in range(5):
            y = top + li * LS
            p.append('<line class="sl" x1="4" y1="%d" x2="%d" y2="%d"/>' % (y, width - 4, y))
        if si == 0:
            p.append('<text class="ts" x="22" y="%d">4</text><text class="ts" x="22" y="%d">4</text>' % (top + LS * 2 - 3, top + LS * 4 - 3))
        x = 46
        row_end, rows_used = [-99, -99], 1        # letter/syllable labels: a second row where they would touch
        for bar in sysb:
            for idx, k, b in bar:
                adv = max(unit * b, 24)
                hx = x + 9
                if k is None:
                    p.append('<rect class="rest" data-i="%d" x="%d" y="%d" width="10" height="16" rx="2"/>' % (idx, hx - 5, top + LS))
                    x += adv
                    continue
                step = LETTERS.index(k[0]) + 7 * (int(k[-1]) - 4)   # 0 = C4
                y = bottom - (step - 2) * LS / 2
                # ledger lines
                if step <= 0:
                    for s in range(0, step - 1, -2):
                        ly = bottom - (s - 2) * LS / 2
                        p.append('<line class="sl" x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (hx - 11, ly, hx + 11, ly))
                if step >= 12:
                    for s in range(12, step + 1, 2):
                        ly = bottom - (s - 2) * LS / 2
                        p.append('<line class="sl" x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (hx - 11, ly, hx + 11, ly))
                hollow = b >= 2
                p.append('<g class="nt" data-i="%d">' % idx)
                p.append('<ellipse class="%s" cx="%d" cy="%.1f" rx="7" ry="5.2" transform="rotate(-20 %d %.1f)"/>' % (
                    'hh' if hollow else 'hf', hx, y, hx, y))
                if b < 4:
                    if step < 6:
                        p.append('<line class="stem" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (hx + 6.3, y - 2, hx + 6.3, y - 36))
                        if b in (0.25, 0.5, 0.75):
                            p.append('<path class="flag" d="M%.1f %.1f q 10 8 8 20"/>' % (hx + 6.3, y - 36))
                        if b == 0.25:
                            p.append('<path class="flag" d="M%.1f %.1f q 10 8 8 20"/>' % (hx + 6.3, y - 28))
                    else:
                        p.append('<line class="stem" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (hx - 6.3, y + 2, hx - 6.3, y + 36))
                        if b in (0.25, 0.5, 0.75):
                            p.append('<path class="flag" d="M%.1f %.1f q 10 -8 8 -20"/>' % (hx - 6.3, y + 36))
                        if b == 0.25:
                            p.append('<path class="flag" d="M%.1f %.1f q 10 -8 8 -20"/>' % (hx - 6.3, y + 28))
                if b in (1.5, 3, 0.75):
                    p.append('<circle class="dot" cx="%d" cy="%.1f" r="2.2"/>' % (hx + 12, y - (3 if step % 2 == 0 else 0)))
                p.append('</g>')
                if key_no(k):
                    p.append('<text class="kn" data-i="%d" x="%d" y="%d">%d</text>' % (idx, hx, nums, key_no(k)))
                lab = letter_syl(k)
                half = 3.3 * len(lab)                       # 11px text: about 6.6px a character
                row = 0 if hx - half >= row_end[0] + 3 else (1 if hx - half >= row_end[1] + 3 else 0)
                row_end[row] = hx + half
                rows_used = max(rows_used, row + 1)
                p.append('<text class="sy" x="%d" y="%d">%s</text>' % (hx, nums + 16 + 13 * row, lab))
                x += adv
            x += 4
            p.append('<line class="bar" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (x, top, x, bottom))
            x += 10
        p.append('<text class="lg" x="4" y="%d">клавиша</text>' % nums)
        p.append('</svg>')
        svg = ''.join(p)
        if rows_used > 1:
            svg = svg.replace('viewBox="0 0 %d %d"' % (width, H), 'viewBox="0 0 %d %d"' % (width, H + 13), 1)
        out.append(svg)
    return '<div class="staff-wrap">%s</div>' % ''.join(out)


def chips(notes, scale='MAJ'):
    """Big note cards: key number on top, note name under, grouped in bars."""
    out, acc, bar = [], 0, []
    for i, (k, b) in enumerate(notes):
        if k is None:
            bar.append('<span class="chip rest" data-i="%d" style="--w:%s">пауза</span>' % (i, b))
        else:
            sub = letter_syl(k) if scale == 'MAJ' else k
            bar.append('<span class="chip" data-i="%d" style="--w:%s"><b>%s</b><i>%s</i></span>' % (
                i, b, key_no(k) or esc(black_label(k) or k), esc(sub)))
        acc += b
        if acc >= 4 - 1e-9:
            out.append('<span class="cbar">%s</span>' % ''.join(bar))
            bar, acc = [], 0
    if bar:
        out.append('<span class="cbar">%s</span>' % ''.join(bar))
    return '<div class="chips">%s</div>' % ''.join(out)


def grid_spb(notes):
    """The coarsest SLOOP step that holds every note: 1 (DIV 1/4), 2 (1/8) or 4 (1/16)."""
    for spb in (1, 2, 4):
        if all(abs(b * spb - round(b * spb)) < 1e-9 for _, b in notes):
            return spb
    return 4


def steps_table(notes, spb=4):
    """The melody as SLOOP steps: a note, then TIE for the rest of its length."""
    cells = []
    for i, (k, b) in enumerate(notes):
        n = int(round(b * spb))
        if k is None:
            cells += [('.', None)] * n
        else:
            cells += [(k, i)] + [('-', i)] * (n - 1)
    row = 16                              # 1/16: a bar a row · 1/8: two bars · 1/4: four bars
    while len(cells) % row:
        cells.append(('.', None))
    total = len(cells)
    rows = []
    for bi in range(0, len(cells), row):
        tds = []
        for j, (c, i) in enumerate(cells[bi:bi + row]):
            cls = 'm' + (' gs' if j % (8 if spb == 2 else 4) == 0 else '') + (' note' if c not in '.-' else ' tie' if c == '-' else ' rest')
            tds.append('<td class="%s"%s>%s</td>' % (cls, ' data-i="%d"' % i if i is not None else '', esc(c if c not in '.-' else '')))
        lab = 'такт %d' % (bi // 16 + 1) if spb == 4 else 'шаги %d–%d' % (bi + 1, bi + row)
        if spb == 2:
            lab = 'такты %d–%d' % (bi // 8 + 1, bi // 8 + 2)
        elif spb == 1:
            lab = 'такты %d–%d' % (bi // 4 + 1, bi // 4 + 4)
        rows.append('<tr><th class="lab">%s</th>%s</tr>' % (lab, ''.join(tds)))
    if spb == 4:
        head = ''.join('<th class="h%s%s">%s</th>' % (' gs' if j % 4 == 0 else '', ' beat' if j % 4 == 0 else '', 'e+a'[j % 4 - 1] if j % 4 else j // 4 + 1) for j in range(16))
    elif spb == 2:
        head = ''.join('<th class="h%s%s">%s</th>' % (' gs' if j % 8 == 0 else '', '' if j % 2 else ' beat', '+' if j % 2 else j % 8 // 2 + 1) for j in range(16))
    else:
        head = ''.join('<th class="h%s beat">%d</th>' % (' gs' if j % 4 == 0 else '', j % 4 + 1) for j in range(16))
    return ('<div class="grid-scroll"><table class="grid mel"><thead><tr><th class="lab"></th>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>' % (head, ''.join(rows)), total)
