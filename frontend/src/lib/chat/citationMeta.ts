import type { Citation } from "@/lib/api";

/**
 * Filters out metadata values that carry no information for the reader —
 * "unknown" is the enrichment pipeline's fallback when a chunk couldn't
 * be classified, and rendering it as a pill just adds noise.
 */
export function visibleCitationTags(citation: Citation): string[] {
  return [citation.authority, citation.topic, citation.document_type].filter(
    (value): value is string => Boolean(value) && value.toLowerCase() !== "unknown"
  );
}