import { describe, it, expect } from "vitest";
import { isValidUploadFile } from "./validateUpload";

const makeFile = (name: string) => new File(["dummy"], name);

describe("isValidUploadFile", () => {
  it("accepts .pdf files", () => {
    expect(isValidUploadFile(makeFile("report.pdf"))).toBe(true);
  });

  it("accepts .pdf regardless of case", () => {
    expect(isValidUploadFile(makeFile("Report.PDF"))).toBe(true);
  });

  it("rejects non-pdf files", () => {
    expect(isValidUploadFile(makeFile("image.png"))).toBe(false);
    expect(isValidUploadFile(makeFile("data.docx"))).toBe(false);
  });

  it("rejects files with no extension", () => {
    expect(isValidUploadFile(makeFile("README"))).toBe(false);
  });
});