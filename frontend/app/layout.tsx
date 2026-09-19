import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Polymer AI Platform",
  description: "AI-native infrastructure for polymer materials research",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
