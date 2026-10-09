"""Audio pack: the WAVs from render_audio.js -> MP3 files named by the codes shown in the book,
in folders by part, zipped for the iPhone Files app.
    python3 tools/pack_audio.py sloop-book.html out/wav out/sloop-audio.zip
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = {'kurs': '1 Курс', 'zhanr': '2 Жанры', 'shkola': '3 Школа'}
CHAPTERS = {1: 'Как читать сетки', 2: 'Ударные', 3: 'Брейки', 4: 'Аккорды', 5: 'Басы', 6: 'Мелодии',
            7: 'Рецепты', 8: 'Против одинаковости'}
TARGET = -16.0       # LUFS: every file about as loud as the next, a sparse hi-hat example included

README = """Аудио-пакет «Книги партий SLOOP»

Каждый файл — один пример из книги. Его код написан в книге рядом с кнопкой «▶ Слушать»:
«♪ К02-1» → папка «1 Курс» → файл «К02-1 …».

  1 Курс        — К00…К13, номер урока и номер примера в уроке
  2 Жанры       — Ж01…Ж09, номер жанра
  3 Школа       — Ш1…Ш3, часть Школы
  4 Справочник  — по главам; коды как в книге: D01 (бит), F08 (брейк), B01 (бас), M01 (мелодия)

Это звук браузерного синтезатора книги — примерный, чтобы услышать ритм и ноты.
На FM-1 с пресетом из книги звучит по-настоящему.

iPhone: открой архив в «Файлах» (нажми на него — распакуется в папку рядом),
дальше нажимай на любой файл — играет без интернета.
"""


def folder(ch):
    m = re.match(r'^(kurs|zhanr|shkola)', ch)
    if m:
        return PARTS[m.group(1)]
    n = int(ch[:2])
    return os.path.join('4 Справочник', 'Глава %d. %s' % (n, CHAPTERS.get(n, ch[3:])))


def loudness(path):
    """Integrated loudness, LUFS."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])


def main(book, wav_dir, zip_path):
    s = open(book, encoding='utf-8').read()
    pats = json.loads(re.search(r'const PATTERNS = (\[.*?\]);\n', s, re.S).group(1))
    tmp = tempfile.mkdtemp()
    top = os.path.join(tmp, 'SLOOP аудио')
    os.makedirs(top)
    with open(os.path.join(top, 'Как слушать.txt'), 'w', encoding='utf-8') as f:
        f.write(README)
    for pid, p in enumerate(pats):
        a = p['aud']
        d = os.path.join(top, folder(a['ch']))
        os.makedirs(d, exist_ok=True)
        name = ('%s %s' % (a['code'], a['name'])).strip()
        dst = os.path.join(d, name + '.mp3')
        src = os.path.join(wav_dir, '%d.wav' % pid)
        gain = max(-10.0, min(18.0, TARGET - loudness(src)))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src,
                        '-af', 'volume=%.1fdB,alimiter=limit=0.89:level=false' % gain, '-ar', '44100', '-ac', '1',
                        '-c:a', 'libmp3lame', '-b:a', '96k',
                        '-metadata', 'title=%s' % name, '-metadata', 'album=Книга партий SLOOP',
                        '-metadata', 'track=%d' % (pid + 1), dst], check=True)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as z:     # MP3 does not compress further
        for dp, _, files in sorted(os.walk(top)):
            for fn in sorted(files):
                full = os.path.join(dp, fn)
                z.write(full, os.path.relpath(full, tmp))
    shutil.rmtree(tmp)
    print('files', len(pats), 'zip', os.path.getsize(zip_path))


if __name__ == '__main__':
    main(*sys.argv[1:4])
