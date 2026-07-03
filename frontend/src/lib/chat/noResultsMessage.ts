import type { TranslationKey } from "@/lib/i18n";

type Translate = (key: TranslationKey) => string;

/**
 * Builds the "no matching documents" message, listing whichever filters
 * (authority/topic) narrowed the search — so the user knows what to relax.
 */
export function buildNoResultsMessage(tr: Translate, authority: string, topic: string): string {
  const activeFilters: string[] = [];
  if (authority !== "All") activeFilters.push(`${tr("filter_authority")}: ${authority}`);
  if (topic !== "All") activeFilters.push(`${tr("filter_topic")}: ${topic}`);

  const filtersStr = activeFilters.join(` ${tr("chat_no_results_join")} `);
  return tr("chat_no_results").replace("{filters}", filtersStr);
}