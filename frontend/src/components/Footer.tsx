import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-auto flex flex-col items-center gap-1 p-4 text-center text-sm text-gray-500">
      <span>© 2026 MyKepatuhan</span>
      <Link href="/privacy" className="underline underline-offset-2 hover:text-gray-700">
        Privacy Policy
      </Link>
      <Link href="/terms" className="underline underline-offset-2 hover:text-gray-700">
        Terms of Service
      </Link>
    </footer>
  );
}