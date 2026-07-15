"use client";

import { motion } from "framer-motion";
import { ArrowRight, Eye, EyeOff, Lock, Mail } from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";
import { BrandWordmark } from "@/components/layout/brand-mark";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { isAuthed, login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [showPass, setShowPass] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);
  const [shake, setShake] = React.useState(0);

  // Already signed in → straight to the studio.
  React.useEffect(() => {
    if (isAuthed()) router.replace("/dashboard");
  }, [router]);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    // Tiny delay so the button state reads as a real check.
    setTimeout(() => {
      if (login(username, password)) {
        router.push("/dashboard");
      } else {
        setError("Invalid username or password.");
        setShake((s) => s + 1);
        setBusy(false);
      }
    }, 350);
  }

  return (
    <div className="relative grid min-h-screen place-items-center overflow-hidden bg-background px-4">
      {/* Background layers */}
      <div className="aurora-bg" />
      <div className="pointer-events-none absolute inset-0 -z-10 grid-bg opacity-50" />
      <div className="pointer-events-none absolute -left-24 top-24 -z-10 h-72 w-72 rounded-full bg-aurora-violet/25 blur-3xl animate-float" />
      <div
        className="pointer-events-none absolute -right-16 bottom-24 -z-10 h-80 w-80 rounded-full bg-aurora-cyan/20 blur-3xl animate-float"
        style={{ animationDelay: "-2.5s" }}
      />

      <motion.div
        key={shake}
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0, x: shake ? [0, -10, 10, -6, 6, 0] : 0 }}
        transition={{ duration: shake ? 0.4 : 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md"
      >
        <div className="mb-8 flex justify-center">
          <BrandWordmark />
        </div>

        <div className="glass-strong rounded-3xl p-8 shadow-glow">
          <h1 className="font-display text-2xl font-bold tracking-tight">Welcome back</h1>
          <p className="mt-1.5 text-sm text-muted-foreground">
            Sign in to open your creative studio.
          </p>

          <form onSubmit={submit} className="mt-7 space-y-5">
            <div className="space-y-1.5">
              <Label htmlFor="username">Username</Label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground/70" />
                <Input
                  id="username"
                  type="email"
                  autoComplete="username"
                  placeholder="you@company.com"
                  className="pl-10"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoFocus
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground/70" />
                <Input
                  id="password"
                  type={showPass ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="••••••••••"
                  className="pl-10 pr-11"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPass((v) => !v)}
                  aria-label={showPass ? "Hide password" : "Show password"}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-muted-foreground/70 transition-colors hover:text-foreground"
                >
                  {showPass ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {error && (
              <p className="rounded-xl bg-destructive/10 px-3.5 py-2.5 text-sm font-medium text-destructive">
                {error}
              </p>
            )}

            <Button type="submit" variant="aurora" size="lg" className="group w-full" disabled={busy}>
              {busy ? <Spinner /> : null}
              {busy ? "Signing in…" : "Sign in"}
              {!busy && (
                <ArrowRight className="transition-transform duration-200 group-hover:translate-x-0.5" />
              )}
            </Button>
          </form>
        </div>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          Runs locally · your data never leaves this machine
        </p>
      </motion.div>
    </div>
  );
}
