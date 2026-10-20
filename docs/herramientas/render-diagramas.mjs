// Renderiza docs/diagramas/*.mmd a docs/imagenes/diagramas/*.png con Mermaid y Chrome.
// Uso: npm run diagramas   (requiere Google Chrome instalado; no descarga navegadores)
import { chromium } from "playwright";
import { readdir, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const aqui = path.dirname(fileURLToPath(import.meta.url));
const origen = path.resolve(aqui, "../diagramas");
const destino = path.resolve(aqui, "../imagenes/diagramas");
const mermaidJs = path.resolve(aqui, "node_modules/mermaid/dist/mermaid.min.js");

const navegador = await chromium.launch({ channel: "chrome" });
const pagina = await navegador.newPage({ deviceScaleFactor: 2, viewport: { width: 1600, height: 1200 } });
await pagina.setContent(`<!doctype html><html><body style="margin:0;background:#fff">
  <div id="lienzo" style="display:inline-block;padding:16px;background:#fff"></div></body></html>`);
await pagina.addScriptTag({ path: mermaidJs });
await pagina.evaluate(() => {
  window.mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    fontFamily: "Arial, Helvetica, sans-serif",
    themeVariables: {
      primaryColor: "#e8f1fa",
      primaryBorderColor: "#0b3d6e",
      primaryTextColor: "#10233a",
      lineColor: "#3c4e63",
      fontSize: "15px",
    },
    flowchart: { htmlLabels: true, curve: "basis" },
    sequence: { mirrorActors: false },
  });
});

const archivos = (await readdir(origen)).filter((f) => f.endsWith(".mmd")).sort();
for (const archivo of archivos) {
  const fuente = await readFile(path.join(origen, archivo), "utf8");
  await pagina.evaluate(async (codigo) => {
    const lienzo = document.getElementById("lienzo");
    const { svg } = await window.mermaid.render("d" + Date.now(), codigo);
    lienzo.innerHTML = svg;
    // Mermaid limita el SVG al ancho del contenedor; se fija su tamano natural.
    const el = lienzo.querySelector("svg");
    const vb = el.viewBox.baseVal;
    el.removeAttribute("style");
    el.setAttribute("width", String(vb.width));
    el.setAttribute("height", String(vb.height));
  }, fuente);
  const salida = path.join(destino, archivo.replace(/\.mmd$/, ".png"));
  await pagina.locator("#lienzo").screenshot({ path: salida });
  console.log("ok", path.basename(salida));
}
await navegador.close();
