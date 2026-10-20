// Captura las pantallas del modulo para el informe (docs/imagenes/capturas/*.png).
// Requiere el entorno local levantado: simulador (9000), API (8000) y frontend (3000), con las tablas des_*
// vacias. La API debe iniciarse con RECUPERACION_INTERVALO_SEG y ENTREGA_INTERVALO_SEG altos (300): el
// guion ejecuta la recuperacion y las entregas a demanda para que cada captura muestre un estado estable.
// Uso: npm run capturas
import { chromium } from "playwright";
import { fileURLToPath } from "node:url";
import path from "node:path";

const WEB = process.env.WEB_URL ?? "http://localhost:3000";
const API = process.env.API_URL ?? "http://127.0.0.1:8000";
const SIM = process.env.SIM_URL ?? "http://127.0.0.1:9000";
const salida = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../imagenes/capturas");

const sim = (ruta, cuerpo) =>
  fetch(`${SIM}${ruta}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cuerpo ?? {}) });

async function tokenSupervisor() {
  const r = await fetch(`${SIM}/seguridad/v1/token`, {
    method: "POST",
    body: new URLSearchParams({ grant_type: "password", username: "supervisor2", password: "Demo2026!" }),
  });
  return (await r.json()).access_token;
}
const token = await tokenSupervisor();
const entregar = () =>
  fetch(`${API}/api/v1/operacion/entregas`, { method: "POST", headers: { Authorization: `Bearer ${token}` } }).then((r) => r.json());

const navegador = await chromium.launch({ channel: "chrome" });
const opciones = { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5, locale: "es-PE" };

async function nuevaSesion(usuario) {
  const contexto = await navegador.newContext(opciones);
  const pagina = await contexto.newPage();
  await pagina.goto(`${WEB}/login`);
  await pagina.fill("#usuario", usuario);
  await pagina.fill("#contrasena", "Demo2026!");
  await pagina.getByRole("button", { name: "Ingresar" }).click();
  await pagina.waitForURL("**/creditos");
  return pagina;
}

async function capturar(pagina, nombre, opcionesCaptura = {}) {
  await pagina.evaluate(() => window.scrollTo(0, 0));
  await pagina.waitForTimeout(400);
  await pagina.screenshot({ path: path.join(salida, nombre), ...opcionesCaptura });
  console.log("ok", nombre);
}

async function buscar(pagina, documento) {
  await pagina.goto(`${WEB}/creditos`);
  await pagina.fill("#valor", documento);
  await pagina.getByRole("button", { name: "Buscar" }).click();
  await pagina.getByText("Resultados (").waitFor();
}

async function prepararYValidar(pagina, documento, cuentaEnmascarada) {
  await buscar(pagina, documento);
  await pagina.getByRole("button", { name: "Preparar desembolso" }).click();
  await pagina.waitForURL("**/ordenes/*");
  await pagina.getByText(cuentaEnmascarada).first().waitFor();
  await pagina.getByRole("button", { name: "Validar identidad" }).click();
  await pagina.getByRole("button", { name: "Validar nuevamente" }).waitFor();
  await pagina.getByRole("button", { name: new RegExp(cuentaEnmascarada.replace(/\*/g, "\\*")) }).click();
  await pagina.getByText("Seleccionada").waitFor();
}

async function confirmar(pagina, esperado) {
  await pagina.getByRole("button", { name: "Continuar a confirmación" }).click();
  await pagina.getByRole("button", { name: "Confirmar desembolso" }).click();
  await pagina.getByText(esperado).waitFor({ timeout: 20000 });
}

// 1. Inicio de sesion
{
  const contexto = await navegador.newContext(opciones);
  const pagina = await contexto.newPage();
  await pagina.goto(`${WEB}/login`);
  await capturar(pagina, "01_login.png");
  await contexto.close();
}

const operador = await nuevaSesion("operador1");

// 2-6. Flujo completo: consulta, preparacion, confirmacion, resultado y constancia
await buscar(operador, "70000001");
await capturar(operador, "02_consulta_creditos.png");
await operador.getByRole("button", { name: "Preparar desembolso" }).click();
await operador.waitForURL("**/ordenes/*");
await operador.getByText("****4521").first().waitFor();
await operador.getByRole("button", { name: "Validar identidad" }).click();
await operador.getByRole("button", { name: "Validar nuevamente" }).waitFor();
await operador.getByRole("button", { name: /\*\*\*\*4521/ }).click();
await operador.getByText("Seleccionada").waitFor();
await capturar(operador, "03_preparacion.png", { fullPage: true });
await operador.locator("section", { hasText: "Cuenta destino" }).first().screenshot({ path: path.join(salida, "08_moneda_distinta.png") });
console.log("ok 08_moneda_distinta.png");
const urlOrdenA = operador.url();
await operador.getByRole("button", { name: "Continuar a confirmación" }).click();
await operador.getByRole("button", { name: "Confirmar desembolso" }).waitFor();
await capturar(operador, "04_confirmacion.png");
await operador.getByRole("button", { name: "Confirmar desembolso" }).click();
await operador.getByText("Desembolso confirmado").waitFor({ timeout: 20000 });
await entregar();
await operador.reload();
await operador.getByText(/ACU-\d{4}-\d+/).waitFor();
await capturar(operador, "05_resultado.png");
await operador.getByRole("link", { name: "Ver constancia" }).click();
await operador.getByText("Constancia de desembolso").waitFor();
await capturar(operador, "06_constancia.png", { fullPage: true });

// 7. Resultado incierto: Cuentas registra el abono pero la respuesta se pierde
await sim("/_sim/escenarios", { cobranza_caida: true });
await prepararYValidar(operador, "70000005", "****5563");
await confirmar(operador, "Resultado en verificación");
await capturar(operador, "07_por_verificar.png");

// Ordenes adicionales para el historial y el monitor
await prepararYValidar(operador, "70000008", "****8856");
await confirmar(operador, "Desembolso confirmado");
await prepararYValidar(operador, "70000006", "****6678");
await confirmar(operador, "Desembolso rechazado");
await buscar(operador, "70000007");
await operador.getByRole("button", { name: "Preparar desembolso" }).click();
await operador.waitForURL("**/ordenes/*");
await operador.getByRole("button", { name: "Validar identidad" }).click();
await operador.getByText("RECHAZADA").first().waitFor();
await entregar(); // Cobranza caida: la entrega de DES-...-000003 queda PENDIENTE con su error

// 11. Monitor operativo del supervisor
const supervisor = await nuevaSesion("supervisor1");
await supervisor.goto(`${WEB}/operacion`);
await supervisor.getByText("Órdenes con resultado incierto").waitFor();
await supervisor.getByText("POR VERIFICAR").first().waitFor();
await capturar(supervisor, "11_monitor.png");

// Recuperacion y entrega pendientes
await supervisor.getByRole("button", { name: "Ejecutar recuperación" }).click();
await supervisor.getByText(/Recuperación: \d+ revisadas/).waitFor();
await sim("/_sim/escenarios", { cobranza_caida: false });
await supervisor.waitForTimeout(6000); // espera creciente del primer reintento (5 s)
await supervisor.getByRole("button", { name: "Ejecutar entregas" }).click();
await supervisor.getByText(/Entregas: \d+ enviadas/).waitFor();

// 9. Historial
await supervisor.goto(`${WEB}/ordenes`);
await supervisor.getByText("órdenes").first().waitFor();
await capturar(supervisor, "09_historial.png");

// 10. Detalle con validaciones y bitacora
await supervisor.goto(urlOrdenA);
await supervisor.getByText("Trazabilidad").waitFor();
await supervisor.getByRole("button", { name: "Ver bitácora" }).click();
await supervisor.getByText("Bitácora (solo inserción)").waitFor();
await supervisor.locator("section", { hasText: "Trazabilidad" }).last().screenshot({ path: path.join(salida, "10_detalle_auditoria.png") });
console.log("ok 10_detalle_auditoria.png");

// 12. Conciliacion
await supervisor.goto(`${WEB}/conciliacion`);
await supervisor.getByRole("button", { name: "Conciliar" }).click();
await supervisor.getByText(/Conciliado|diferencias/).first().waitFor();
await capturar(supervisor, "12_conciliacion.png");

// 13. OpenAPI
{
  const contexto = await navegador.newContext(opciones);
  const pagina = await contexto.newPage();
  await pagina.goto(`${API}/docs`);
  await pagina.getByText("CU-02/03 Órdenes").first().waitFor();
  await capturar(pagina, "13_swagger.png");
  await contexto.close();
}

await navegador.close();
