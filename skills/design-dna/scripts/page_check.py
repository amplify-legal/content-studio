#!/usr/bin/env python3
"""
page_check.py: read a page's finish off the render, on any surface.

    python3 .claude/skills/design-dna/scripts/page_check.py <page.html> [--widths 1440,390] [--json]
    python3 .claude/skills/design-dna/scripts/page_check.py <page.html> --out /abs/folder
    python3 .claude/skills/design-dna/scripts/page_check.py --self-test

Renders the page in headless Chromium (Playwright) at each width, scrolls it
like a reader so every entrance fires, takes a screenshot of the first screen
and the full page, opens every <details> so folded rows are checked too, then
reads off the render:

  sideways scroll on the page and inside every scrolling box, text runs under
  the floor (18px by default; SVG text at its drawn size), distinct type sizes
  (at most 6), lowest contrast (reading text 4.5:1, text over 43px 3:1),
  controls and links under 44px, presence of prefers-reduced-motion,
  :focus-visible and ::selection rules, any prefers-color-scheme block, any
  gradient.

The rules it checks are references/finish.md section 6 in this skill. Its
defaults are a light-mode, no-gradient house style: if your brand ships a dark
mode or gradients, edit CHECKS and the matching probes, or ignore those 2 lines.
Surface-agnostic, so it runs where dna_check.py has no measured surface.

2 fixes a first prototype needed, kept here as the reason for the code:

  1. Links count as tap targets. A prototype that skipped every <a> passed a
     page of 30px "Open" links. A link that sits inside a line of prose is the
     one exemption (the WCAG 2.5.8 inline rule: its height is the sentence's
     line height); it is counted and printed, never failed.
  2. Sideways scroll is read inside every box, not only on the page. A body set
     to overflow-x: clip hides a sideways scroll from the page-level test, so
     the page test also counts content cut off past the right edge, and every
     box with overflow-x auto or scroll that is wider inside than out is a fail.

Needs: pip install playwright, then either `playwright install chromium` or a
local Chrome (set CHROME=/path/to/chrome; on macOS the default Google Chrome
path is tried). Output goes to a folder under the system temp directory unless
--out names one, so screenshots never land inside a repo by accident. Exit 0
every check passed at every width, 1 any check failed, 2 the page could not be
rendered.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import time

CHROME = os.environ.get("CHROME") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DEFAULT_WIDTHS = [1440, 390]
FLOOR_PX = 18.0      # finish.md section 2: nothing under 18px, code included
LARGE_PX = 43.0      # finish.md section 6: 3:1 above 43px, 4.5:1 for reading text
MAX_SIZES = 6        # finish.md section 2: at most 6 sizes on a page
TARGET_PX = 44.0     # finish.md section 5: every control, links included, 44px tall

CHECKS = [
    ("page_scroll", "No sideways scroll on the page"),
    ("box_scroll", "No sideways scroll inside any box"),
    ("text_floor", "No text under the 18px floor"),
    ("type_sizes", "At most 6 type sizes"),
    ("contrast_reading", "Reading text at 4.5:1 or better"),
    ("contrast_large", "Text over 43px at 3:1 or better"),
    ("targets", "No control or link under 44px"),
    ("reduced_motion", "prefers-reduced-motion block present"),
    ("focus_visible", ":focus-visible rule present"),
    ("selection", "::selection rule present"),
    ("no_dark_mode", "No prefers-color-scheme block"),
    ("no_gradient", "No gradient"),
]

PROBE = r"""
(opts) => {
  const FLOOR = opts.floor, LARGE = opts.large, TARGET = opts.target;
  const de = document.documentElement, body = document.body;
  const VW = de.clientWidth;
  const sel = el => {
    const parts = []; let e = el;
    for (let i = 0; e && e.nodeType === 1 && i < 4; i++) {
      let s = e.tagName.toLowerCase();
      if (e.id) { parts.unshift(s + '#' + e.id); break; }
      const c = [...(e.classList || [])].slice(0, 2).join('.');
      if (c) s += '.' + c;
      parts.unshift(s); e = e.parentElement;
    }
    return parts.join(' > ');
  };
  const cumOpacity = el => { let o = 1; while (el && el.nodeType === 1) { o *= parseFloat(getComputedStyle(el).opacity || '1'); el = el.parentElement; } return o; };
  const srOnly = el => {
    while (el && el.nodeType === 1 && el !== body) {
      const cs = getComputedStyle(el);
      if (cs.clip && /rect\(0/.test(cs.clip) && cs.position === 'absolute') return true;
      if (/inset\(50%/.test(cs.clipPath || '')) return true;
      const r = el.getBoundingClientRect();
      if (r.width <= 1 && r.height <= 1 && cs.overflow === 'hidden') return true;
      el = el.parentElement;
    }
    return false;
  };
  const shown = el => {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility !== 'visible') return false;
    if (cumOpacity(el) < 0.05) return false;
    return !srOnly(el);
  };

  // ---------- colour ----------
  const parse = c => {
    if (!c) return null;
    const m = c.match(/^rgba?\(([^)]+)\)$/); if (!m) return null;
    const p = m[1].split(/[\s,\/]+/).filter(Boolean).map(v => v.endsWith('%') ? parseFloat(v) / 100 : Number(v));
    if (p.length < 3 || p.slice(0, 3).some(isNaN)) return null;
    return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
  };
  const over = (top, under) => { const a = top[3]; return [0, 1, 2].map(i => top[i] * a + under[i] * (1 - a)).concat([1]); };
  const lum = c => { const [r, g, b] = c.slice(0, 3).map(v => { v = v / 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }); return .2126 * r + .7152 * g + .0722 * b; };
  const bgCache = new Map();
  const bgOf = el => {
    // composite every ancestor's background, outermost first, over the white canvas
    const chain = []; let e = el, image = false;
    while (e && e.nodeType === 1) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') image = true;
      chain.push(cs.backgroundColor); e = e.parentElement;
    }
    let base = [255, 255, 255, 1];
    for (let i = chain.length - 1; i >= 0; i--) { const c = parse(chain[i]); if (c && c[3] > 0) base = over(c, base); }
    return { color: base, image };
  };

  // ---------- text runs ----------
  const runs = []; let unparsed = 0, imageBg = 0, hiddenRuns = 0;
  const tw = document.createTreeWalker(body, NodeFilter.SHOW_TEXT);
  while (tw.nextNode()) {
    const n = tw.currentNode; const txt = n.textContent.replace(/\s+/g, ' ').trim(); if (!txt) continue;
    const el = n.parentElement; if (!el) continue;
    if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'TITLE'].includes(el.tagName)) continue;
    const rg = document.createRange(); rg.selectNodeContents(n);
    const rects = [...rg.getClientRects()].filter(r => r.width > 0.5 && r.height > 0.5);
    if (!rects.length) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility !== 'visible') continue;
    const op = cumOpacity(el);
    if (op < 0.05) { hiddenRuns++; continue; }
    if (srOnly(el)) continue;
    let size = parseFloat(cs.fontSize);
    if (typeof SVGGraphicsElement !== 'undefined' && el instanceof SVGGraphicsElement && el.getScreenCTM) {
      const m = el.getScreenCTM(); if (m) size = size * Math.hypot(m.a, m.b);
    }
    runs.push({ el, txt, size, op, cs });
  }
  const sizes = [...new Set(runs.map(r => Math.round(r.size)))].sort((a, b) => a - b);
  const small = runs.filter(r => r.size < FLOOR - 0.05);
  const fams = [...new Set(runs.map(r => r.cs.fontFamily.split(',')[0].replace(/["']/g, '').trim()))];
  let worstR = { ratio: 99 }, worstL = { ratio: 99 }, failR = 0, failL = 0;
  for (const r of runs) {
    const fg = parse(r.cs.color); if (!fg) { unparsed++; continue; }
    const bg = bgOf(r.el); if (bg.image) { imageBg++; continue; }
    const eff = over([fg[0], fg[1], fg[2], fg[3] * r.op], bg.color);
    const L1 = lum(eff), L2 = lum(bg.color);
    const ratio = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
    const large = r.size > LARGE;
    const rec = { ratio: Math.round(ratio * 100) / 100, size: Math.round(r.size * 10) / 10, sample: r.txt.slice(0, 50), where: sel(r.el) };
    if (large) { if (ratio < 3) failL++; if (ratio < worstL.ratio) worstL = rec; }
    else { if (ratio < 4.5) failR++; if (ratio < worstR.ratio) worstR = rec; }
  }

  // ---------- sideways scroll ----------
  const pageScrollW = Math.max(de.scrollWidth, body.scrollWidth);
  const pageScroll = pageScrollW > VW + 1;
  const boxes = []; const cut = []; const clipped = [];
  const all = [...body.querySelectorAll('*')];
  const flaggedCut = new Set();
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (['auto', 'scroll'].includes(cs.overflowX) && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1 && shown(el)) {
      boxes.push({ where: sel(el), inside: el.scrollWidth, outside: el.clientWidth });
    } else if (['hidden', 'clip'].includes(cs.overflowX) && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1 && shown(el) && cs.textOverflow !== 'ellipsis') {
      clipped.push({ where: sel(el), inside: el.scrollWidth, outside: el.clientWidth });
    }
    // content past the right edge whose only clipper is the page itself
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    if (!(r.right > VW + 1 || r.left < -1)) continue;
    if (cs.position === 'fixed' || !shown(el)) continue;
    let a = el.parentElement, clipper = null;
    while (a && a !== body && a !== de) { const ox = getComputedStyle(a).overflowX; if (ox !== 'visible') { clipper = a; break; } a = a.parentElement; }
    if (clipper) continue;
    let p = el.parentElement, under = false; while (p) { if (flaggedCut.has(p)) { under = true; break; } p = p.parentElement; }
    if (under) continue;
    flaggedCut.add(el);
    cut.push({ where: sel(el), right: Math.round(r.right), left: Math.round(r.left) });
  }

  // ---------- targets ----------
  const CTRL = 'button, a[href], summary, select, textarea, input:not([type=hidden]), [role=button], [role=link], [role=tab], [role=checkbox], [role=switch], [role=menuitem]';
  const isCtrl = el => el.matches && el.matches(CTRL);
  const blockOf = el => { let e = el.parentElement; while (e && e !== body) { if (!getComputedStyle(e).display.startsWith('inline')) return e; e = e.parentElement; } return body; };
  const targets = []; const inlineLinks = []; let nCtrl = 0;
  const counted = new Set();
  for (const el of body.querySelectorAll(CTRL + ', label')) {
    let t = el;
    if (el.tagName === 'INPUT' && ['checkbox', 'radio'].includes(el.type)) {
      const lab = el.closest('label') || (el.id && document.querySelector('label[for="' + CSS.escape(el.id) + '"]'));
      if (lab) continue;           // the label is the target and is counted on its own
    }
    if (el.tagName === 'LABEL') {
      const inp = el.querySelector('input[type=checkbox], input[type=radio]') || (el.htmlFor && document.getElementById(el.htmlFor));
      if (!inp || !['checkbox', 'radio'].includes(inp.type)) continue;
    }
    let anc = t.parentElement, inside = false;
    while (anc && anc !== body) { if (isCtrl(anc) || (anc.tagName === 'LABEL' && counted.has(anc))) { inside = true; break; } anc = anc.parentElement; }
    if (inside) continue;
    if (!shown(t)) continue;
    counted.add(t); nCtrl++;
    const r = t.getBoundingClientRect();
    const cs = getComputedStyle(t);
    if (t.tagName === 'A' && cs.display.startsWith('inline') && !cs.display.includes('block') && !cs.display.includes('flex') && !cs.display.includes('grid')) {
      const blk = blockOf(t);
      const rest = (blk.innerText || '').replace(/\s+/g, ' ').trim().length - (t.innerText || '').replace(/\s+/g, ' ').trim().length;
      if (rest > 3) { inlineLinks.push({ where: sel(t), h: Math.round(r.height), text: (t.innerText || '').trim().slice(0, 40) }); continue; }
    }
    if (r.height < TARGET - 0.5) targets.push({ where: sel(t), h: Math.round(r.height * 10) / 10, text: (t.innerText || t.value || t.getAttribute('aria-label') || '').trim().slice(0, 40) });
  }

  // ---------- stylesheets ----------
  let css = '', unreadable = 0;
  const readRules = rules => { for (const r of rules) { css += r.cssText + '\n'; if (r.styleSheet) { try { readRules(r.styleSheet.cssRules); } catch (e) { unreadable++; } } } };
  for (const s of document.styleSheets) { try { readRules(s.cssRules); } catch (e) { unreadable++; } }
  const inlineStyles = [...document.querySelectorAll('[style]')].map(e => e.getAttribute('style')).join('\n');
  let computedGradient = 0;
  for (const el of all) { const bi = getComputedStyle(el).backgroundImage; if (bi && bi.includes('gradient(')) computedGradient++; }
  const svgGradients = document.querySelectorAll('linearGradient, radialGradient').length;
  const metaScheme = [...document.querySelectorAll('meta[name="color-scheme"]')].map(m => m.content).join(' ');
  return {
    viewport: VW,
    pageHeight: de.scrollHeight,
    pageScroll, pageScrollWidth: pageScrollW, cutPastEdge: cut.slice(0, 8), nCut: cut.length,
    boxes: boxes.slice(0, 8), nBoxes: boxes.length, clippedBoxes: clipped.slice(0, 5), nClipped: clipped.length,
    textRuns: runs.length, hiddenRuns, sizes, nSizes: sizes.length,
    under: small.length, underSamples: small.slice(0, 6).map(r => ({ size: Math.round(r.size * 10) / 10, sample: r.txt.slice(0, 40), where: sel(r.el) })),
    families: fams,
    worstReading: worstR.ratio === 99 ? null : worstR, failReading: failR,
    worstLarge: worstL.ratio === 99 ? null : worstL, failLarge: failL,
    contrastSkipped: { unparsedColour: unparsed, imageBackground: imageBg },
    controls: nCtrl, smallTargets: targets.length, smallTargetSamples: targets.slice(0, 8),
    inlineLinksExempt: inlineLinks.length,
    reducedMotion: /prefers-reduced-motion/.test(css),
    focusVisible: /:focus-visible/.test(css),
    selection: /::(-moz-)?selection/.test(css),
    darkMode: /prefers-color-scheme/.test(css) || /dark/i.test(metaScheme) || /color-scheme:\s*[^;}]*dark/i.test(css),
    gradient: /gradient\(/.test(css) || /gradient\(/.test(inlineStyles) || computedGradient > 0 || svgGradients > 0,
    gradientWhere: { css: /gradient\(/.test(css), inlineStyle: /gradient\(/.test(inlineStyles), elements: computedGradient, svg: svgGradients },
    transitionAll: /transition:\s*all\b/.test(css) || /transition-property:\s*all\b/.test(css) || /transition:\s*all\b/.test(inlineStyles),
    textWrapBalance: /text-wrap(-style)?:\s*balance/.test(css),
    tabularNums: getComputedStyle(body).fontVariantNumeric.includes('tabular'),
    unreadableSheets: unreadable,
  };
}
"""

HIDDEN_NO_JS = r"""
() => {
  let hidden = 0, total = 0;
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (tw.nextNode()) {
    const n = tw.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || ['SCRIPT','STYLE','NOSCRIPT','TEMPLATE'].includes(el.tagName)) continue;
    const rg = document.createRange(); rg.selectNodeContents(n);
    if (![...rg.getClientRects()].some(r => r.width > 0.5)) continue;
    total++;
    let e = el, o = 1, vis = getComputedStyle(el).visibility === 'visible';
    while (e && e.nodeType === 1) { o *= parseFloat(getComputedStyle(e).opacity || '1'); e = e.parentElement; }
    if (o < 0.05 || !vis) hidden++;
  }
  return { hidden, total };
}
"""


def verdicts(m):
    """Turn one width's probe into pass or fail per check, with a plain detail."""
    def boxes_txt(xs):
        return ", ".join(f"{b['where']} ({b['inside']}px inside {b['outside']}px)" for b in xs[:3])
    out = {}
    cut = m["nCut"]
    out["page_scroll"] = (not m["pageScroll"] and cut == 0,
                          "none" if not m["pageScroll"] and cut == 0 else
                          (f"page is {m['pageScrollWidth']}px wide in a {m['viewport']}px window" if m["pageScroll"] else "") +
                          (("; " if m["pageScroll"] else "") + f"{cut} element(s) cut off past the edge, first {m['cutPastEdge'][0]['where']} (right edge at {m['cutPastEdge'][0]['right']}px)" if cut else ""))
    out["box_scroll"] = (m["nBoxes"] == 0, "none" if m["nBoxes"] == 0 else f"{m['nBoxes']} box(es): {boxes_txt(m['boxes'])}")
    out["text_floor"] = (m["under"] == 0, "none" if m["under"] == 0 else
                         f"{m['under']} run(s), e.g. " + "; ".join(f"{s['size']}px \"{s['sample']}\" in {s['where']}" for s in m["underSamples"][:3]))
    out["type_sizes"] = (m["nSizes"] <= MAX_SIZES, f"{m['nSizes']}: " + ", ".join(str(s) for s in m["sizes"]))
    wr = m["worstReading"]
    out["contrast_reading"] = (m["failReading"] == 0, "no reading text" if not wr else
                               f"lowest {wr['ratio']}:1 on \"{wr['sample']}\" ({wr['size']}px, {wr['where']})" +
                               (f"; {m['failReading']} run(s) under 4.5" if m["failReading"] else ""))
    wl = m["worstLarge"]
    out["contrast_large"] = (m["failLarge"] == 0, "no text over 43px" if not wl else
                             f"lowest {wl['ratio']}:1 on \"{wl['sample']}\" ({wl['size']}px)" +
                             (f"; {m['failLarge']} run(s) under 3" if m["failLarge"] else ""))
    st = m["smallTargets"]
    out["targets"] = (st == 0, (f"0 of {m['controls']}" if st == 0 else
                                f"{st} of {m['controls']}, e.g. " + "; ".join(f"{t['where']} at {t['h']}px \"{t['text']}\"" for t in m["smallTargetSamples"][:3])) +
                      f" ({m['inlineLinksExempt']} link(s) inside prose, exempt)")
    out["reduced_motion"] = (m["reducedMotion"], "present" if m["reducedMotion"] else "missing")
    out["focus_visible"] = (m["focusVisible"], "present" if m["focusVisible"] else "missing")
    out["selection"] = (m["selection"], "present" if m["selection"] else "missing")
    out["no_dark_mode"] = (not m["darkMode"], "none" if not m["darkMode"] else "a dark-mode rule is present")
    g = m["gradientWhere"]
    out["no_gradient"] = (not m["gradient"], "none" if not m["gradient"] else
                          ", ".join(k for k, v in (("in a stylesheet", g["css"]), ("in a style attribute", g["inlineStyle"]),
                                                   (f"{g['elements']} element(s) painted with one", g["elements"]),
                                                   (f"{g['svg']} SVG gradient(s)", g["svg"])) if v))
    return {k: {"pass": bool(p), "detail": d} for k, (p, d) in out.items()}


def launch(pw):
    if os.path.exists(CHROME):
        return pw.chromium.launch(executable_path=CHROME, headless=True)
    return pw.chromium.launch(headless=True)


def check_page(br, path, widths, out_dir=None, settle_ms=1500, step_wait=120, floor=FLOOR_PX, shots=True, no_js=True):
    path = os.path.abspath(path)
    url = "file://" + path
    res = {}
    for i, w in enumerate(widths):
        h = 900 if w >= 1024 else 844
        ctx = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
        pg = ctx.new_page()
        try:
            pg.goto(url, wait_until="load", timeout=45000)
        except Exception as e:  # a slow CDN font should not stop the read
            print(f"  note: load did not finish cleanly at {w}px ({type(e).__name__}); reading what rendered", file=sys.stderr)
        try:
            pg.evaluate("document.fonts && document.fonts.ready.then(() => 1)")
        except Exception:
            pass
        pg.wait_for_timeout(min(settle_ms, 800))

        def reader_pass(wait):
            y, steps = 0, 0
            total = pg.evaluate("document.documentElement.scrollHeight")
            while y < total and steps < 400:
                pg.evaluate(f"window.scrollTo(0,{y})")
                pg.wait_for_timeout(wait)
                y += int(h * 0.66)
                steps += 1
                total = pg.evaluate("document.documentElement.scrollHeight")
            pg.evaluate(f"window.scrollTo(0,{total})")
            pg.wait_for_timeout(settle_ms)
            pg.evaluate("window.scrollTo(0,0)")
            pg.wait_for_timeout(300)

        reader_pass(step_wait)
        # a late web font can shift the layout under the first pass, so text an
        # entrance never revealed gets one slower second pass before it counts
        hidden_first = pg.evaluate(HIDDEN_NO_JS)["hidden"]
        passes = 1
        if hidden_first and settle_ms >= 500:
            reader_pass(step_wait * 3)
            passes = 2
        first_view_height = pg.evaluate("document.documentElement.scrollHeight")
        shot = {}
        if shots and out_dir:
            shot["top"] = os.path.join(out_dir, f"{w}-top.png")
            shot["full"] = os.path.join(out_dir, f"{w}-full.png")
            pg.screenshot(path=shot["top"], full_page=False)
            pg.screenshot(path=shot["full"], full_page=True)
        opened = pg.evaluate("(() => { const d = [...document.querySelectorAll('details:not([open])')]; d.forEach(x => x.open = true); return d.length; })()")
        if opened:
            pg.wait_for_timeout(400)
        m = pg.evaluate(PROBE, {"floor": floor, "large": LARGE_PX, "target": TARGET_PX})
        ctx.close()
        info = {
            "page_height": first_view_height, "page_height_folds_open": m["pageHeight"], "families": m["families"], "text_runs": m["textRuns"],
            "text_runs_still_hidden": m["hiddenRuns"], "hidden_after_first_reader_pass": hidden_first,
            "reader_passes": passes, "folds_opened_for_the_read": opened,
            "boxes_clipping_content": m["nClipped"], "clipped_samples": m["clippedBoxes"],
            "transition_all": m["transitionAll"], "text_wrap_balance": m["textWrapBalance"],
            "tabular_numerals": m["tabularNums"], "inline_links_exempt": m["inlineLinksExempt"],
            "contrast_not_read": m["contrastSkipped"], "cross_origin_sheets_unread": m["unreadableSheets"],
        }
        if no_js and i == 0:
            c2 = br.new_context(viewport={"width": w, "height": h}, java_script_enabled=False)
            p2 = c2.new_page()
            try:
                p2.goto(url, wait_until="load", timeout=30000)
            except Exception:
                pass
            p2.wait_for_timeout(300)
            info["text_hidden_without_script"] = p2.evaluate(HIDDEN_NO_JS)
            c2.close()
        res[str(w)] = {"checks": verdicts(m), "info": info, "screenshots": shot, "raw": m}
    return res


def print_report(path, res, json_path):
    print(f"page_check · {os.path.abspath(path)}")
    all_ok = True
    for w, r in res.items():
        n_ok = sum(1 for c in r["checks"].values() if c["pass"])
        ok = n_ok == len(CHECKS)
        all_ok &= ok
        print(f"\n{w}px  {'PASS' if ok else 'FAIL'}  {n_ok} of {len(CHECKS)} pass  (page {r['info']['page_height']}px tall)")
        for cid, label in CHECKS:
            c = r["checks"][cid]
            print(f"  {'PASS' if c['pass'] else 'FAIL'}  {label}: {c['detail']}")
        inf = r["info"]
        notes = []
        if inf["transition_all"]:
            notes.append("uses transition: all (finish.md section 3 says never)")
        if inf.get("text_hidden_without_script", {}).get("hidden"):
            t = inf["text_hidden_without_script"]
            notes.append(f"{t['hidden']} of {t['total']} text runs hidden if the script never runs (finish.md section 3)")
        if inf["boxes_clipping_content"]:
            notes.append(f"{inf['boxes_clipping_content']} box(es) clip content without a scroll, first {inf['clipped_samples'][0]['where']}")
        if inf["text_runs_still_hidden"]:
            notes.append(f"{inf['text_runs_still_hidden']} text run(s) still hidden after {inf['reader_passes']} reader pass(es): an entrance that never fired, or text hidden on purpose")
        if inf["folds_opened_for_the_read"]:
            notes.append(f"{inf['folds_opened_for_the_read']} fold(s) opened so folded rows were read too")
        for n in notes:
            print(f"  note  {n}")
        if r["screenshots"]:
            print(f"  shots {r['screenshots']['top']}\n        {r['screenshots']['full']}")
    print(f"\nJSON: {json_path}")
    print("RESULT:", "PASS" if all_ok else "FAIL")
    return all_ok


# ---------------------------------------------------------------- self-test

BASE_CSS = {
    "core": "html{background:#F5F5F5}body{margin:0;padding:0 24px;font:400 18px/1.6 system-ui,sans-serif;color:#1A1A1A;background:#F5F5F5}"
            "h1{font-size:43px;font-weight:400;margin:0}button{min-height:44px;font:inherit;padding:0 16px}"
            ".cta{display:inline-flex;align-items:center;min-height:44px}"
            ".tick{display:flex;align-items:center;min-height:44px;gap:8px}",
    "selection": "::selection{background:#DCE6F7}",
    "focus": ":focus-visible{outline:2px solid #2B5FD9}",
    "motion": "@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important}}",
}
CLEAN_BODY = (
    '<h1>A clean page</h1>'
    '<p>Reading text with an <a href="#x">inline link</a> inside the sentence, which is exempt.</p>'
    '<p style="font-size:57px;color:#888888;margin:0">57</p>'
    '<button>Do it</button> <a class="cta" href="#y">Open the page</a>'
    '<label class="tick"><input type="checkbox"> Done</label>'
    '<svg viewBox="0 0 100 50" width="300" height="150"><text x="5" y="20" font-size="8">24px label</text></svg>'
)


def fixture(body=CLEAN_BODY, drop=(), extra_css="", head=""):
    css = "".join(v for k, v in BASE_CSS.items() if k not in drop) + extra_css
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{head}<style>{css}</style></head><body>{body}</body></html>'


FIXTURES = [
    ("clean page passes every check", fixture(), set()),
    ("16px code fails the floor", fixture(CLEAN_BODY + '<p><code style="font-size:16px">/a/path</code></p>'), {"text_floor"}),
    ("folded 14px text is still read", fixture(CLEAN_BODY + '<details><summary style="min-height:44px">More</summary><p style="font-size:14px">folded</p></details>'), {"text_floor"}),
    ("SVG text drawn at 8px fails the floor", fixture(CLEAN_BODY + '<svg viewBox="0 0 100 50" width="100" height="50"><text x="2" y="20" font-size="8">tiny</text></svg>'), {"text_floor"}),
    ("9 type sizes fail the scale", fixture(CLEAN_BODY + "".join(f'<p style="font-size:{s}px">s{s}</p>' for s in (20, 22, 26, 28, 30))), {"type_sizes"}),
    ("faint 18px text fails reading contrast", fixture(CLEAN_BODY + '<p style="color:#888888">faint reading text</p>'), {"contrast_reading"}),
    ("faint 57px text fails large contrast", fixture(CLEAN_BODY + '<p style="font-size:57px;color:#B3B3B3;margin:0">99</p>'), {"contrast_large"}),
    ("a 30px button fails the target", fixture(CLEAN_BODY + '<button style="min-height:0;height:30px">small</button>'), {"targets"}),
    ("a standalone 30px link fails the target (fix 1)", fixture(CLEAN_BODY + '<p><a href="#z" style="display:inline-block;padding:2px 6px">Open</a></p>'), {"targets"}),
    ("a small checkbox label fails the target", fixture(CLEAN_BODY + '<p><label><input type="checkbox"> tiny</label></p>'), {"targets"}),
    ("a 2000px row scrolls the page", fixture(CLEAN_BODY + '<div style="width:2000px">wide</div>'), {"page_scroll"}),
    ("body clip hides a 2000px row, still caught (fix 2)", fixture(CLEAN_BODY + '<div style="width:2000px">wide</div>', extra_css="body{overflow-x:clip}"), {"page_scroll"}),
    ("a table scrolling inside its box is caught (fix 2)", fixture(CLEAN_BODY + '<div style="overflow-x:auto"><table style="width:1600px"><tr><td>a</td><td>b</td></tr></table></div>', extra_css="body{overflow-x:clip}"), {"box_scroll"}),
    ("no reduced-motion block fails", fixture(drop=("motion",)), {"reduced_motion"}),
    ("no focus ring rule fails", fixture(drop=("focus",)), {"focus_visible"}),
    ("no selection rule fails", fixture(drop=("selection",)), {"selection"}),
    ("a dark-mode block fails", fixture(extra_css="@media (prefers-color-scheme: dark){body{background:#111;color:#eee}}"), {"no_dark_mode"}),
    ("a stylesheet gradient fails", fixture(CLEAN_BODY + '<div class="g">g</div>', extra_css=".g{background:linear-gradient(#fff,#eee)}"), {"no_gradient"}),
    ("a style-attribute gradient fails", fixture(CLEAN_BODY + '<div style="background-image:radial-gradient(#fff,#eee)">g</div>'), {"no_gradient"}),
]


def self_test():
    from playwright.sync_api import sync_playwright
    tmp = tempfile.mkdtemp(prefix="page_check_selftest_")
    bad = 0
    t0 = time.time()
    with sync_playwright() as pw:
        br = launch(pw)
        for i, (name, html, expect) in enumerate(FIXTURES):
            p = os.path.join(tmp, f"fixture-{i:02d}.html")
            with open(p, "w") as f:
                f.write(html)
            res = check_page(br, p, DEFAULT_WIDTHS, settle_ms=80, step_wait=20, shots=False, no_js=False)
            ok = True
            got_all = []
            for w, r in res.items():
                got = {k for k, c in r["checks"].items() if not c["pass"]}
                got_all.append(f"{w}:{','.join(sorted(got)) or 'none'}")
                if got != expect:
                    ok = False
                    for k in sorted(got ^ expect):
                        print(f"        at {w}px {k}: {r['checks'][k]['detail']}")
            bad += 0 if ok else 1
            print(f"  {'ok  ' if ok else 'FAIL'} {name}  (expected {','.join(sorted(expect)) or 'none'}; got {' '.join(got_all)})")
        br.close()
    print(f"\nself-test: {len(FIXTURES) - bad} of {len(FIXTURES)} fixtures behave as expected, {time.time() - t0:.0f}s, fixtures in {tmp}")
    return bad == 0


def main():
    ap = argparse.ArgumentParser(description="Read a page's finish off the render (finish.md section 6).")
    ap.add_argument("page", nargs="?")
    ap.add_argument("--widths", default=",".join(str(w) for w in DEFAULT_WIDTHS))
    ap.add_argument("--json", action="store_true", help="print the JSON to stdout instead of the report")
    ap.add_argument("--out", help="absolute folder for the screenshots and the JSON (default: under the system temp folder)")
    ap.add_argument("--floor", type=float, default=FLOOR_PX, help="type floor in px (default 18, finish.md section 2)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(0 if self_test() else 1)
    if not a.page:
        ap.error("give a page, or --self-test")
    if not os.path.isfile(a.page):
        print(f"page_check: no such file: {a.page}", file=sys.stderr)
        sys.exit(2)
    widths = [int(x) for x in a.widths.split(",") if x.strip()]
    absp = os.path.abspath(a.page)
    if a.out:
        out_dir = os.path.abspath(a.out)
    else:
        key = hashlib.md5(absp.encode()).hexdigest()[:8]
        stem = os.path.splitext(os.path.basename(absp))[0]
        parent = os.path.basename(os.path.dirname(absp))
        out_dir = os.path.join(tempfile.gettempdir(), "page_check", f"{parent}-{stem}-{key}")
    os.makedirs(out_dir, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            br = launch(pw)
            res = check_page(br, absp, widths, out_dir=out_dir, floor=a.floor)
            br.close()
    except Exception as e:
        print(f"page_check: could not render {absp}: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
    for r in res.values():
        r.pop("raw", None) if not a.json else None
    doc = {"page": absp, "checked": time.strftime("%Y-%m-%d %H:%M"), "floor_px": a.floor, "widths": res,
           "pass": all(c["pass"] for r in res.values() for c in r["checks"].values())}
    json_path = os.path.join(out_dir, "page_check.json")
    with open(json_path, "w") as f:
        json.dump(doc, f, indent=2)
    if a.json:
        print(json.dumps(doc, indent=2))
        sys.exit(0 if doc["pass"] else 1)
    ok = print_report(absp, res, json_path)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
