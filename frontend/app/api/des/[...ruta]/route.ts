import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { API_URL, COOKIE_SESION } from "@/lib/servidor";

// BFF: reenvia a la API de Desembolso agregando el token de la cookie y la correlacion.
// En Testing/Produccion API_URL apunta a la ruta del modulo en el Bus de Servicios.
async function reenviar(request: NextRequest, ctx: { params: Promise<{ ruta: string[] }> }) {
  const { ruta } = await ctx.params;
  const token = (await cookies()).get(COOKIE_SESION)?.value;
  if (!token) {
    return NextResponse.json({ codigo: "NO_AUTENTICADO", mensaje: "La sesión expiró" }, { status: 401 });
  }
  const destino = new URL(`${API_URL}/api/v1/${ruta.map(encodeURIComponent).join("/")}`);
  destino.search = request.nextUrl.search;
  const cabeceras: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    "X-Correlation-ID": request.headers.get("x-correlation-id") ?? crypto.randomUUID(),
  };
  const clave = request.headers.get("x-idempotency-key");
  if (clave) cabeceras["X-Idempotency-Key"] = clave;
  let cuerpo: string | undefined;
  if (request.method !== "GET") {
    cuerpo = await request.text();
    cabeceras["Content-Type"] = "application/json";
  }
  try {
    const r = await fetch(destino, { method: request.method, headers: cabeceras, body: cuerpo, cache: "no-store" });
    const respuesta = new NextResponse(await r.text(), {
      status: r.status,
      headers: { "Content-Type": r.headers.get("content-type") ?? "application/json" },
    });
    for (const nombre of ["x-correlation-id", "idempotent-replay"]) {
      const valor = r.headers.get(nombre);
      if (valor) respuesta.headers.set(nombre, valor);
    }
    return respuesta;
  } catch {
    return NextResponse.json({ codigo: "DEPENDENCIA_NO_DISPONIBLE", mensaje: "La API de Desembolso no está disponible" }, { status: 503 });
  }
}

export const GET = reenviar;
export const POST = reenviar;
export const PUT = reenviar;
