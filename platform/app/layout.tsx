import type { ReactNode } from "react";
import {
  ClerkProvider,
  SignInButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";

export const metadata = {
  title: "KeyAI — verified research platform",
  description:
    "Authenticated platform for the machine-verifiable Research OS (secp256k1, P-256).",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body
          style={{
            margin: 0,
            fontFamily:
              "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
            color: "#0b1b34",
            background: "#f4f8fc",
          }}
        >
          <header
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 16,
              padding: "14px 24px",
              background: "#001a3f",
              color: "#fff",
            }}
          >
            <a
              href="/"
              style={{ color: "#fff", fontWeight: 800, textDecoration: "none" }}
            >
              keyAI · platform
            </a>
            <nav style={{ display: "flex", gap: 16, alignItems: "center" }}>
              <a href="/" style={{ color: "#b9cbe8", textDecoration: "none" }}>
                Overview
              </a>
              <a
                href="/research"
                style={{ color: "#b9cbe8", textDecoration: "none" }}
              >
                Research (private)
              </a>
              <SignedOut>
                <SignInButton mode="modal" />
              </SignedOut>
              <SignedIn>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </nav>
          </header>
          <main style={{ maxWidth: 960, margin: "0 auto", padding: "28px 24px" }}>
            {children}
          </main>
        </body>
      </html>
    </ClerkProvider>
  );
}
