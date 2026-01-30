import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { GoogleTagManager } from "./components/GoogleTagManager";
import { defaultMetadata } from "./lib/metadata";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = defaultMetadata;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';

  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href={`${basePath}/favicon.ico`} sizes="any" />
      </head>
      <body
        className={`${inter.variable} antialiased`}
        suppressHydrationWarning
        style={{ fontFamily: 'var(--font-inter), system-ui, sans-serif' }}
      >
        <GoogleTagManager />
        {children}
      </body>
    </html>
  );
}
