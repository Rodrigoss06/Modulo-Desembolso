import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Marco } from "@/components/Marco";
import { ProveedorSesion } from "@/lib/sesion";
import { API_URL, COOKIE_SESION } from "@/lib/servidor";
import type { Sesion } from "@/lib/tipos";

async function obtenerSesion(): Promise<Sesion | null> {
  const token = (await cookies()).get(COOKIE_SESION)?.value;
  if (!token) return null;
  try {
    const r = await fetch(`${API_URL}/api/v1/sesion`, { headers: { Authorization: `Bearer ${token}` }, cache: "no-store" });
    return r.ok ? ((await r.json()) as Sesion) : null;
  } catch {
    return null;
  }
}

export default async function LayoutAplicacion({ children }: { children: React.ReactNode }) {
  const sesion = await obtenerSesion();
  if (!sesion) redirect("/api/auth/logout");
  return (
    <ProveedorSesion sesion={sesion}>
      <Marco>{children}</Marco>
    </ProveedorSesion>
  );
}
