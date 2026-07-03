import { Footer } from "@/components/Footer";
import { Hero } from "@/components/landing/Hero";
import { WhyDifferent } from "@/components/landing/WhyDifferent";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { WhoFor } from "@/components/landing/WhoFor";
import { Authorities } from "@/components/landing/Authorities";
import { CtaBanner } from "@/components/landing/CtaBanner";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Hero />
      <WhyDifferent />
      <HowItWorks />
      <WhoFor />
      <Authorities />
      <CtaBanner />
      <Footer />
    </div>
  );
}