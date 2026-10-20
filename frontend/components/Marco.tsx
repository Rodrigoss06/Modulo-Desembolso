"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { esSupervision, useSesion } from "@/lib/sesion";

const ROL: Record<string, string> = {
  OPERADOR_AGENCIA: "Operador de agencia",
  SUPERVISOR: "Supervisor",
  AUDITOR: "Auditor",
};

export function Marco({ children }: { children: React.ReactNode }) {
  const sesion = useSesion();
  const ruta = usePathname();
  const enlaces = [
    { href: "/creditos", texto: "Créditos" },
    { href: "/ordenes", texto: "Órdenes" },
    ...(esSupervision(sesion)
      ? [
          { href: "/operacion", texto: "Operación" },
          { href: "/conciliacion", texto: "Conciliación" },
        ]
      : []),
    { href: "/reversiones", texto: "Reversiones" },
  ];
  return (
    <div className="min-h-screen">
      <header className="no-imprimir bg-marca-800 text-white shadow">
        <div className="mx-auto flex max-w-7xl items-center gap-8 px-6 py-3">
          <Link href="/creditos" className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-white text-sm font-black text-marca-800">BNA</span>
            <span className="leading-tight">
              <span className="block text-sm font-semibold">Banco Nacional de Arequipa</span>
              <span className="block text-xs text-marca-100">Desembolso de Créditos · Módulo 13</span>
            </span>
          </Link>
          <nav className="flex flex-1 gap-1">
            {enlaces.map((e) => {
              const activo = ruta === e.href || ruta.startsWith(`${e.href}/`);
              return (
                <Link
                  key={e.href}
                  href={e.href}
                  className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                    activo ? "bg-white/15 text-white" : "text-marca-100 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  {e.texto}
                </Link>
              );
            })}
          </nav>
          <div className="text-right leading-tight">
            <p className="text-sm font-semibold">{sesion.nombre}</p>
            <p className="text-xs text-marca-100">
              {ROL[sesion.rol] ?? sesion.rol} · {sesion.agencia_nombre ?? "Sin agencia"}
            </p>
          </div>
          <form action="/api/auth/logout" method="post">
            <button className="rounded-md px-3 py-2 text-sm text-marca-100 ring-1 ring-white/20 hover:bg-white/10 hover:text-white">
              Salir
            </button>
          </form>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-6">{children}</main>
    </div>
  );
}
