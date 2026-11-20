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
  document.querySelector("#source").value = "[[1,null]]";
  document.querySelector("form").requestSubmit();
  if (canvases || !document.querySelector("#view svg")) throw Error("expected SVG-only redraw");
  if (document.querySelector("#raster").hidden) throw Error("PNG action is hidden");
  const download = new Promise(resolve => {
    HTMLAnchorElement.prototype.click = function () { resolve([this.download, this.href]); };
  });
  document.querySelector("#size").value = "512";
  document.querySelector("#png").click();
  const [name,url] = await download;
  const blob = await (await fetch(url)).blob();
  const image = await createImageBitmap(blob);
  if (canvases !== 1 || name !== "heatmap.png" || blob.type !== "image/png" ||
      image.width !== 512 || image.height !== 128) throw Error("PNG download or dimensions");
  const ctx = new OffscreenCanvas(512,128).getContext("2d");
  ctx.drawImage(image,0,0);
  if (ctx.getImageData(10,10,1,1).data[3] !== 255 ||
      ctx.getImageData(500,10,1,1).data[3] !== 0) throw Error("missing cell transparency");
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
