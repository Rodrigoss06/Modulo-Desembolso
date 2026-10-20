import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { COOKIE_SESION } from "@/lib/servidor";

async function cerrar(request: Request) {
  (await cookies()).delete(COOKIE_SESION);
  return NextResponse.redirect(new URL("/login", request.url), { status: 303 });
}

export const GET = cerrar;
export const POST = cerrar;
