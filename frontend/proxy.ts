import { NextRequest, NextResponse } from "next/server";

// Verificacion optimista: sin cookie de sesion se envia al login. La autorizacion real la hace la API.
export function proxy(request: NextRequest) {
  if (!request.cookies.has("des_token") && request.nextUrl.pathname !== "/login") {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
