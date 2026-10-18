import { describe, expect, it } from "vitest";
import { parseEcgFile } from "@/services/predictionService";

describe("ECG Client Parser & Validation", () => {
  it("parses valid numeric CSV ECG signal data correctly", async () => {
    const csvContent = `time,voltage\n0.00,0.12\n0.01,0.25\n0.02,0.85\n0.03,1.20\n0.04,-0.30\n0.05,0.10`;
    const file = new File([csvContent], "ecg_test.csv", { type: "text/csv" });

    const result = await parseEcgFile(file);
    expect(result.pointCount).toBe(6);
    expect(result.samples.length).toBe(6);
    expect(result.samples[0].mv).toBe(0.12);
    expect(result.samples[3].mv).toBe(1.2);
  });

  it("parses valid JSON ECG signal array correctly", async () => {
    const jsonContent = JSON.stringify([0.15, 0.45, 1.1, -0.2, 0.05]);
    const file = new File([jsonContent], "ecg_signal.json", { type: "application/json" });

    const result = await parseEcgFile(file);
    expect(result.pointCount).toBe(5);
    expect(result.samples[2].mv).toBe(1.1);
  });

  it("rejects non-numeric arbitrary text files", async () => {
    const textContent = `This is some random text file\nWith no numeric ECG data\nJust lines of words\nNot medical data\nTest line five`;
    const file = new File([textContent], "notes.csv", { type: "text/csv" });

    await expect(parseEcgFile(file)).rejects.toThrow(/File structure is not a valid ECG signal/i);
  });

  it("rejects empty files", async () => {
    const file = new File([""], "empty.csv", { type: "text/csv" });
    await expect(parseEcgFile(file)).rejects.toThrow(/file is empty/i);
  });
});
