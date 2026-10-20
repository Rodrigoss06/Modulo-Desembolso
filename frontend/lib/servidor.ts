// Configuracion solo de servidor (Route Handlers y componentes de servidor).
export const API_URL = process.env.DESEMBOLSO_API_URL ?? "http://127.0.0.1:8000";
export const TOKEN_URL = process.env.SEGURIDAD_TOKEN_URL ?? "http://127.0.0.1:9000/seguridad/v1/token";
export const COOKIE_SESION = "des_token";
export const COOKIE_SEGURA = process.env.COOKIE_SEGURA === "true";
