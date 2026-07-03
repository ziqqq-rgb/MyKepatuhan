/** Only PDFs are accepted for ingestion. */
export function isValidUploadFile(file: File): boolean {
  return file.name.toLowerCase().endsWith(".pdf");
}