import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "./providers";

const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || "ScaleX AI";

export const metadata: Metadata = {
  title: {
    default: `${APP_NAME} — AI Creative Studio`,
    template: `%s · ${APP_NAME}`,
  },
  description:
    "Turn any product URL into a full marketing campaign — on-brand copy, images, video, and UGC, generated in seconds.",
  applicationName: APP_NAME,
};

export const viewport: Viewport = {
  themeColor: "#0a0a12",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {/* Runtime web fonts (build stays offline-safe; graceful system fallback). */}
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
