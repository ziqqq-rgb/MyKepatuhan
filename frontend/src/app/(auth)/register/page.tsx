"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Check, ShieldCheck } from "lucide-react";
import { useStackApp } from "@stackframe/stack";
import { useLanguage } from "@/lib/i18n";
import { ErrorBanner } from "@/components/ErrorBanner";
import { apiRegister, apiLogin, setToken } from "@/lib/api";

function GoogleIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" aria-hidden>
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
    </svg>
  );
}

export default function RegisterPage() {
  const { tr } = useLanguage();
  const router = useRouter();
  const stackApp = useStackApp();

  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm]   = useState("");
  const [showPw, setShowPw]     = useState(false);
  const [loading, setLoading]   = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [error, setError]       = useState<string | null>(null);

  const pwLongEnough = password.length >= 8;
  const pwMatch      = password === confirm && confirm.length > 0;

  /* ── Google OAuth ── */
  async function handleGoogle() {
    setError(null);
    setGoogleLoading(true);
    try {
      await stackApp.signInWithOAuth("google");
    } catch {
      setError("Google sign-up failed. Please try again.");
      setGoogleLoading(false);
    }
  }

  /* ── Email / password ── */
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!pwLongEnough) { setError("Password must be at least 8 characters."); return; }
    if (!pwMatch)      { setError(tr("register_pw_mismatch")); return; }

    setLoading(true);
    try {
      const result = await stackApp.signUpWithCredential({ email, password });
      if (result.status === "error") {
        setError(result.error?.message ?? "Registration failed.");
        return;
      }
      await apiRegister(email, password);
      const authResponse = await apiLogin(email, password);
      setToken(authResponse.access_token);
      router.push("/chat");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-100 animate-fade-in">
      {/* Logo mark */}
      <div className="mb-8 flex flex-col items-center text-center">
        <div
          className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl text-white shadow-lg"
          style={{ background: "var(--gradient-primary)", boxShadow: "var(--shadow-elegant)" }}
        >
          <ShieldCheck className="h-6 w-6" strokeWidth={2} />
        </div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">
          {tr("register_title")}
        </h1>
        <p className="mt-1.5 text-sm text-muted-foreground">{tr("register_sub")}</p>
      </div>

      {/* Card */}
      <div
        className="rounded-2xl border border-border/60 p-6"
        style={{ background: "var(--gradient-card)", boxShadow: "var(--shadow-card)" }}
      >
        {error && <div className="mb-5"><ErrorBanner error={error} /></div>}

        {/* Google button */}
        <button
          onClick={handleGoogle}
          disabled={googleLoading || loading}
          className="flex w-full items-center justify-center gap-3 rounded-xl border border-border bg-secondary/80 px-4 py-2.5 text-sm font-medium text-foreground transition-all hover:bg-secondary hover:border-border/80 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {googleLoading
            ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-border border-t-foreground" />
            : <GoogleIcon />}
          Continue with Google
        </button>

        {/* Divider */}
        <div className="my-5 flex items-center gap-3">
          <div className="h-px flex-1 bg-border" />
          <span className="text-xs text-muted-foreground">or sign up with email</span>
          <div className="h-px flex-1 bg-border" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground">
              {tr("register_email")}
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              placeholder="you@example.com"
              className="w-full rounded-xl border border-border bg-background/60 px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-all focus:border-primary/60 focus:ring-2 focus:ring-primary/15"
            />
          </div>

          {/* Password */}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground">
              {tr("register_password")}
            </label>
            <div className="relative">
              <input
                type={showPw ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
                placeholder="••••••••"
                className="w-full rounded-xl border border-border bg-background/60 px-3.5 py-2.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-all focus:border-primary/60 focus:ring-2 focus:ring-primary/15"
              />
              <button
                type="button"
                onClick={() => setShowPw((v) => !v)}
                tabIndex={-1}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
              >
                {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            <div className="mt-2 flex items-center gap-1.5 text-xs">
              <span
                className={`flex h-3.5 w-3.5 items-center justify-center rounded-full transition-colors ${
                  pwLongEnough ? "bg-success text-white" : "bg-border"
                }`}
              >
                {pwLongEnough && <Check className="h-2.5 w-2.5" strokeWidth={3} />}
              </span>
              <span className={pwLongEnough ? "text-success" : "text-muted-foreground"}>
                {tr("register_pw_hint")}
              </span>
            </div>
          </div>

          {/* Confirm password */}
          <div>
            <label className="mb-1.5 block text-sm font-medium text-foreground">
              {tr("register_confirm")}
            </label>
            <div className="relative">
              <input
                type={showPw ? "text" : "password"}
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
                placeholder="••••••••"
                className={`w-full rounded-xl border bg-background/60 px-3.5 py-2.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground/50 outline-none transition-all focus:ring-2 focus:ring-primary/15 ${
                  confirm.length > 0 && !pwMatch
                    ? "border-destructive/70 focus:border-destructive"
                    : "border-border focus:border-primary/60"
                }`}
              />
              {confirm.length > 0 && pwMatch && (
                <Check className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-success" strokeWidth={2.5} />
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || googleLoading}
            className="flex w-full items-center justify-center rounded-xl py-2.5 text-sm font-semibold text-white transition-all hover:opacity-90 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
            style={{ background: "var(--gradient-primary)", boxShadow: "var(--shadow-elegant)" }}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Creating account...
              </span>
            ) : tr("register_submit")}
          </button>
        </form>
      </div>

      <p className="mt-5 text-center text-sm text-muted-foreground">
        {tr("register_has_account")}{" "}
        <Link href="/login" className="font-medium text-primary transition-colors hover:text-primary/80">
          {tr("register_login_link")}
        </Link>
      </p>
    </div>
  );
}