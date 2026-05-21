import Link from "next/link";
export function Navbar({ variant }: { variant?: string }) {
  return (
    <nav className="p-4 border-b flex justify-between items-center bg-white">
      <Link href="/" className="font-bold text-xl">MyKepatuhan</Link>
      <div className="flex gap-4">
        <Link href="/login" className="text-sm font-medium">Login</Link>
        <Link href="/chat" className="text-sm font-medium bg-blue-600 text-white px-3 py-1 rounded">Chat</Link>
      </div>
    </nav>
  );
}