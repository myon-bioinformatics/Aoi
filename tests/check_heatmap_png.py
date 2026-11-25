"""Exercise the built page in a local ChromeDriver session (stdlib only)."""
import json
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


def command(method, path, data=None):
    body = None if data is None else json.dumps(data).encode()
    request = Request("http://127.0.0.1:9515" + path, data=body, method=method,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=40) as response:
        return json.load(response)["value"]


CHECK = """
const done = arguments[0];
(async () => {
  let canvases = 0;
  const create = document.createElement.bind(document);
  document.createElement = (tag, ...args) => {
    if (tag === "canvas") canvases++;
    return create(tag, ...args);
  };

  // 1. Pure grid PNG export (axes unchecked): exact 512x128 and transparent null cell
  document.querySelector("#export-axes").checked = false;
  document.querySelector("#source").value = "[[1,null]]";
  document.querySelector("form").requestSubmit();
  if (canvases || !document.querySelector("#view svg")) throw Error("expected SVG-only redraw");
  if (document.querySelector("#raster").hidden) throw Error("PNG action is hidden");
  let downloadPromise = new Promise(resolve => {
    HTMLAnchorElement.prototype.click = function () { resolve([this.download, this.href]); };
  });
  document.querySelector("#size").value = "512";
  document.querySelector("#png").click();
  let [name, url] = await downloadPromise;
  let blob = await (await fetch(url)).blob();
  let image = await createImageBitmap(blob);
  if (canvases !== 1 || name !== "heatmap.png" || blob.type !== "image/png" ||
      image.width !== 512 || image.height !== 128) throw Error("PNG download or dimensions: " + image.width + "x" + image.height);
  let ctx = new OffscreenCanvas(512, 128).getContext("2d");
  ctx.drawImage(image, 0, 0);
  if (ctx.getImageData(10, 10, 1, 1).data[3] !== 255 ||
      ctx.getImageData(500, 10, 1, 1).data[3] !== 0) throw Error("missing cell transparency");

  // 2. Labeled SVG/PNG export (axes checked) + CSV sample + transpose + zmin/zmax + cell click + Base64
  document.querySelector("#export-axes").checked = true;
  document.querySelector("[data-sample='csv']").click();
  if (!document.querySelector("#status").textContent.includes("3行 × 3列")) throw Error("CSV parse failed");
  if (!document.querySelector("#view svg").textContent.includes("朝")) throw Error("missing axis labels in SVG");

  document.querySelector("#palette").value = "cividis";
  document.querySelector("#palette").dispatchEvent(new Event("change"));
  if (!document.querySelector("#status").textContent.includes("Cividis")) throw Error("palette switch failed");

  document.querySelector("#transpose").click();
  document.querySelector("#zmin").value = "0";
  document.querySelector("#zmax").value = "40";
  document.querySelector("#zmax").dispatchEvent(new Event("change"));
  if (!document.querySelector("#stat-range").textContent.includes("0 – 40")) throw Error("zmin/zmax failed");

  const firstCell = document.querySelector("#view rect[data-cell]");
  firstCell.dispatchEvent(new MouseEvent("click", { bubbles: true }));
  if (!document.querySelector("#cell-info").textContent.includes("選択セル")) throw Error("cell inspector failed");

  document.querySelector("#base64").click();
  for (let i = 0; i < 40 && !document.querySelector("#b64text").value; i++) {
    await new Promise(r => setTimeout(r, 50));
  }
  if (!document.querySelector("#b64text").value.startsWith("data:image/png;base64,")) {
    throw Error("Base64 PNG export failed");
  }

  // 3. PSWB theme switch
  const themeSel = document.querySelector("[data-ui-theme-switch]");
  themeSel.value = "github-like";
  themeSel.dispatchEvent(new Event("change"));
  if (document.body.dataset.uiTheme !== "github-like") throw Error("PSWB theme switch failed");

  // 4. Wide matrix stays inside mobile viewport (no document-level horizontal overflow)
  const wideRow = Array.from({ length: 24 }, (_, i) => i);
  document.querySelector("#source").value = JSON.stringify([wideRow, wideRow]);
  document.querySelector("#format").value = "json";
  document.querySelector("form").requestSubmit();
  if (document.documentElement.scrollWidth > window.innerWidth) {
    throw Error("horizontal overflow on mobile: " + document.documentElement.scrollWidth + " > " + window.innerWidth);
  }

  done("ok");
})().catch(error => done(String(error)));
"""


def main():
    driver = subprocess.Popen(["chromedriver", "--port=9515"])
    try:
        for _ in range(100):
            try:
                command("GET", "/status")
                break
            except URLError:
                time.sleep(0.1)
        session = command("POST", "/session", {"capabilities": {"alwaysMatch": {
            "browserName": "chrome", "goog:chromeOptions": {"args": ["--headless", "--no-sandbox"]}
        }}})["sessionId"]
        path = "/session/" + session
        try:
            command("POST", path + "/window/rect", {"width": 390, "height": 844})
            command("POST", path + "/url", {"url": Path(sys.argv[1]).resolve().as_uri()})
            result = command("POST", path + "/execute/async", {"script": CHECK, "args": []})
            assert result == "ok", result
        finally:
            command("DELETE", path)
    finally:
        driver.terminate()
        driver.wait()


if __name__ == "__main__":
    main()
