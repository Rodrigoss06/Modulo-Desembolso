import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_URL, COOKIE_SEGURA, COOKIE_SESION, TOKEN_URL } from "@/lib/servidor";

// Obtiene el JWT de Seguridad y lo guarda en una cookie httpOnly: el navegador nunca ve el token.
export async function POST(request: Request) {
  const { usuario, contrasena } = (await request.json()) as { usuario?: string; contrasena?: string };
  if (!usuario || !contrasena) {
    return NextResponse.json({ codigo: "VALIDACION_ENTRADA", mensaje: "Ingrese usuario y contraseña" }, { status: 422 });
  }
  let respuesta: Response;
  try {
    respuesta = await fetch(TOKEN_URL, {
      method: "POST",
      body: new URLSearchParams({ grant_type: "password", username: usuario, password: contrasena }),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ codigo: "DEPENDENCIA_NO_DISPONIBLE", mensaje: "El servicio de Seguridad no está disponible" }, { status: 503 });
  }
  if (!respuesta.ok) {
    return NextResponse.json({ codigo: "CREDENCIALES_INVALIDAS", mensaje: "Usuario o contraseña incorrectos" }, { status: 401 });
  }
  const { access_token, expires_in } = (await respuesta.json()) as { access_token: string; expires_in: number };
  const sesion = await fetch(`${API_URL}/api/v1/sesion`, {
    headers: { Authorization: `Bearer ${access_token}` },
    cache: "no-store",
  }).catch(() => null);
  if (!sesion || !sesion.ok) {
    return NextResponse.json({ codigo: "DEPENDENCIA_NO_DISPONIBLE", mensaje: "La API de Desembolso no está disponible" }, { status: 503 });
  }
  (await cookies()).set(COOKIE_SESION, access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: COOKIE_SEGURA,
    path: "/",
    maxAge: expires_in,
  });
  return NextResponse.json(await sesion.json());
}
