/* Capture QA screenshots of key slides (full fragment reveal states). */
const puppeteer = require("puppeteer-core");
const CHROME = "/tmp/pw-slideshow/chromium-1243/chrome-linux64/chrome";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: "new",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
    defaultViewport: { width: 1600, height: 900 },
  });
  const page = await browser.newPage();
  await page.goto("http://127.0.0.1:8791/index.html", { waitUntil: "networkidle2", timeout: 60000 });
  await sleep(2500);

  const frame = () => page.frames().find((f) => f.url().includes("composition/index.html"));
  const active = () => page.evaluate(() => {
    const el = document.querySelector("hyperframes-slideshow");
    const f = el.querySelector("hyperframes-player").iframeElement;
    const a = f.contentDocument && f.contentDocument.querySelector(".scene-frame.is-active");
    return a ? a.id : null;
  });
  async function nextUntil(target, max = 40) {
    for (let i = 0; i < max; i++) {
      if ((await active()) === target) return true;
      await page.keyboard.press("ArrowRight");
      await sleep(650);
    }
    return false;
  }
  async function revealAll(sceneId, ids) {
    for (let i = 0; i < ids.length + 2; i++) {
      const op = await frame().evaluate((ids) => ids.map((id) => {
        const el = document.getElementById(id);
        return el ? getComputedStyle(el).opacity : "1";
      }), ids);
      if (!op.includes("0")) break;
      if ((await active()) !== sceneId) break;
      await page.keyboard.press("ArrowRight");
      await sleep(650);
    }
  }
  const shot = (n) => page.screenshot({ path: `qa/${n}.png` });

  await sleep(1200);
  await shot("slide01-cover");

  await nextUntil("p2-problems");
  await revealAll("p2-problems", ["p2-c1", "p2-c2", "p2-c3", "p2-c4"]);
  await sleep(800);
  await shot("slide02-problems");

  await nextUntil("p4-solution");
  await revealAll("p4-solution", ["p4-s1", "p4-s2", "p4-s3", "p4-bar"]);
  await sleep(800);
  await shot("slide04-solution");

  // hotspot -> branch
  await page.evaluate(() => {
    const el = document.querySelector("hyperframes-slideshow");
    const p = el.querySelector('.hf-hotspot-pill[data-hotspot-target="arch-detail"]');
    const r = p.getBoundingClientRect();
    window.__qaClick = { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  });
  const c1 = await page.evaluate(() => window.__qaClick);
  await page.mouse.click(c1.x, c1.y);
  await sleep(1200);
  await shot("branch-arch");

  await page.keyboard.press("ArrowLeft");
  await sleep(900);
  await nextUntil("p5-how");
  await revealAll("p5-how", ["p5-a1", "p5-a2", "p5-chips", "p5-bar"]);
  await sleep(800);
  await shot("slide05-how");

  await nextUntil("p9-security");
  await revealAll("p9-security", ["p9-f1", "p9-f2", "p9-f3", "p9-f4", "p9-bar"]);
  await sleep(800);
  await shot("slide09-security");

  // b-compare is branch-only: go home first, then forward to p5, click pill
  for (let i = 0; i < 40; i++) {
    if ((await active()) === "p1-cover") break;
    await page.keyboard.press("ArrowLeft");
    await sleep(500);
  }
  const ok5 = await nextUntil("p5-how");
  if (!ok5) console.log("warn: p5-how not reached");
  await page.evaluate(() => {
    const el = document.querySelector("hyperframes-slideshow");
    const p = el.querySelector('.hf-hotspot-pill[data-hotspot-target="compare-detail"]');
    if (!p) { window.__qaClick = null; return; }
    const r = p.getBoundingClientRect();
    window.__qaClick = { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  });
  const c2 = await page.evaluate(() => window.__qaClick);
  if (c2) {
    await page.mouse.click(c2.x, c2.y);
    await sleep(1200);
  }
  await shot("branch-compare");

  await nextUntil("p10-next");
  await revealAll("p10-next", ["p10-contact", "p10-close"]);
  await sleep(800);
  await shot("slide10-next");

  await browser.close();
  console.log("QA screenshots saved to qa/");
})().catch((e) => { console.error(e); process.exit(1); });
