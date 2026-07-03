"use client";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { useUser } from "@stackframe/stack";
import { clearToken } from "@/lib/api";

type NavbarProps = {
  variant?: "app" | "landing";
  userEmail?: string;
  isAdmin?: boolean;
};

export function Navbar({ variant = "app", userEmail, isAdmin }: NavbarProps) {
  const user = useUser();
  const router = useRouter();

  async function handleLogout() {
    clearToken();
    try {
      await user?.signOut();
    } finally {
      router.push("/");
    }
  }

  const navClass =
    variant === "landing"
      ? "absolute inset-x-0 top-0 z-20 flex h-16 shrink-0 items-center justify-between bg-transparent px-4 sm:px-6"
      : "flex h-14 shrink-0 items-center justify-between border-b border-border bg-card/60 px-4 backdrop-blur-md sm:px-6";

  const logo = (
    <>
      <Image src="/logo.svg" alt="MyKepatuhan logo" width={28} height={28} priority />
      <span className="text-[15px] font-semibold tracking-tight text-foreground">
        My<span
          className="bg-clip-text text-transparent"
          style={{ backgroundImage: "var(--gradient-primary)" }}
        >Kepatuhan</span>
      </span>
    </>
  );

  return (
    <nav className={navClass}>
      {variant === "landing" ? (
        <Link href="/" className="flex items-center">
          {logo}
        </Link>
      ) : (
        <div className="flex items-center">{logo}</div>
      )}

      <div className="flex items-center gap-3">
        {user ? (
          <>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:border-destructive/40 hover:bg-destructive/5 hover:text-destructive"
            >
              <LogOut className="h-3.5 w-3.5" strokeWidth={2} />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              Log in
            </Link>
            <Link
              href="/register"
              className="rounded-lg px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
              style={{ background: "var(--gradient-primary)" }}
            >
              Sign up
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}