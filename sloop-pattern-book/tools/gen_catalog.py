#!/usr/bin/env python3
"""Write 09-katalog.md: every factory sound and drum kit of SLOOP 2.4, with where the book uses it.

Usage: python3 tools/gen_catalog.py   (run again after editing the book; then build_html.py)

The lists are SLOOP 2.4.1's own (firmware/src/ui.c BANK, drums.c and tools/gen_drumkits.py at
tag v2.4.1): 76 sounds, 37 factory kits + 5 user kits, 10 engines.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_html import ORDER  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# kind -> [(name, engine, how it sounds, genres)]
SOUNDS = [
    ('Басы', [
        ('808 BOOM', 'ANALOG', 'классическая 808: длинная гудящая бочка с нотой. Звучит на 2 октавы ниже клавиш, съезжает между нажатыми нотами', 'трэп, плагг, реггетон, джерси-клаб'),
        ('808 DIRTY', 'ANALOG', '808 с перегрузом — грязнее и злее', 'фонк, рейдж, хайперпоп'),
        ('808 SLIDE', 'ANALOG', '808 для длинных слайдов между нотами', 'дрилл, трэп'),
        ('SUB BASS', 'ANALOG', 'чистый низкий саб почти без верхов, тоже на 2 октавы ниже', 'хаус, регги, гараж, эмбиент'),
        ('PLUGG BASS', 'ANALOG', 'мягкая 808 для плагга, скользит между нотами', 'плагг, плаггнб'),
        ('REESE', 'ANALOG', 'толстый расстроенный бас, который «шевелится»', 'драм-н-бейс, дабстеп'),
        ('WOBBLE', 'ANALOG', 'бас с качающимся фильтром', 'дабстеп'),
        ('ACID 303', 'ANALOG', 'кислотный бас в духе TB-303 — крути CUT и RES', 'эйсид, техно'),
        ('FUNK BASS', 'ANALOG', 'упругий бас для коротких нот', 'фанк, диско'),
        ('FM BASS', 'DIGITAL', 'плотный FM-бас со щелчком в начале', 'хаус, техно, амапиано'),
        ('CZ BASS', 'PHASE', 'бас в духе Casio CZ', 'синтвейв, техно'),
        ('FAT BASS', 'TRIO', 'три осциллятора — широкий жирный бас', 'синтвейв, рок, хаус, джи-фанк'),
        ('WOW BASS', 'VOICE', 'бас с «голосовым» оттенком, как будто говорит «вау»', 'фанк, джи-фанк'),
        ('GB BASS', 'LOFI', '8-битный бас, как в старых приставках', 'чиптюн'),
        ('UP BASS', 'SAMPLE', 'сэмпл контрабаса', 'бум-бэп, джаз, босса'),
        ('DEEP BASS', 'SAMPLE', 'сэмпл глубокого баса', 'лоу-фай, регги, R&B'),
        ('ROUND BASS', 'FM6', 'округлый FM-бас в духе DX7', 'дип-хаус, сити-поп'),
    ]),
    ('Клавишные', [
        ('RHODES', 'DIGITAL', 'электропиано в духе Rhodes — тёплое, «бархатное»', 'лоу-фай, соул, R&B, амапиано'),
        ('DX RHODES', 'DIGITAL', 'FM-электропиано 80-х, как на DX7', 'сити-поп, баллады 80-х'),
        ('WURLI', 'DIGITAL', 'электропиано Wurlitzer — чуть «кусачее»', 'соул, инди'),
        ('M1 PIANO', 'DIGITAL', 'яркое пиано хаус-музыки 90-х', 'хаус'),
        ('AFRO KEYS', 'DIGITAL', 'светлые клавиши для афро-грувов', 'афробит, амапиано, реггетон'),
        ('GRAND PNO', 'SAMPLE', 'рояль Steinway, записанный по нотам; длинные ноты затухают', 'баллады, дрилл, кино'),
        ('DUSTY PNO', 'SAMPLE', 'пыльное пиано, как сэмпл со старой пластинки', 'бум-бэп, лоу-фай'),
        ('LOFI KEYS', 'SAMPLE', 'клавиши с лоу-фай окраской', 'лоу-фай'),
        ('SOFT KEYS', 'PHASE', 'мягкие клавиши', 'лоу-фай, эмбиент'),
        ('CLAV', 'DIGITAL', 'клавинет — щёлкающие, ритмичные клавиши', 'фанк, регги, диско'),
        ('TINE EP', 'FM6', 'электропиано со «звенящими» язычками (DX7)', 'сити-поп, R&B'),
    ]),
    ('Органы', [
        ('SOUL ORGAN', 'WHEEL', 'электроорган для соула', 'соул, регги'),
        ('GOSPEL', 'WHEEL', 'церковный «госпел»-орган', 'госпел, R&B'),
        ('JAZZ ORGAN', 'WHEEL', 'джазовый орган', 'джаз, соул-джаз'),
        ('DIRTY B3', 'WHEEL', 'перегруженный орган Hammond B3', 'рок, блюз'),
        ('HOUSE ORGN', 'WHEEL', 'орган хаус-музыки 90-х', 'хаус, гараж'),
        ('DRAWBARS', 'FM6', 'орган, собранный на FM6', 'госпел, хаус'),
    ]),
    ('Пэды', [
        ('WARM PAD', 'ANALOG', 'тёплый аналоговый пэд', 'хаус, поп, эмбиент'),
        ('SAW PAD', 'TRIO', 'яркий пэд из «пил»', 'синтвейв, транс, хайперпоп'),
        ('GLASS PAD', 'DIGITAL', 'стеклянный FM-пэд', 'плагг, эмбиент, трэп'),
        ('DARK STR', 'ANALOG', 'тёмные синт-струнные', 'дрилл, кино, трэп'),
        ('CZ STRING', 'PHASE', 'струнные в духе Casio CZ', '80-е, синтвейв'),
        ('ATMOS PAD', 'ANALOG', 'атмосферный «воздушный» пэд', 'эмбиент, драм-н-бейс'),
        ('LOFI CLOUD', 'GRAIN', 'гранулярное «облако» звука', 'лоу-фай, эмбиент'),
        ('VIBE HAZE', 'GRAIN', 'дымка из нот вибрафона', 'лоу-фай, эмбиент'),
        ('CHOIR AAH', 'VOICE', 'хор на «а-а-а»', 'трэп, эпик, джерси-клаб (нарезка)'),
        ('SOUL OOH', 'VOICE', 'хор на «у-у-у», мягкий', 'соул, R&B, дип-хаус'),
        ('SOFT PAD', 'FM6', 'мягкий FM-пэд', 'эмбиент, баллады'),
    ]),
    ('Лиды', [
        ('SUPERSAW', 'ANALOG', 'широкая «суперпила» — много расстроенных голосов', 'рейдж, транс, хайперпоп, синтвейв'),
        ('G-FUNK LD', 'ANALOG', 'высокий свистящий лид джи-фанка', 'джи-фанк'),
        ('SYNC LEAD', 'TRIO', 'резкий «синхро»-лид', 'электро, рок, поп'),
        ('HOOVER', 'TRIO', 'рейв-«хувер» 90-х', 'рейв, джангл'),
        ('TALKBOX', 'VOICE', '«говорящий» синт, как через трубку', 'джи-фанк, фанк'),
        ('GAME LEAD', 'LOFI', '8-битный лид из игр', 'чиптюн, хайперпоп'),
        ('LOFI FLUTE', 'SAMPLE', 'флейта с лоу-фай окраской', 'лоу-фай, хип-хоп'),
        ('FLUTE DUST', 'GRAIN', 'флейта, «распылённая» на зёрна', 'эмбиент, лоу-фай'),
    ]),
    ('Плаки и колокольчики', [
        ('TRAP PLUCK', 'ANALOG', 'короткий синт-щипок', 'реггетон, трэп, поп'),
        ('RESO PLUCK', 'PHASE', 'резонансный щипок с «пиу» в начале', 'хаус, синтвейв'),
        ('PLUGG BELL', 'DIGITAL', 'светлый колокольчик плагга', 'плагг, плаггнб'),
        ('TRAP BELL', 'DIGITAL', 'колокольчик трэпа', 'трэп, фонк'),
        ('MUSIC BOX', 'DIGITAL', 'музыкальная шкатулка', 'эмбиент, «тёмные» интро'),
        ('KALIMBA', 'DIGITAL', 'калимба — африканское «пианино большими пальцами»', 'афро, лоу-фай'),
        ('MARIMBA', 'DIGITAL', 'маримба — деревянные пластины', 'афро, латино'),
        ('VIBES', 'SAMPLE', 'вибрафон', 'джаз, лоу-фай, хип-хоп'),
        ('8BIT ARP', 'LOFI', '8-битный звук для быстрых арпеджио', 'чиптюн, хайперпоп'),
        ('GLASS BELL', 'FM6', 'стеклянный колокол в духе DX7', 'эмбиент, плагг'),
        ('WOOD BARS', 'FM6', 'деревянные пластины на FM6', 'афро, эмбиент'),
        ('NYLON PICK', 'FM6', 'щипок нейлоновой гитары', 'эмо-рэп, босса, афро'),
    ]),
    ('Стабы', [
        ('MIN STAB', 'TRIO', 'минорный аккорд одной клавишей (CHORD держи OFF)', 'хаус, рейв'),
        ('MIN7 STAB', 'TRIO', 'минорный септаккорд одной клавишей', 'дип-хаус, гараж'),
        ('RAVE STAB', 'TRIO', 'рейв-аккорд одной клавишей', 'рейв, техно, брейкбит'),
        ('DUB CHORD', 'TRIO', 'даб-аккорд одной клавишей — красиво с дилеем', 'даб-техно, дип-хаус'),
        ('SYN BRASS', 'ANALOG', 'синтезаторная медь 80-х', 'синтвейв, поп'),
        ('CZ BRASS', 'PHASE', 'медь в духе Casio CZ', 'фанк, синтвейв'),
        ('HORN STAB', 'SAMPLE', 'духовой «удар» из сэмпла', 'бум-бэп, хип-хоп'),
        ('STRING STB', 'SAMPLE', 'короткий струнный «удар»', 'дрилл, хип-хоп, кино'),
        ('BRASS SECT', 'FM6', 'медная секция', 'фанк, диско'),
    ]),
    ('Эффекты', [
        ('SCRATCH', 'SAMPLE', 'скретч, бэкспин и перемотка — разные клавиши дают разное', 'хип-хоп, бум-бэп'),
        ('GM KIT', 'SAMPLE', 'барабаны на синт-треке: нижняя клавиша F3 — бочка, лад не действует', 'перкуссия со своей длиной (полиметрия)'),
    ]),
]

# (number, kit, style written by the firmware, genres)
KITS = [
    ('1', 'ACOUSTIC', 'STUDIO', 'живая установка: рок, поп, фанк, джаз'),
    ('2', 'DEEP', 'SOFT', 'мягкая живая: баллады, трип-хоп'),
    ('3', 'TIGHT', 'PUNCHY', 'плотная живая: рок, фанк'),
    ('4', 'BRIGHT', 'BRIGHT', 'яркая живая: поп-рок, инди'),
    ('5', 'DUST', 'DUSTY', 'пыльная живая: бум-бэп, лоу-фай'),
    ('6', '808', 'HIP HOP', 'хип-хоп, трэп, электро'),
    ('7', '909', 'HOUSE', 'хаус, техно, рейв'),
    ('8', '606', 'ACID', 'эйсид, минимал'),
    ('9', '80S', '80S POP', 'поп 80-х, синтвейв'),
    ('10', 'VINTAGE', 'RHYTHM BOX', 'фанк, регги, брейкбит, старая драм-машина'),
    ('11', 'TRAP', 'TRAP', 'трэп, эмо-рэп, рейдж, джерси-клаб'),
    ('12', 'DRILL', 'UK DRILL', 'дрилл'),
    ('13', 'BOOMBAP', 'HIP HOP', 'бум-бэп, хип-хоп 2020-х'),
    ('14', 'LO-FI', 'LO-FI', 'лоу-фай'),
    ('15', 'PHONK', 'PHONK', 'фонк'),
    ('16', 'HOUSE', 'HOUSE', 'хаус'),
    ('17', 'D.HOUSE', 'DEEP HOUSE', 'дип-хаус'),
    ('18', 'TECHNO', 'TECHNO', 'техно'),
    ('19', 'MINIMAL', 'MINIMAL', 'минимал'),
    ('20', 'ELECTRO', 'ELECTRO', 'электро'),
    ('21', 'DISCO', 'DISCO', 'диско, ню-диско'),
    ('22', 'GARAGE', 'UK GARAGE', 'UK garage'),
    ('23', 'JUNGLE', 'DRUM & BASS', 'джангл, драм-н-бейс'),
    ('24', 'DUBSTEP', 'BASS MUSIC', 'дабстеп'),
    ('25', 'DEMBOW', 'REGGAETON', 'реггетон, мумбатон'),
    ('26', 'AMAPIANO', 'AMAPIANO', 'амапиано'),
    ('27', 'AFRO', 'AFROBEAT', 'афробит, афро-хаус'),
    ('28', 'LATIN', 'LATIN', 'босса, сальса, кумбия'),
    ('29', 'TRIBAL', 'TRIBAL', 'афро-хаус, перкуссия, нечётные размеры'),
    ('30', 'SYNTHWV', 'SYNTHWAVE', 'синтвейв'),
    ('31', 'CHIP', 'CHIPTUNE', 'чиптюн'),
    ('32', 'ARCADE', 'VIDEO GAME', 'чиптюн, музыка из игр'),
    ('33', 'GLITCH', 'GLITCH', 'глитч, IDM, хайперпоп'),
    ('34', 'INDUSTR', 'INDUSTRIAL', 'индастриал, хард-техно'),
    ('35', 'HYPER', 'HYPERPOP', 'хайперпоп'),
    ('36', 'AMBIENT', 'AMBIENT', 'эмбиент, даунтемпо'),
    ('37', 'JAZZ', 'JAZZ', 'джаз, босса, лаунж'),
]

ENGINES = [
    ('ANALOG', 'OSC / FLT', 'аналоговый синт: два осциллятора и фильтр', '808, басы, SUPERSAW, тёплые пэды'),
    ('DIGITAL', 'OPS / MOD', '4-операторный FM-синтез', 'электропиано, колокольчики, FM-басы'),
    ('PHASE', 'PHS / LINE', 'фазовые искажения в духе Casio CZ', 'CZ-басы, струнные, медь'),
    ('LOFI', 'CHIP / MOTN', '8-битный чип', 'GB BASS, GAME LEAD, 8BIT ARP'),
    ('SAMPLE', 'SET / TONE', 'сэмплер: наборы PIANO, BASS, VIBES, HORNS, STRGS, FLUTE, SCRCH, PERC и твои USR1–USR4', 'рояль, контрабас, флейта, скретчи'),
    ('VOICE', 'VOWL / TONE', 'голос и хоры (форманты)', 'CHOIR AAH, SOUL OOH, TALKBOX'),
    ('TRIO', 'OSC / TONE', 'три осциллятора', 'FAT BASS, стабы-аккорды, HOOVER'),
    ('WHEEL', 'BARS / TONE', 'электроорган (тонколёса)', 'все органы'),
    ('GRAIN', 'GRAN / SPRY', 'гранулярный: звук рассыпается на «зёрна»', 'облака, дымка, эмбиент'),
    ('FM6', 'OPS / PATCH', '6 операторов, как Yamaha DX7 (8 заводских патчей F1–F8, свои — B1–B27)', 'TINE EP, ROUND BASS, NYLON PICK'),
]

ONLY_25 = ('PHYS и NOISE (движки), SYN1–SYN4 (киты), а также звуки вроде SITAR, KOTO, HARP, XYLOPHONE, STEEL GTR, '
           'TABLA, RAIN, VINYL, RISER, MONO BASS, SAW BASS, FAT LEAD, PAN FLUTE, ROCK ORGAN, CHIP CHORD')


def label(fn, short):
    if fn.startswith('kurs-'):
        return 'Курс ' + short.split('.')[0]
    if fn.startswith('zhanr-'):
        return short.replace('★', '').strip()
    if fn.startswith('shkola-'):
        return 'Школа ' + fn[7]
    return 'Гл. ' + short.split('.')[0]


def usage():
    texts = []
    for fn, part, short in ORDER:
        if fn in ('README.md', '09-katalog.md'):
            continue
        path = os.path.join(ROOT, fn)
        if os.path.exists(path):
            texts.append((fn, label(fn, short), open(path, encoding='utf-8').read()))
    return texts


def where(name, texts, kit=False):
    out = []
    for fn, lab, s in texts:
        if kit:
            pat = r'(?:кит[а-я]*|· кит)[^\n|]{0,40}?(?<![A-Z0-9.-])' + re.escape(name) + r'(?![A-Z0-9])'
        else:
            pat = r'(?<![A-Z0-9])' + re.escape(name) + r'(?![A-Z0-9])'
        if re.search(pat, s):
            out.append('[%s](%s)' % (lab, fn))
    return ', '.join(out) if out else '—'


def main():
    texts = usage()
    L = ['# Глава 9. Каталог: все звуки и киты SLOOP 2.4', '',
         'Всё, что есть в твоей прошивке «с завода»: **76 звуков**, **37 китов** (+ 5 ячеек для своих), **10 движков**. '
         'Список взят из кода самой прошивки 2.4.1. В колонке «Где в книге» — главы, где звук или кит используется.', '',
         '> **Как читать «Как звучит».** Это ориентир по названию, движку и описанию в руководстве SLOOP. '
         'Лучшая проверка — 10 секунд на FM-1: выбери звук и сыграй пару нот.', '',
         '## Как выбрать звук', '',
         '```panel', 'hl=ALGORITHM:трек PRESETS:звук', 'caption=ALGORITHM — трек, PRESETS — звук. Звуки идут по видам: басы, клавишные, органы, пэды, лиды, плаки, стабы, эффекты; потом твои 32 ячейки', '```', '',
         '- **PRESETS** на треках 1–3 листает звуки по видам — как в таблицах ниже. На треке 4 — киты.',
         '- **SAVE → PRESETS → KNOB 2** — выбрать сразу движок. **SAVE → TOOLS → INIT** — «чистый» звук движка.',
         '- Сменить звук не страшно: паттерн, лад и микс трека остаются.', '',
         '## Быстрый выбор: что взять для…', '',
         '| Нужно | Бери |', '| --- | --- |',
         '| бас для трэпа, дрилла, плагга | 808 BOOM, 808 SLIDE, 808 DIRTY, PLUGG BASS |',
         '| бас для хауса, диско, фанка | SUB BASS, FAT BASS, FUNK BASS, FM BASS |',
         '| «живой» бас | UP BASS, DEEP BASS |',
         '| аккорды мягко и красиво | RHODES, DUSTY PNO, GLASS PAD, SOUL OOH |',
         '| аккорды ярко и широко | SAW PAD, SUPERSAW, M1 PIANO, HOUSE ORGN |',
         '| мелодия-колокольчик | TRAP BELL, PLUGG BELL, GLASS BELL, MUSIC BOX |',
         '| громкий лид | SUPERSAW, SYNC LEAD, HOOVER, GAME LEAD |',
         '| «гитара» | NYLON PICK |',
         '| аккорд одной клавишей | MIN STAB, MIN7 STAB, RAVE STAB, DUB CHORD |',
         '| скретчи и перкуссия на синт-треке | SCRATCH, GM KIT |', '']
    n = 0
    for kind, rows in SOUNDS:
        n += len(rows)
        L += ['## %s (%d)' % (kind, len(rows)), '']
        for name, eng, how, genres in rows:            # a short card a sound: readable on a phone
            L.append('- **%s** · %s — %s. *Жанры:* %s. *В книге:* %s' % (name, eng, how, genres, where(name, texts)))
        L.append('')
    assert n == 76, n
    L += ['Плюс **32 ячейки** для твоих звуков (SAVE → USER) — в PRESETS они идут после заводских.', '',
          '## Барабанные киты (37 + 5)', '',
          'На треке 4 **PRESETS** листает киты. «Стиль» — подпись, которую пишет сама прошивка рядом с китом.', '',
          ]
    for num, kit, style, genres in KITS:
        L.append('- **%s. %s** · стиль %s — %s. *В книге:* %s' % (num, kit, style, genres, where(kit, texts, kit=True)))
    L += ['- **38–41. USR1–USR4** · YOUR KIT — свой кит из сэмплов (~7,4 с), делается в веб-редакторе → Drum kit',
          '- **42. USR3+4** · BIG KIT — большой свой кит (~15 с)', '',
          'В каждом ките 16 звуков — по одному на белую клавишу:', '',
          '```keys', 'mode=drums', 'caption=Одинаково во всех китах: клавиша 1 — бочка, 3 — малый, 5 — хэт… меняется только звучание', '```', '',
          '## Движки (10)', '',
          ]
    for eng, pages, what, examples in ENGINES:
        L.append('- **%s** (страницы EDIT: %s) — %s. *Звуки:* %s' % (eng, pages, what, examples))
    L += ['', 'Восемь ручек движка — на страницах EDIT 1 и EDIT 2 (коротко нажми EDIT один или два раза).', '',
          '## Чего в 2.4 нет', '',
          'Если в интернете или в руководстве к новой версии увидишь эти названия — у тебя их нет, они появились в SLOOP 2.5: ' + ONLY_25 + '. '
          'Книга их не использует.', '']
    open(os.path.join(ROOT, '09-katalog.md'), 'w', encoding='utf-8').write('\n'.join(L))
    print('09-katalog.md: %d sounds, %d kits' % (n, len(KITS)))


if __name__ == '__main__':
    main()
