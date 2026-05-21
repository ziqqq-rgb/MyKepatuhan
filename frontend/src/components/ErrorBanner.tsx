export function ErrorBanner({ error }: { error: string | null }) {
  if (!error) return null;
  return <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm">{error}</div>;
}