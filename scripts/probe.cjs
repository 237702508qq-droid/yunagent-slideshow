/* Probe: where do the runtime actually expose scenes manifest & playhead? */
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

  const iframeWin = await page.evaluate(() => {
    const el = document.querySelector("hyperframes-slideshow");
    const p = el.querySelector("hyperframes-player");
    const f = p && p.iframeElement;
    if (!f) return { err: "no iframeElement" };
    const w = f.contentWindow;
    const keys = Object.keys(w).filter((k) => /hf|hyper|clip|scene|player|manifest/i.test(k));
    return { keys, hasClipManifest: !!w.__clipManifest, clipKeys: w.__clipManifest ? Object.keys(w.__clipManifest) : null };
  });
  console.log("IFRAME KEYS:", JSON.stringify(iframeWin, null, 1));

  // parent player element internals
  const parentProbe = await page.evaluate(() => {
    const el = document.querySelector("hyperframes-slideshow");
    const p = el.querySelector("hyperframes-player");
    const out = { playerOwnKeys: [], scenesType: typeof p.scenes };
    try {
      let proto = Object.getPrototypeOf(p);
      for (let i = 0; i < 3 && proto; i++) {
        out.playerOwnKeys.push(...Object.getOwnPropertyNames(proto).filter((k) => /scene|manifest|time|duration/i.test(k)));
        proto = Object.getPrototypeOf(proto);
      }
    } catch (e) { out.err = String(e); }
    try { out.scenesSample = p.scenes ? (Array.isArray(p.scenes) ? p.scenes.length : Object.keys(p.scenes).length) : null; } catch (e) {}
    return out;
  });
  console.log("PLAYER PROBE:", JSON.stringify(parentProbe, null, 1));

  // controller probe
  const ctrlProbe = await page.evaluate(() => {
    const el = document.querySelector("hyperframes-slideshow");
    const c = el.controller;
    if (!c) return { controller: null };
    const out = { controller: true, keys: Object.keys(c).slice(0, 40) };
    try { out.pos = JSON.parse(JSON.stringify(c.position || c.state || null)); } catch (e) { out.pos = String(e); }
    return out;
  });
  console.log("CONTROLLER PROBE:", JSON.stringify(ctrlProbe, null, 1));

  // root timeline time inside iframe (playhead alternative)
  const f = page.frames().find((fr) => fr.url().includes("composition/index.html"));
  const tlTime = f ? await f.evaluate(() => window.__timelines && window.__timelines.root ? window.__timelines.root.time() : -1) : -1;
  console.log("root timeline time:", tlTime);

  // scene store candidates inside iframe
  const sceneStore = f ? await f.evaluate(() => {
    const w = window;
    const out = {};
    for (const k of ["__hfScenes", "__clipManifest", "__hfRuntime", "hfRuntime", "__hyperframes"]) {
      if (w[k]) out[k] = typeof w[k] === "object" ? Object.keys(w[k]).slice(0, 12) : typeof w[k];
    }
    // any global with .scenes array
    for (const k of Object.keys(w)) {
      try {
        const v = w[k];
        if (v && typeof v === "object" && Array.isArray(v.scenes) && v.scenes.length > 3) {
          out["scenes@" + k] = v.scenes.map((s) => s.id || s.compositionId).slice(0, 14);
        }
      } catch (e) {}
    }
    return out;
  }) : {};
  console.log("SCENE STORE:", JSON.stringify(sceneStore, null, 1));

  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
