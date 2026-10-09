#!/usr/bin/env python3
"""Build sloop-book.html: the whole book as one self-contained page.

Usage: python3 tools/build_html.py [book_dir] [out_file]

Markdown is converted by a small converter that knows exactly what the book
uses (headings, paragraphs, lists, tables, quotes, code blocks). Drum and
melody grids in code blocks become coloured tables that can be played in the
browser (a simple Web Audio synth, not the FM-1 sound).
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fm1_svg as F  # noqa: E402

ORDER = [
    ('README.md', 'Начало', 'Обложка и оглавление'),
    ('kurs-00-znakomstvo.md', 'Курс с нуля', '0. Знакомство с FM-1'),
    ('kurs-01-tri-noty.md', 'Курс с нуля', '1. Три ступеньки'),
    ('kurs-02-oda.md', 'Курс с нуля', '2. Пять пальцев: «Ода к радости»'),
    ('kurs-03-bratec-yakov.md', 'Курс с нуля', '3. Восьмые: «Братец Яков»'),
    ('kurs-04-zapis.md', 'Курс с нуля', '4. Записываем мелодию'),
    ('kurs-05-pervyj-bit.md', 'Курс с нуля', '5. Первый бит'),
    ('kurs-06-bit-ozhivaet.md', 'Курс с нуля', '6. Бит оживает'),
    ('kurs-07-mazhor-minor.md', 'Курс с нуля', '7. Мажор и минор'),
    ('kurs-08-akkordy.md', 'Курс с нуля', '8. Аккорды одним пальцем'),
    ('kurs-09-bas.md', 'Курс с нуля', '9. Бас'),
    ('kurs-10-pervyj-lup.md', 'Курс с нуля', '10. Первая песня-луп'),
    ('kurs-11-chernye-klavishi.md', 'Курс с нуля', '11. Чёрные клавиши-волшебники'),
    ('kurs-12-pesnya.md', 'Курс с нуля', '12. Из лупа — песня'),
    ('kurs-13-dalshe.md', 'Курс с нуля', '13. Дальше — сам'),
    ('shkola-1-ritm-i-udarnye.md', 'Школа', 'Ритм и ударные'),
    ('shkola-2-noty-lady-akkordy.md', 'Школа', 'Ноты, лады, аккорды'),
    ('shkola-3-bas-melodiya-forma.md', 'Школа', 'Бас, мелодия, форма'),
    ('01-kak-chitat-i-vvodit.md', 'Справочник', '1. Как читать и вводить'),
    ('02-udarnye.md', 'Справочник', '2. Ударные'),
    ('03-breyki-i-perehody.md', 'Справочник', '3. Брейки и переходы'),
    ('04-akkordy.md', 'Справочник', '4. Аккорды'),
    ('05-basy.md', 'Справочник', '5. Басы'),
    ('06-melodii.md', 'Справочник', '6. Мелодии'),
    ('07-retsepty.md', 'Справочник', '7. Рецепты треков'),
    ('08-protiv-odinakovosti.md', 'Справочник', '8. Против одинаковости'),
]

SCALES = {
    'MAJ': [0, 2, 4, 5, 7, 9, 11], 'MIN': [0, 2, 3, 5, 7, 8, 10],
    'DOR': [0, 2, 3, 5, 7, 9, 10], 'PHRY': [0, 1, 3, 5, 7, 8, 10],
    'LYD': [0, 2, 4, 6, 7, 9, 11], 'MIX': [0, 2, 4, 5, 7, 9, 10],
    'LOC': [0, 1, 3, 5, 6, 8, 10], 'HARM': [0, 2, 3, 5, 7, 8, 11],
    'MEL': [0, 2, 3, 5, 7, 9, 11], 'PEN': [0, 2, 4, 7, 9],
    'MPEN': [0, 3, 5, 7, 10], 'BLUES': [0, 3, 5, 6, 7, 10],
}
WHITE = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
LANES = {1: 'KICK', 2: 'KICK 2', 3: 'SNARE', 4: 'CLAP', 5: 'HAT', 6: 'OPEN HAT', 7: 'PEDAL HAT', 8: 'RIM',
         9: 'SNARE 2', 10: 'LOW TOM', 11: 'HI TOM', 12: 'CRASH', 13: 'RIDE', 14: 'SHAKER', 15: 'CONGA', 16: 'COWBELL'}


def slug(h):
    h = h.strip().lower()
    h = re.sub(r'[^\w\- ]', '', h, flags=re.U)
    return h.replace(' ', '-')


def pref(fn):
    return re.sub(r'[^a-z0-9-]', '', fn[:-3].lower())


class Book:
    def __init__(self, root):
        self.root = root
        self.patterns = []

    # ------------------------------------------------------------ inline
    def link(self, target, cur):
        if re.match(r'^[a-z]+://', target):
            return target, True
        fn, _, an = target.partition('#')
        fn = fn or cur
        if not an:
            return '#ch-' + pref(fn), False
        return '#' + pref(fn) + '--' + an, False

    def inline(self, s, cur):
        codes = []

        def keep(m):
            codes.append('<code>' + html.escape(m.group(1), quote=False) + '</code>')
            return '\x00%d\x00' % (len(codes) - 1)

        s = re.sub(r'`([^`]+)`', keep, s)
        s = html.escape(s, quote=False)

        def lk(m):
            href, ext = self.link(m.group(2), cur)
            extra = ' target="_blank" rel="noopener"' if ext else ''
            return '<a href="%s"%s>%s</a>' % (html.escape(href), extra, m.group(1))

        s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lk, s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<![\*\w])\*(?=\S)(.+?)(?<=\S)\*(?![\*\w])', r'<em>\1</em>', s)
        return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m.group(1))], s)

    # ------------------------------------------------------------ blocks
    def convert(self, fn):
        lines = open(os.path.join(self.root, fn), encoding='utf-8').read().split('\n')
        out, toc, used = [], [], {}
        ctx = []                       # paragraph text since the last heading
        i = 0
        while i < len(lines):
            l = lines[i]
            if l.startswith('```'):
                lang = l[3:].strip()
                j = i + 1
                while j < len(lines) and not lines[j].startswith('```'):
                    j += 1
                if lang:
                    out.append(self.fm1_block(lang, lines[i + 1:j], fn))
                else:
                    out.append(self.code(lines[i + 1:j], ' '.join(ctx), fn))
                i = j + 1
                continue
            m = re.match(r'^(#{1,6}) (.*)$', l)
            if m:
                lvl, text = len(m.group(1)), m.group(2).strip()
                s = slug(text)
                if s in used:
                    used[s] += 1
                    s = '%s-%d' % (s, used[s])
                else:
                    used[s] = 0
                hid = pref(fn) + '--' + s
                out.append('<h%d id="%s">%s</h%d>' % (lvl, hid, self.inline(text, fn), lvl))
                if lvl in (2, 3):
                    toc.append((lvl, hid, re.sub(r'[`*]', '', text)))
                if lvl <= 3:
                    ctx = []
                i += 1
                continue
            if re.match(r'^-{3,}\s*$', l):
                out.append('<hr>')
                i += 1
                continue
            if l.startswith('|') and i + 1 < len(lines) and re.match(r'^\|\s*:?-{3}', lines[i + 1]):
                j = i
                rows = []
                while j < len(lines) and lines[j].startswith('|'):
                    rows.append(lines[j])
                    j += 1
                out.append(self.table(rows, fn))
                i = j
                continue
            if l.startswith('>'):
                j = i
                buf = []
                while j < len(lines) and lines[j].startswith('>'):
                    buf.append(lines[j][1:].strip())
                    j += 1
                paras = [p for p in ' \n'.join(buf).split(' \n \n')]
                body = ''.join('<p>%s</p>' % self.inline(p.replace(' \n', ' '), fn) for p in paras if p.strip())
                out.append('<blockquote>%s</blockquote>' % body)
                i = j
                continue
            if re.match(r'^(- |\d+\. )', l):
                ordered = bool(re.match(r'^\d+\. ', l))
                pat = r'^\d+\. ' if ordered else r'^- '
                items = []
                j = i
                while j < len(lines) and (re.match(pat, lines[j]) or (lines[j].startswith('   ') and items)):
                    if re.match(pat, lines[j]):
                        items.append(re.sub(pat, '', lines[j]))
                    else:
                        items[-1] += ' ' + lines[j].strip()
                    j += 1
                tag = 'ol' if ordered else 'ul'
                start = ''
                if ordered:
                    n = int(re.match(r'^(\d+)', l).group(1))
                    if n != 1:
                        start = ' start="%d"' % n
                out.append('<%s%s>%s</%s>' % (tag, start, ''.join('<li>%s</li>' % self.inline(t, fn) for t in items), tag))
                ctx.extend(items)
                i = j
                continue
            if l.strip() == '[[done]]':
                out.append('<label class="done"><input type="checkbox" data-lesson="%s"> '
                           '<span>Урок пройден</span></label>' % pref(fn))
                i += 1
                continue
            if not l.strip():
                i += 1
                continue
            j = i
            buf = []
            while j < len(lines) and lines[j].strip() and not re.match(r'^(#{1,6} |```|\||>|- |\d+\. |-{3,}\s*$)', lines[j]):
                buf.append(lines[j].strip())
                j += 1
            if not buf:                 # a line no rule took: keep it as a paragraph
                buf, j = [l.strip()], i + 1
            text = ' '.join(buf)
            if re.fullmatch(r'(\[[^\]]+\]\([^)\s]+\)\s*·?\s*)+', text):
                i = j                   # the chapter's own prev / next links: the page has a pager
                continue
            ctx.append(text)
            out.append('<p>%s</p>' % self.inline(text, fn))
            i = j
        h2 = [t for t in toc if t[0] == 2]
        toc = [t[1:] for t in (toc if len(h2) < 5 else h2)]   # few sections: list the parts inside them too
        return '\n'.join(out), toc

    # ------------------------------------------------------------ course blocks
    @staticmethod
    def opts(lines):
        o = {}
        for l in lines:
            if '=' in l:
                k, _, v = l.partition('=')
                o[k.strip()] = v.strip()
        return o

    @staticmethod
    def pairs(text):
        """'C4:1 D4 E4:до' -> {'C4': '1', 'D4': '', 'E4': 'до'}"""
        out = {}
        for tok in text.split():
            k, _, v = tok.partition(':')
            out[k] = v.replace('_', ' ')
        return out

    def play_bar(self, pid, meta, extra=''):
        return ('<div class="grid-bar"><button class="play" data-pid="%d" aria-label="Слушать">'
                '<span class="ico">▶</span><span class="txt">Слушать</span></button>'
                '<span class="meta">%s</span>%s</div>' % (pid, html.escape(meta), extra))

    def fm1_block(self, lang, lines, fn):
        o = self.opts(lines)
        cap = self.inline(o['caption'], fn) if o.get('caption') else None
        if lang == 'panel':
            scr = o['screen'].split(';') if o.get('screen') else None
            return F.panel(self.pairs(o.get('hl', '')), cap, scr)
        if lang == 'keys':
            mode = o.get('mode', 'notes')
            lit = [int(x) for x in o.get('steps', '').split()]
            return F.keyboard(self.pairs(o.get('hl', '')), o.get('ghost', '').split(), mode, lit, cap,
                              play_keys=True)
        if lang == 'song':
            return self.song(o, fn)
        if lang == 'chords':
            return self.chords(o, fn)
        if lang == 'loop':
            return self.loop(o, fn)
        raise ValueError('unknown block %s in %s' % (lang, fn))

    def song_events(self, notes, scale, voice, t0=0.0):
        ev, t = [], t0
        for i, (k, b) in enumerate(notes):
            if k is not None:
                m = F.white_midi(k, scale) if '#' not in k else F.midi(k)
                if voice == 'bass':
                    m -= 24
                ev.append([t, b, m, voice, [k], i])
            t += b
        return ev, t - t0

    def song(self, o, fn):
        notes = F.parse_notes(o['notes'])
        scale = o.get('scale', 'MAJ')
        voice = o.get('voice', 'lead')
        bpm = int(o.get('bpm', 90))
        ev, beats = self.song_events(notes, scale, voice)
        beats = -(-beats // 4) * 4
        pid = len(self.patterns)
        self.patterns.append({'type': 'ev', 'bpm': bpm, 'beats': beats, 'ev': ev, 'dr': []})
        meta = '%d BPM' % bpm + ('' if scale == 'MAJ' else ' · лад %s (KEYS = WHITE)' % scale)
        title = '<div class="ctitle">%s</div>' % self.inline(o['title'], fn) if o.get('title') else ''
        used = {k: '' for k, _ in notes if k}
        body = []
        if scale == 'MAJ' and o.get('staff', 'yes') == 'yes':
            body.append(F.staff(notes))
        else:
            body.append(F.chips(notes, scale))
        body.append(F.keyboard(used, (), 'notes', (), None))
        if o.get('steps', 'yes') == 'yes':
            spb = {'1/4': 1, '1/8': 2, '1/16': 4}.get(o.get('div')) or F.grid_spb(notes)
            tbl, n = F.steps_table(notes, spb)
            div = {1: '1/4', 2: '1/8', 4: '1/16'}[spb]
            label = 'Как ввести по шагам: DIV %s, LEN %d' % (div, n)
            warn = ''
            if n > 64:
                warn = ('<p class="cnote">В SLOOP не больше 64 шагов на трек: введи первую половину (LEN 64), '
                        'сохрани секцию (SAVE + клавиша 5), потом вторую половину — в другую секцию (SAVE + 6).</p>')
            body.append('<details class="steps"><summary>%s</summary>%s%s</details>' % (label, tbl, warn))
        note = '<p class="cnote">%s</p>' % self.inline(o['note'], fn) if o.get('note') else ''
        return '<figure class="course" data-pid="%d">%s%s%s%s</figure>' % (
            pid, title, self.play_bar(pid, meta), ''.join(body), note)

    @staticmethod
    def chord_of(tok, scale, kind):
        root, *mods = tok.split('+')
        ms = F.chord_keys(root, scale, kind)
        if 'F#' in mods:                  # CHORD+ F#: major <-> minor
            third = ms[1] - ms[0]
            if third in (3, 4):
                ms[1] = ms[0] + (7 - third)
        if 'G#' in mods and kind == 'TRIAD':
            sc = F.SCALES[scale]
            idx = F.LETTERS.index(root[0]) + 7 * (int(root[1]) - 4) + 6
            octv, deg = divmod(idx, len(sc))
            ms.append(60 + 12 * octv + sc[deg])
        third = ms[1] - ms[0]
        fifth = ms[2] - ms[0]
        q = '' if third == 4 else ('°' if fifth == 6 else 'm') if third == 3 else 'sus4' if third == 5 else ''
        if kind == 'POWER':
            q = '5'
        name = F.NOTE_NAMES[ms[0] % 12] + q + ('7' if len(ms) > 3 else '')
        deg = F.LETTERS.index(root[0]) % 7
        rom = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][deg]
        if q in ('m', '°'):
            rom = rom.lower() + ('°' if q == '°' else '')
        if len(ms) > 3:
            rom += '7'
        return root, mods, ms, name, rom

    def chords(self, o, fn):
        scale = o.get('scale', 'MAJ')
        kind = o.get('kind', 'TRIAD')
        bpm = int(o.get('bpm', 80))
        bars = o['bars'].split()
        ev, cards, hl, ghost = [], [], {}, set()
        for i, tok in enumerate(bars):
            root, mods, ms, name, rom = self.chord_of(tok, scale, kind)
            names = [F.midi_name(m) for m in ms]
            ev.append([i * 4, 4, ms, 'pad', names, i])
            hl.setdefault(root, str(i + 1) if root not in hl else hl[root] + ',' + str(i + 1))
            for m in mods:
                if m in ('F#', 'G#', 'A#', 'C#', 'D#'):
                    hl.setdefault(m + '4', '')
            ghost.update(n for n in names if n != root)
            extra = ''.join('<em>+%s</em>' % html.escape(m) for m in mods)
            cards.append('<span class="ccard" data-i="%d"><small>%d</small><b>%s%s</b><span>%s</span><i>%s</i></span>' % (
                i, i + 1, html.escape(root), extra, html.escape(name), html.escape(rom)))
        for k in list(hl):
            if ',' in hl[k]:
                hl[k] = hl[k].split(',')[0] + '…'
        pid = len(self.patterns)
        self.patterns.append({'type': 'ev', 'bpm': bpm, 'beats': len(bars) * 4, 'ev': ev, 'dr': []})
        title = '<div class="ctitle">%s</div>' % self.inline(o['title'], fn) if o.get('title') else ''
        meta = '%d BPM · CHORD = %s%s · по такту на аккорд' % (bpm, kind, '' if scale == 'MAJ' else ' · ' + scale)
        kb = F.keyboard(hl, sorted(ghost), 'notes', (), None)
        note = '<p class="cnote">%s</p>' % self.inline(o['note'], fn) if o.get('note') else ''
        return '<figure class="course" data-pid="%d">%s%s<div class="ccards">%s</div>%s%s</figure>' % (
            pid, title, self.play_bar(pid, meta), ''.join(cards), kb, note)

    def loop(self, o, fn):
        bpm = int(o.get('bpm', 90))
        scale = o.get('scale', 'MAJ')
        nbars = int(o.get('bars', 4))
        beats = nbars * 4
        ev, dr = [], []
        tracks = []
        if o.get('drums'):
            lanes = []
            for part in o['drums'].split(';'):
                ln, _, pat = part.strip().partition(':')
                lanes.append((int(ln), pat))
            for b in range(nbars):
                for ln, pat in lanes:
                    for st, ch in enumerate(pat):
                        if ch != '.':
                            dr.append([b * 4 + st / 4, ln, {'g': .22, 'x': .5, 'X': .8, 'O': 1}.get(ch, .8), 'drums'])
            rows = ''.join('<tr><th class="lab"><span class="ln">%d</span> %s</th>%s</tr>' % (
                ln, F.esc(LANES[ln]),
                ''.join('<td class="c v-%s%s"></td>' % ({'.': 'e'}.get(ch, ch), ' gs' if j % 4 == 0 else '') for j, ch in enumerate(pat)))
                for ln, pat in lanes)
            tracks.append(('drums', 4, 'Ударные', '<div class="grid-scroll"><table class="grid drum">%s</table></div>' % rows))
        if o.get('chords'):
            toks = o['chords'].split()
            cards = []
            for i, tok in enumerate(toks):
                root, mods, ms, name, rom = self.chord_of(tok, scale, o.get('kind', 'TRIAD'))
                per = beats / len(toks)
                ev.append([i * per, per, ms, 'pad', [F.midi_name(m) for m in ms], -1])
                cards.append('<span class="ccard"><b>%s</b><span>%s</span><i>%s</i></span>' % (html.escape(tok), html.escape(name), html.escape(rom)))
            tracks.append(('pad', 2, 'Аккорды (CHORD = TRIAD)', '<div class="ccards">%s</div>' % ''.join(cards)))
        if o.get('bass'):
            notes = F.parse_notes(o['bass'])
            e, _ = self.song_events(notes, scale, 'bass')
            for x in e:
                x[5] = -1
            ev += e
            tracks.append(('bass', 1, 'Бас', F.chips(notes, scale).replace(' data-i="', ' data-x="')))
        if o.get('melody'):
            notes = F.parse_notes(o['melody'])
            e, _ = self.song_events(notes, scale, 'lead')
            ev += e
            tracks.append(('lead', 3, 'Мелодия', F.staff(notes) if scale == 'MAJ' else F.chips(notes, scale)))
        pid = len(self.patterns)
        self.patterns.append({'type': 'ev', 'bpm': bpm, 'beats': beats, 'ev': ev, 'dr': dr})
        title = '<div class="ctitle">%s</div>' % self.inline(o['title'], fn) if o.get('title') else ''
        rows = ''.join('<div class="trk t%d"><label class="tmute"><input type="checkbox" checked data-voice="%s"> '
                       '<span class="tno">%d</span> %s</label>%s</div>' % (n, v, n, html.escape(t), body)
                       for v, n, t, body in tracks)
        note = '<p class="cnote">%s</p>' % self.inline(o['note'], fn) if o.get('note') else ''
        return '<figure class="course loop" data-pid="%d">%s%s%s%s</figure>' % (
            pid, title, self.play_bar(pid, '%d BPM · %d такта · галочки = mute (как GLO + 1…4)' % (bpm, nbars)), rows, note)

    def split_row(self, row):
        codes = []

        def keep(m):
            codes.append(m.group(0))
            return '\x01%d\x01' % (len(codes) - 1)

        row = re.sub(r'`[^`]*`', keep, row.strip())
        cells = row.strip('|').split('|')
        return [re.sub(r'\x01(\d+)\x01', lambda m: codes[int(m.group(1))], c).strip() for c in cells]

    def table(self, rows, fn):
        head = self.split_row(rows[0])
        body = [self.split_row(r) for r in rows[2:]]
        h = ''.join('<th>%s</th>' % self.inline(c, fn) for c in head)
        b = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % self.inline(c, fn) for c in r) for r in body)
        return '<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (h, b)

    # ------------------------------------------------------------ grids
    @staticmethod
    def settings(ctx):
        bpm = re.search(r'BPM (\d+)', ctx)
        swg = re.search(r'SWG (\d+) %', ctx)
        div = re.search(r'DIV (1/16|1/8|1/4|8T|16T)', ctx)
        sc = re.search(r'\b(MAJ|MIN|DOR|PHRY|LYD|MIX|LOC|HARM|MEL|MPEN|PEN|BLUES)\b', ctx)
        return {
            'bpm': int(bpm.group(1)) if bpm else 100,
            'swing': int(swg.group(1)) if swg else 50,
            'div': div.group(1) if div else '1/16',
            'scale': sc.group(1) if sc else 'MAJ',
        }

    def code(self, lines, ctx, fn):
        lines = [l.rstrip() for l in lines]
        while lines and not lines[-1].strip():
            lines.pop()
        return self.drum_grid(lines, ctx, fn) or self.mel_grid(lines, ctx, fn) or \
            '<pre>%s</pre>' % html.escape('\n'.join(lines), quote=False)

    def drum_grid(self, lines, ctx, fn):
        subs = []                       # [{title, head:[groups], rows:[(label, groups, comment)]}]
        for l in lines:
            if not l.strip():
                continue
            lab, rest = l[:12], l[12:]
            if re.fullmatch(r'(\.\.\.\|)?[1-9][e+a]*(\|[1-9][e+a]*)*', rest):
                subs.append({'title': lab.strip(), 'head': rest.split('|'), 'rows': []})
                continue
            m = re.fullmatch(r'([XOxgFN.234\-|]+)(\s+.*)?', rest)
            if m and subs and '|' in m.group(1):
                groups = m.group(1).split('|')
                if [len(g) for g in groups] != [len(g) for g in subs[-1]['head']]:
                    return None
                subs[-1]['rows'].append((lab.strip(), groups, (m.group(2) or '').strip()))
                continue
            return None
        if not subs or not any(s['rows'] for s in subs):
            return None
        st = self.settings(ctx)
        spb = 3 if st['div'] == '8T' or (subs[0]['head'][0] in ('1+a',)) else 4

        def lane_of(label):
            m = re.match(r'^(\d+)\s', label)
            return int(m.group(1)) if m else None

        def playable(sub):
            if sub['head'][0] == '...':
                return False
            return all(lane_of(r[0]) or r[0].startswith('Усл') for r in sub['rows'])

        bars = all(s['title'].startswith('такт') for s in subs) and len(subs) > 1
        groups_of = [subs] if bars else [[s] for s in subs]
        html_out = []
        for grp in groups_of:
            pid = None
            if all(playable(s) for s in grp):
                pid = len(self.patterns)
                lanes, cond, length = {}, [], 0
                for s in grp:
                    n = sum(len(g) for g in s['head'])
                    for lab, groups, _ in s['rows']:
                        cells = list(''.join(groups))
                        if lab.startswith('Усл'):
                            cond += [None] * (length - len(cond)) + cells
                            continue
                        ln = lane_of(lab)
                        lanes.setdefault(ln, [])
                        lanes[ln] += ['.'] * (length - len(lanes[ln])) + cells
                    length += n
                for ln in lanes:
                    lanes[ln] += ['.'] * (length - len(lanes[ln]))
                if cond:
                    cond += ['.'] * (length - len(cond))
                self.patterns.append({'type': 'drum', 'bpm': st['bpm'], 'swing': st['swing'], 'spb': spb,
                                      'len': length, 'lanes': lanes, 'cond': cond or None})
            html_out.append(self.render_drum(grp, pid, st, bool(any(r[0].startswith('Усл') for s in grp for r in s['rows']))))
        return '\n'.join(html_out)

    def toolbar(self, pid, st, fill, kind):
        if pid is None:
            return ''
        meta = '%d BPM' % st['bpm']
        if st['swing'] != 50:
            meta += ' · SWG %d %%' % st['swing']
        if kind == 'mel':
            meta += ' · %s' % st['scale']
        f = '<label class="fill"><input type="checkbox" data-fill="%d"> брейк (GLO + 10)</label>' % pid if fill else ''
        return ('<div class="grid-bar"><button class="play" data-pid="%d" aria-label="Слушать">'
                '<span class="ico">▶</span><span class="txt">Слушать</span></button>'
                '<span class="meta">%s</span>%s</div>' % (pid, meta, f))

    def render_drum(self, grp, pid, st, fill):
        parts = []
        offset = 0
        for s in grp:
            n = sum(len(g) for g in s['head'])
            head_cells = []
            k = 0
            for gi, g in enumerate(s['head']):
                for ci, ch in enumerate(g):
                    cls = ['h']
                    if ci == 0:
                        cls.append('gs')
                    if ch.isdigit():
                        cls.append('beat')
                    head_cells.append('<th class="%s" data-s="%s">%s</th>' % (' '.join(cls), offset + k if pid is not None else '', html.escape(ch)))
                    k += 1
            title = '<caption>%s</caption>' % html.escape(s['title']) if s['title'] else ''
            rows = []
            for lab, groups, comment in s['rows']:
                cells = []
                k = 0
                for g in groups:
                    for ci, ch in enumerate(g):
                        cls = ['c', 'v-' + {'.': 'e', 'X': 'X', 'O': 'O', 'x': 'x', 'g': 'g', '-': 't', 'F': 'F', 'N': 'N'}.get(ch, 'r')]
                        if ci == 0:
                            cls.append('gs')
                        txt = ch if ch in '234FN' else ''
                        cells.append('<td class="%s" data-s="%s" title="%s">%s</td>' % (
                            ' '.join(cls), offset + k if pid is not None else '', html.escape(ch), txt))
                        k += 1
                m = re.match(r'^(\d+)\s+(.*)$', lab)
                if m:
                    labh = '<span class="ln">%s</span> %s' % (m.group(1), html.escape(m.group(2)))
                else:
                    labh = html.escape(lab)
                com = '<td class="com">%s</td>' % html.escape(comment) if comment else ''
                rows.append('<tr><th class="lab">%s</th>%s%s</tr>' % (labh, ''.join(cells), com))
            parts.append('<table class="grid drum">%s<thead><tr><th class="lab"></th>%s</tr></thead><tbody>%s</tbody></table>'
                         % (title, ''.join(head_cells), ''.join(rows)))
            offset += n
        return '<figure class="grid-wrap" data-pid="%s">%s<div class="grid-scroll">%s</div></figure>' % (
            '' if pid is None else pid, self.toolbar(pid, st, fill, 'drum'), ''.join(parts))

    def mel_grid(self, lines, ctx, fn):
        rows = []
        head = None
        for l in lines:
            if not l.strip():
                continue
            m = re.fullmatch(r'(.{7})\|(.+)\|\s*', l)
            if not m:
                return None
            lab, body = m.group(1).strip(), m.group(2)
            groups = body.split('|')
            if any(len(g) % 3 for g in groups):
                return None
            cells = [[g[i:i + 3].strip() for i in range(0, len(g), 3)] for g in groups]
            if head is None and not lab:
                head = cells
                continue
            rows.append((lab, cells))
        if head is None or not rows:
            return None
        st = self.settings(ctx)
        spb = {'1/16': 4, '1/8': 2, '1/4': 1, '8T': 3, '16T': 6}[st['div']]
        n = sum(len(g) for g in head)
        bass = fn.startswith('05-')
        voices, order = {}, []
        last = None
        for lab, cells in rows:
            flat = [c for g in cells for c in g]
            if lab.startswith('флаг'):
                if last is not None:
                    v = voices[last]
                    v['flags'] += ['.'] * (len(v['cells']) - n - len(v['flags'])) + flat
                continue
            if lab == 'аккорд':
                last = None
                continue
            key = re.sub(r'^(нота|такт \d+|т\.\d–\d)$', '', lab)
            key = re.sub(r'\s*т\d+$', '', key)
            if key not in voices:
                voices[key] = {'cells': [], 'flags': []}
                order.append(key)
            voices[key]['cells'] += flat
            last = key
        pid = None
        if voices:
            scale = SCALES[st['scale']]
            length = max(len(v['cells']) for v in voices.values())
            out_voices = []
            for k in order:
                v = voices[k]
                cells = v['cells'] + ['.'] * (length - len(v['cells']))
                flags = v['flags'] + ['.'] * (length - len(v['flags']))
                notes = []
                for c in cells:
                    if re.fullmatch(r'[A-G][3-5]', c):
                        idx = WHITE.index(c[0]) + 7 * (int(c[1]) - 4)
                        cnt = len(scale)
                        octv, deg = divmod(idx, cnt)
                        notes.append(60 + 12 * octv + scale[deg] - (24 if bass else 0))
                    else:
                        notes.append(c)
                out_voices.append({'notes': notes, 'flags': flags})
            pid = len(self.patterns)
            self.patterns.append({'type': 'mel', 'bpm': st['bpm'], 'swing': st['swing'], 'spb': spb,
                                  'len': length, 'voices': out_voices, 'bass': bass})
        # render: one table, every row its own line, step numbers continue across bars
        hc = []
        for gi, g in enumerate(head):
            for ci, c in enumerate(g):
                hc.append('<th class="h%s%s">%s</th>' % (' gs' if ci == 0 else '', ' beat' if c.isdigit() else '', html.escape(c)))
        body = []
        pos = {}
        for lab, cells in rows:
            flat = [c for g in cells for c in g]
            if lab.startswith('флаг') or lab == 'аккорд':
                key = None
            else:
                key = re.sub(r'^(нота|такт \d+|т\.\d–\d)$', '', lab)
                key = re.sub(r'\s*т\d+$', '', key)
            if lab.startswith('флаг'):
                base = pos.get('_lastbase', 0)
            elif key is not None:
                base = pos.get(key, 0)
                pos[key] = base + len(flat)
                pos['_lastbase'] = base
            else:
                base = 0
            tds = []
            k = 0
            for g in cells:
                for ci, c in enumerate(g):
                    cls = ['m']
                    if ci == 0:
                        cls.append('gs')
                    if lab.startswith('флаг'):
                        cls.append('flag')
                        txt = '' if c == '.' else c
                    elif c == '-':
                        cls.append('tie')
                        txt = ''
                    elif c == '.':
                        cls.append('rest')
                        txt = ''
                    else:
                        cls.append('note')
                        txt = c
                    ds = base + k if pid is not None and (key is not None or lab.startswith('флаг')) else ''
                    tds.append('<td class="%s" data-s="%s" data-v="%s">%s</td>' % (' '.join(cls), ds, html.escape(key or ''), html.escape(txt)))
                    k += 1
            body.append('<tr class="%s"><th class="lab">%s</th>%s</tr>' % ('flagrow' if lab.startswith('флаг') else '', html.escape(lab), ''.join(tds)))
        tbl = '<table class="grid mel"><thead><tr><th class="lab"></th>%s</tr></thead><tbody>%s</tbody></table>' % (''.join(hc), ''.join(body))
        return '<figure class="grid-wrap" data-pid="%s">%s<div class="grid-scroll">%s</div></figure>' % (
            '' if pid is None else pid, self.toolbar(pid, st, False, 'mel'), tbl)


def build(root, out):
    book = Book(root)
    sections, nav = [], []
    group = None
    for fn, part, short in ORDER:
        body, toc = book.convert(fn)
        sid = 'ch-' + pref(fn)
        sections.append('<section class="chapter" id="%s" data-file="%s">%s</section>' % (sid, fn, body))
        if part != group:
            nav.append('<li class="part">%s</li>' % html.escape(part))
            group = part
        sub = ''.join('<li><a href="#%s">%s</a></li>' % (hid, html.escape(t)) for hid, t in toc)
        nav.append('<li class="chap" data-sec="%s"><a href="#%s">%s</a><ul class="sub">%s</ul></li>' % (sid, sid, html.escape(short), sub))
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html'), encoding='utf-8').read()
    page = tpl.replace('{{NAV}}', '\n'.join(nav)).replace('{{SECTIONS}}', '\n'.join(sections)) \
              .replace('{{PATTERNS}}', json.dumps(book.patterns, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
    open(out, 'w', encoding='utf-8').write(page)
    print('patterns', len(book.patterns), 'bytes', len(page.encode('utf-8')))


if __name__ == '__main__':
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = sys.argv[1] if len(sys.argv) > 1 else here
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, 'sloop-book.html')
    build(root, out)
