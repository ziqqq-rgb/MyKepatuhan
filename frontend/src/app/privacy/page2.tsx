import type { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { TERMS_OF_SERVICE_HTML} from "./content";

export const metadata: Metadata = {
  title: "Terms of Service",
};

export default function TermsOfServicePage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar variant="landing" />

      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-20 sm:px-6">
        <div
          className="rounded-2xl bg-white p-6 text-black shadow-sm sm:p-10"
          dangerouslySetInnerHTML={{ __html: TERMS_OF_SERVICE_HTML }}
        />
      </main>

      <Footer />
    </div>
  );
}