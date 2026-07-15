"use client";

import { useRouter } from "next/navigation";
import * as React from "react";
import { LoadingOverlay } from "@/components/ui/spinner";
import { isAuthed } from "@/lib/auth";

/** Blocks the studio until the user signs in — redirects to /login otherwise. */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = React.useState(false);

  React.useEffect(() => {
    if (isAuthed()) setReady(true);
    else router.replace("/login");
  }, [router]);

  if (!ready) {
    return (
      <div className="grid min-h-screen place-items-center">
        <LoadingOverlay label="Opening the studio…" />
      </div>
    );
  }
  return <>{children}</>;
}
