import axios, { AxiosError } from "axios";

// Todas las llamadas del navegador van al BFF (/api/des), nunca directo a la API ni al Bus.
export const api = axios.create({ baseURL: "/api/des", headers: { "Content-Type": "application/json" } });

export class ErrorApi extends Error {
  constructor(
    mensaje: string,
    public codigo: string,
    public estado: number,
    public detalle?: unknown,
    public correlationId?: string,
  ) {
    super(mensaje);
  }
}

api.interceptors.request.use((config) => {
  config.headers.set("X-Correlation-ID", crypto.randomUUID());
  return config;
});

api.interceptors.response.use(
  (respuesta) => respuesta,
  (error: AxiosError<{ codigo?: string; mensaje?: string; detalle?: unknown; correlation_id?: string }>) => {
    const datos = error.response?.data;
    if (error.response?.status === 401 && typeof window !== "undefined") {
      window.location.href = "/api/auth/logout";
    }
    return Promise.reject(
      new ErrorApi(
        datos?.mensaje ?? "No se pudo comunicar con el servidor",
        datos?.codigo ?? "ERROR_DE_RED",
        error.response?.status ?? 0,
        datos?.detalle,
        datos?.correlation_id ?? error.response?.headers?.["x-correlation-id"],
      ),
    );
  },
);

export function nuevaClave(): string {
  return crypto.randomUUID();
}
