import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BNA · Desembolso de Créditos",
  description: "Módulo 13 Desembolso de la Línea de Créditos del Banco Nacional de Arequipa",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es-PE">
      <body className="min-h-screen font-sans antialiased">{children}</body>
    </html>
  );
}
