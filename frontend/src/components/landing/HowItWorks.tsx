"use client";

import { useEffect, useRef, useState } from "react";
import { useLanguage, type TranslationKey } from "@/lib/i18n";

const STEP_KEYS: TranslationKey[] = ["how_1", "how_2", "how_3"];

// phase 0 = idle/reset, 1 = step1 lit, 2 = line1 growing,
// 3 = step2 lit, 4 = line2 growing, 5 = step3 lit (held longest, then loops)
const SEQUENCE: { phase: number; delay: number }[] = [
  { phase: 0, delay: 400 },
  { phase: 1, delay: 500 },
  { phase: 2, delay: 700 },
  { phase: 3, delay: 500 },
  { phase: 4, delay: 700 },
  { phase: 5, delay: 2200 },
];

export function HowItWorks() {
  const { tr } = useLanguage();
  const [phase, setPhase] = useState(0);
  const idxRef = useRef(0);

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    const run = () => {
      setPhase(SEQUENCE[idxRef.current].phase);
      timeoutId = setTimeout(() => {
        idxRef.current = (idxRef.current + 1) % SEQUENCE.length;
        run();
      }, SEQUENCE[idxRef.current].delay);
    };
    run();
    return () => clearTimeout(timeoutId);
  }, []);

  const stepLit = (i: number) => phase >= i * 2 + 1;
  const lineGrown = (i: number) => phase >= i * 2 + 2;

  return (
    <section id="how" className="border-b border-border">
      <div className="mx-auto max-w-5xl px-4 py-20 sm:px-6">
        <h2 className="text-center text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          {tr("how_title")}
        </h2>

        <div className="mt-16 flex items-start">
          {STEP_KEYS.map((key, i) => (
            <div key={key} className="flex flex-1 items-start last:flex-none">
              <div className="flex w-20 flex-col items-center text-center sm:w-48">
                <div
                  className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full border-2 text-lg font-semibold transition-all duration-500 ${
                    stepLit(i)
                      ? "scale-110 border-primary text-white"
                      : "border-border bg-card text-muted-foreground"
                  }`}
                  style={stepLit(i) ? { background: "var(--gradient-primary)" } : undefined}
                >
                  {i + 1}
                </div>
                <div
                  className={`mt-4 text-xs font-semibold uppercase tracking-widest transition-colors duration-500 ${
                    stepLit(i) ? "text-primary" : "text-muted-foreground"
                  }`}
                >
                  Step 0{i + 1}
                </div>
                <p
                  className={`mt-1.5 text-sm font-medium leading-snug transition-colors duration-500 sm:text-base ${
                    stepLit(i) ? "text-foreground" : "text-muted-foreground"
                  }`}
                >
                  {tr(key)}
                </p>
              </div>

              {i < STEP_KEYS.length - 1 && (
                <div className="relative mt-6 h-0.5 flex-1 overflow-hidden rounded-full bg-border">
                  <div
                    className="absolute inset-y-0 left-0 rounded-full bg-primary transition-all duration-700 ease-out"
                    style={{ width: lineGrown(i) ? "100%" : "0%" }}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}