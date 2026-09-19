"use client";

import { useEffect, useState } from "react";

type BackendState = "checking" | "connected" | "unavailable";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function Home() {
  const [backendState, setBackendState] = useState<BackendState>("checking");

  useEffect(() => {
    const controller = new AbortController();

    async function checkBackend() {
      try {
        const response = await fetch(`${apiBaseUrl}/health`, { signal: controller.signal });
        setBackendState(response.ok ? "connected" : "unavailable");
      } catch {
        if (!controller.signal.aborted) setBackendState("unavailable");
      }
    }

    void checkBackend();
    return () => controller.abort();
  }, []);

  const statusText = {
    checking: "Backend: Checking…",
    connected: "Backend: Connected",
    unavailable: "Backend: Unavailable",
  }[backendState];

  return (
    <main>
      <section>
        <p className="eyebrow">Phase 1 · Platform foundation</p>
        <h1>Polymer AI Platform</h1>
        <p className="subtitle">AI-native infrastructure for polymer materials research.</p>
        <p className={`status ${backendState}`}>{statusText}</p>
      </section>
    </main>
  );
}
