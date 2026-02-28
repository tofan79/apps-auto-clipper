import type { Metadata } from "next";
import Link from "next/link";
import { ReactNode } from "react";

import "./globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "AutoClipper AI Dashboard",
  description: "Desktop-first AI clip operations dashboard"
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps): JSX.Element {
  return (
    <html lang="en">
      <body className="app-body">
        <Providers>
          <div className="app-shell">
            <header className="topbar">
              <div>
                <p className="eyebrow">AutoClipper AI</p>
                <h1 className="topbar-title">Operator Console</h1>
              </div>
              <nav className="topbar-nav">
                <Link href="/">Dashboard</Link>
                <Link href="/settings">Settings</Link>
              </nav>
            </header>
            <main className="content">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
