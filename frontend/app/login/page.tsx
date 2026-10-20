"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Alerta, Boton, Etiqueta, estiloEntrada } from "@/components/ui";

const esquema = z.object({
  usuario: z.string().trim().min(3, "Ingrese su usuario"),
  contrasena: z.string().min(6, "Ingrese su contraseña"),
});
type Datos = z.infer<typeof esquema>;

const USUARIOS_DEMO = [
  ["operador1", "Operador de agencia"],
  ["supervisor1", "Supervisor"],
  ["auditor1", "Auditor"],
];

export default function Login() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit, formState } = useForm<Datos>({ resolver: zodResolver(esquema) });

  async function ingresar(datos: Datos) {
    setError(null);
    const r = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
    if (!r.ok) {
      const cuerpo = (await r.json().catch(() => ({}))) as { mensaje?: string };
      setError(cuerpo.mensaje ?? "No se pudo iniciar sesión");
      return;
    }
    router.replace("/creditos");
    router.refresh();
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <aside className="hidden flex-col justify-between bg-marca-800 p-12 text-white lg:flex">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-white text-base font-black text-marca-800">BNA</span>
          <span className="text-lg font-semibold">Banco Nacional de Arequipa</span>
        </div>
        <div>
          <h1 className="text-4xl font-semibold leading-tight">Desembolso de créditos</h1>
          <p className="mt-4 max-w-md text-marca-100">
            Convierta un crédito aprobado en un abono confirmado en la cuenta del titular, con validación de identidad,
            control de duplicidad y trazabilidad completa.
          </p>
        </div>
        <p className="text-xs text-marca-200">Módulo 13 · Línea de Créditos · Servicio SRV-CR-04</p>
      </aside>
      <main className="flex items-center justify-center p-8">
        <form onSubmit={handleSubmit(ingresar)} className="w-full max-w-sm space-y-5" noValidate>
          <div>
            <h2 className="text-2xl font-semibold text-slate-900">Iniciar sesión</h2>
            <p className="mt-1 text-sm text-slate-500">Autenticación con el servicio de Seguridad del BNA.</p>
          </div>
          {error && <Alerta tipo="error" titulo={error} />}
          <div>
            <Etiqueta htmlFor="usuario">Usuario</Etiqueta>
            <input id="usuario" autoComplete="username" className={estiloEntrada} {...register("usuario")} />
            {formState.errors.usuario && <p className="mt-1 text-xs text-rose-600">{formState.errors.usuario.message}</p>}
          </div>
          <div>
            <Etiqueta htmlFor="contrasena">Contraseña</Etiqueta>
            <input id="contrasena" type="password" autoComplete="current-password" className={estiloEntrada} {...register("contrasena")} />
            {formState.errors.contrasena && <p className="mt-1 text-xs text-rose-600">{formState.errors.contrasena.message}</p>}
          </div>
          <Boton type="submit" cargando={formState.isSubmitting} className="w-full py-2.5">
            Ingresar
          </Boton>
          {process.env.NEXT_PUBLIC_AMBIENTE === "desarrollo" && (
            <Alerta tipo="info" titulo="Ambiente de desarrollo">
              <p>Usuarios del simulador de Seguridad (contraseña Demo2026!):</p>
              <ul className="mt-1 space-y-0.5 font-mono text-xs">
                {USUARIOS_DEMO.map(([u, rol]) => (
                  <li key={u}>
                    {u} · <span className="font-sans">{rol}</span>
                  </li>
                ))}
              </ul>
            </Alerta>
          )}
        </form>
      </main>
    </div>
  );
}
