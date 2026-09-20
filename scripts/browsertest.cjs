/* Browser runtime test for the standalone slideshow harness (0.8.41).
 * Probes (verified via scripts/probe.cjs):
 *  - scene manifest: parent <hyperframes-player>.scenes (12 entries)
 *  - playhead: iframe window.__timelines.root.time()
 *  - active slide: iframe .scene-frame.is-active id
 *  - fragments: computed opacity of .frag ids
 *  - hotspot pills: light-DOM .hf-hotspot-pill[data-hotspot-target=...]
 */
const puppeteer = require("puppeteer-core");

const CHROME = "/tmp/pw-slideshow/chromium-1243/chrome-linux64/chrome";
const BASE = process.env.DECK_URL || "http://127.0.0.1:8791/index.html";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: "new",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
    defaultViewport: { width: 1600, height: 900 },
  });
  const page = await browser.newPage();
  page.on("pageerror", (e) => console.log("PAGE-ERROR:", String(e).slice(0, 200)));
  const results = [];
  const ok = (name, cond, extra = "") => results.push([cond ? "PASS" : "FAIL", name, extra]);

  await page.goto(BASE, { waitUntil: "networkidle2", timeout: 60000 });
  await sleep(2500);

  const frame = () => page.frames().find((f) => f.url().includes("composition/index.html"));

  async function activeSlide() {
    return page.evaluate(() => {
      const el = document.querySelector("hyperframes-slideshow");
      const f = el.querySelector("hyperframes-player").iframeElement;
      if (!f || !f.contentDocument) return null;
      const a = f.contentDocument.querySelector(".scene-frame.is-active");
      return a ? a.id : null;
    });
  }
  async function counter() {
    return page.evaluate(() => {
      const el = document.querySelector("hyperframes-slideshow");
      const m = (el.querySelector("[data-hf-chrome]") || { textContent: "" }).textContent.match(/(\d+)\s*\/\s*(\d+)/);
      return m ? { cur: +m[1], total: +m[2] } : null;
    });
  }
  async function fragOpacities(ids) {
    const f = frame();
    return f.evaluate((ids) => ids.map((id) => {
      const el = document.getElementById(id);
      return el ? getComputedStyle(el).opacity : null;
    }), ids);
  }
  async function pressKey(k) { await page.keyboard.press(k); await sleep(700); }
  async function nextUntil(target, max = 40) {
    for (let i = 0; i < max; i++) {
      if ((await activeSlide()) === target) return true;
      await pressKey("ArrowRight");
    }
    return (await activeSlide()) === target;
  }
  async function pill(sel) {
    return page.evaluate((sel) => {
      const el = document.querySelector("hyperframes-slideshow");
      const p = el.querySelector(sel);
      if (!p) return null;
      const r = p.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2, text: p.textContent.trim().slice(0, 40) };
    }, sel);
  }

  // ---- 1. manifest & timeline registration ----
  const manifest = await page.evaluate(() => {
    const p = document.querySelector("hyperframes-player");
    try { return (p.scenes || []).map((s) => s.id || s.compositionId); } catch (e) { return []; }
  });
  ok("12 scenes resolved in player manifest", manifest.length === 12,
    `got ${manifest.length}: ${manifest.join(",")}`);

  const f0 = frame();
  const tlKeys = await f0.evaluate(() => Object.keys(window.__timelines || {}));
  ok("timelines registered (root + 12 scenes)", tlKeys.length === 13, `got ${tlKeys.length}`);

  // ---- 2. slide 1 ----
  ok("slide 1 is p1-cover", (await activeSlide()) === "p1-cover", await activeSlide());
  let c = await counter();
  ok("counter 1/10", c && c.cur === 1 && c.total === 10, JSON.stringify(c));

  // ---- 3. p2 fragments ----
  await pressKey("ArrowRight");
  ok("slide 2 is p2-problems", (await activeSlide()) === "p2-problems", await activeSlide());
  let op = await fragOpacities(["p2-c1", "p2-c2", "p2-c3", "p2-c4"]);
  ok("p2 entry: only fragment 1 visible", op[0] === "1" && op[1] === "0", JSON.stringify(op));
  await pressKey("ArrowRight");
  op = await fragOpacities(["p2-c1", "p2-c2", "p2-c3", "p2-c4"]);
  ok("p2: fragment 2 revealed on 2nd next", op[1] === "1" && op[2] === "0", JSON.stringify(op));
  await pressKey("ArrowRight");
  await pressKey("ArrowRight");
  op = await fragOpacities(["p2-c1", "p2-c2", "p2-c3", "p2-c4"]);
  ok("p2: all 4 fragments revealed", op.every((o) => o === "1"), JSON.stringify(op));

  // ---- 4. p4 hotspot: arch-detail ----
  ok("nextUntil p4-solution", await nextUntil("p4-solution"), await activeSlide());
  const pill1 = await pill('.hf-hotspot-pill[data-hotspot-target="arch-detail"]');
  ok("arch-detail pill rendered on p4", !!pill1, JSON.stringify(pill1));
  if (pill1) {
    await page.mouse.click(pill1.x, pill1.y);
    await sleep(1000);
    ok("branch entered: b-arch active", (await activeSlide()) === "b-arch", await activeSlide());
    c = await counter();
    ok("branch counter scoped (1/1)", c && c.cur === 1 && c.total === 1, JSON.stringify(c));
    await pressKey("ArrowLeft");
    ok("prev pops back to p4-solution", (await activeSlide()) === "p4-solution", await activeSlide());
  }
  // in-composition clickable card -> compare bridge
  // (reveal all p4 fragments first, one right at a time, verifying state each time)
  op = await fragOpacities(["p4-s1", "p4-s2", "p4-s3", "p4-bar"]);
  while (op.includes("0")) {
    await pressKey("ArrowRight");
    if ((await activeSlide()) !== "p4-solution") break;
    op = await fragOpacities(["p4-s1", "p4-s2", "p4-s3", "p4-bar"]);
  }
  ok("p4 fully revealed", op.every((o) => o === "1"), JSON.stringify(op));
  const fr = frame();
  await fr.evaluate(() => {
    const el = document.querySelector('[data-hotspot="arch-detail"]');
    el.scrollIntoView({ block: "center" });
  });
  await sleep(400);
  await fr.click('[data-hotspot="arch-detail"]').catch((e) => console.log("frame.click err:", String(e).slice(0, 120)));
  await sleep(1000);
  ok("in-composition card enters b-arch", (await activeSlide()) === "b-arch", await activeSlide());
  await pressKey("ArrowLeft");
  ok("back on p4 after card branch", (await activeSlide()) === "p4-solution", await activeSlide());

  // ---- 5. p5 hotspot: compare-detail ----
  ok("nextUntil p5-how", await nextUntil("p5-how"), await activeSlide());
  const pill2 = await pill('.hf-hotspot-pill[data-hotspot-target="compare-detail"]');
  ok("compare-detail pill rendered on p5", !!pill2, JSON.stringify(pill2));
  if (pill2) {
    await page.mouse.click(pill2.x, pill2.y);
    await sleep(1000);
    ok("branch entered: b-compare active", (await activeSlide()) === "b-compare", await activeSlide());
    await pressKey("ArrowLeft");
    ok("prev pops back to p5-how", (await activeSlide()) === "p5-how", await activeSlide());
  }

  // ---- 6. walk to p10 ----
  ok("nextUntil p10-next", await nextUntil("p10-next"), await activeSlide());
  c = await counter();
  ok("counter 10/10", c && c.cur === 10 && c.total === 10, JSON.stringify(c));
  const t = await f0.evaluate(() => (window.__timelines && window.__timelines.root) ? window.__timelines.root.time() : -1);
  ok("playhead in p10 range [90,100)", t >= 90 && t < 100, `t=${t.toFixed(2)}`);

  // ---- 7. back navigation to slide 1 ----
  for (let i = 0; i < 40; i++) {
    if ((await activeSlide()) === "p1-cover") break;
    await pressKey("ArrowLeft");
  }
  ok("ArrowLeft returns to slide 1", (await activeSlide()) === "p1-cover", await activeSlide());

  await browser.close();
  let fails = 0;
  for (const [st, name, extra] of results) {
    if (st === "FAIL") fails++;
    console.log(`${st}  ${name}${extra ? "   | " + extra : ""}`);
  }
  console.log(fails === 0 ? "\nALL BROWSER TESTS PASSED" : `\n${fails} TEST(S) FAILED`);
  process.exit(fails === 0 ? 0 : 1);
}

main().catch((e) => { console.error(e); process.exit(1); });
