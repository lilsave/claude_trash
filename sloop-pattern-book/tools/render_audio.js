// Records every "Слушать" example of the book into a WAV file, using the book's own browser synth.
// The audio pack (tools/pack_audio.py) turns them into MP3s for phones that cannot run the page.
//   NODE_PATH=$(npm root -g) node tools/render_audio.js sloop-book.html out/wav
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const [, , book = 'sloop-book.html', outDir = 'out/wav'] = process.argv;
const RATE = 44100;

function wav(samples) {
  const b = Buffer.alloc(44 + samples.length * 2);
  b.write('RIFF', 0); b.writeUInt32LE(36 + samples.length * 2, 4); b.write('WAVE', 8);
  b.write('fmt ', 12); b.writeUInt32LE(16, 16); b.writeUInt16LE(1, 20); b.writeUInt16LE(1, 22);
  b.writeUInt32LE(RATE, 24); b.writeUInt32LE(RATE * 2, 28); b.writeUInt16LE(2, 32); b.writeUInt16LE(16, 34);
  b.write('data', 36); b.writeUInt32LE(samples.length * 2, 40);
  samples.forEach((v, i) => b.writeInt16LE(v, 44 + i * 2));
  return b;
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(book));
  const n = await page.evaluate(() => PATTERNS.length);
  for (let pid = 0; pid < n; pid++) {
    const res = await page.evaluate(async ([pid, rate]) => {
      const p = PATTERNS[pid];
      const sb = 60 / p.bpm;
      let loopSec = 0;
      if (p.type === 'ev') loopSec = p.beats * sb;
      else for (let i = 0; i < p.len; i++) loopSec += stepDur(p, i);
      // tunes play once (twice if short); beats and riffs repeat to about 12 seconds
      const tune = p.type === 'ev' && !p.dr.length;
      let loops = tune ? (loopSec < 6 ? 2 : 1) : Math.max(2, Math.min(8, Math.ceil(12 / loopSec)));
      const fill = p.type === 'drum' && p.cond && p.cond.some(c => c === 'F' || c === 'N');
      if (fill) loops = Math.max(loops, 4);
      const t0 = 0.05, total = t0 + loops * loopSec + 2;
      const saved = { ac, out, noiseBuf, ohat, shaper };
      ac = new OfflineAudioContext(1, Math.ceil(total * rate), rate);
      ohat = null; shaper = null;
      const comp = ac.createDynamicsCompressor();
      comp.threshold.value = -12; comp.ratio.value = 12; comp.knee.value = 6; comp.attack.value = 0.003; comp.release.value = 0.25;
      out = ac.createGain(); out.gain.value = 0.6;
      out.connect(comp); comp.connect(ac.destination);
      noiseBuf = ac.createBuffer(1, rate * 1.5, rate);
      const d = noiseBuf.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
      if (p.type === 'ev') {
        const evs = evList(p);
        for (let l = 0; l < loops; l++) evs.forEach(e => playEv(p, e, t0 + l * loopSec + e.t * sb, sb));
      } else {
        let t = t0;
        for (let l = 0; l < loops; l++)
          for (let i = 0; i < p.len; i++) { schedule(p, i, t, fill && l === loops - 1); t += stepDur(p, i); }
      }
      const buf = await ac.startRendering();
      ({ ac, out, noiseBuf, ohat, shaper } = saved);
      const ch = buf.getChannelData(0);
      let end = ch.length;
      while (end > rate && Math.abs(ch[end - 1]) < 1e-4) end--;      // trim the silent tail
      const s = new Array(Math.min(ch.length, end + Math.floor(rate * 0.2)));
      let peak = 0;
      for (let i = 0; i < s.length; i++) {
        const v = Math.max(-1, Math.min(1, ch[i])); peak = Math.max(peak, Math.abs(v));
        s[i] = Math.round(v * 32767);
      }
      return { s, peak, loops, sec: s.length / rate };
    }, [pid, RATE]);
    fs.writeFileSync(path.join(outDir, pid + '.wav'), wav(res.s));
    console.log(pid, 'loops', res.loops, 'sec', res.sec.toFixed(1), 'peak', res.peak.toFixed(2));
  }
  await browser.close();
})();
