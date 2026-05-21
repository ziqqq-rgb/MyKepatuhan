"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Check } from "lucide-react";
import { useStackApp } from "@stackframe/stack";
import { useLanguage } from "@/lib/i18n";
import { ErrorBanner } from "@/components/ErrorBanner";
import { apiRegister, apiLogin, setToken } from "@/lib/api";

export default function RegisterPage() {
  const { tr } = useLanguage();
  const router = useRouter();
  const stackApp = useStackApp();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pwLongEnough = password.length >= 8;
  const pwMatch = password === confirm && confirm.length > 0;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!pwLongEnough) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (!pwMatch) {
      setError(tr("register_pw_mismatch"));
      return;
    }

    setLoading(true);
    try {
      // 1. Register with Neon Auth (Stack Auth) — creates the frontend session
      const result = await stackApp.signUpWithCredential({ email, password });
      if (result.status === "error") {
        setError(result.error?.message ?? "Registration failed.");
        return;
      }

      // 2. Register on FastAPI backend — creates the DB user
      await apiRegister(email, password);

      // 3. Get FastAPI JWT for API calls
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
    <div className="w-full max-w-sm animate-fade-in">
      <div className="rounded-2xl border border-border bg-card p-8 shadow-sm">
        {/* Header */}
        <div className="mb-7 text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            {tr("register_title")}
          </h1>
          <p className="mt-1.5 text-sm text-muted-foreground">{tr("register_sub")}</p>
        </div>

        {error && (
          <div className="mb-5">
            <ErrorBanner message={error} />
          </div>
        )}

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
              className="w-full rounded-lg border border-border bg-background px-3.5 py-2.5 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20"
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
                className="w-full rounded-lg border border-border bg-background px-3.5 py-2.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
              <button
                type="button"
                onClick={() => setShowPw((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                tabIndex={-1}
              >
                {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {/* Password strength hint */}
            <div className="mt-1.5 flex items-center gap-1.5 text-xs">
              <span className={`flex h-3.5 w-3.5 items-center justify-center rounded-full transition-colors ${pwLongEnough ? "bg-success text-white" : "bg-border"}`}>
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
                className={`w-full rounded-lg border bg-background px-3.5 py-2.5 pr-10 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none transition-colors focus:ring-2 focus:ring-primary/20 ${
                  confirm.length > 0 && !pwMatch
                    ? "border-destructive focus:border-destructive"
                    : "border-border focus:border-primary"
                }`}
              />
              {confirm.length > 0 && pwMatch && (
                <Check className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-success" strokeWidth={2.5} />
              )}
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="mt-1 flex w-full items-center justify-center rounded-xl py-2.5 text-sm font-semibold text-white transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            style={{ background: "var(--gradient-primary)" }}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Creating account...
              </span>
            ) : (
              tr("register_submit")
            )}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          {tr("register_has_account")}{" "}
          <Link href="/login" className="font-medium text-primary hover:underline">
            {tr("register_login_link")}
          </Link>
        </p>
      </div>
    </div>
  );
}
