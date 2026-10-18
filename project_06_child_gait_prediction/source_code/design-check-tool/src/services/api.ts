// API service layer for Child Gait AI
// Flow: React Frontend -> FastAPI Backend -> SQLite Database (gait_records) & ML Service

const API_BASE_URL =
  (import.meta.env["VITE_API_URL"] as string | undefined) ?? "http://localhost:8000";

export type GaitCategory = "Normal" | "Diplegic" | "Hemiplegic" | string;

export interface GaitInput {
  childId: string;
  age: number;
  gender: string;
  heelPressure: number;
  toePressure: number;
  tiltAngle: number;
  stepDuration: number;
  strideLength: number;
  walkingSpeed: number;
}

export interface PredictionResponse {
  prediction: GaitCategory;
  confidence?: number | undefined;
  assessmentId?: string | undefined;
  recommendations?: string[] | undefined;
  record?: Record<string, any> | undefined;
}

export interface AssessmentRecord {
  id: string;
  date: string;
  childId: string;
  age: number;
  gender: string;
  heelPressure: number;
  toePressure: number;
  tiltAngle: number;
  stepDuration: number;
  strideLength: number;
  walkingSpeed: number;
  prediction: GaitCategory;
  confidence?: number | undefined;
  recommendations?: string[] | undefined;
}

const STORAGE_KEY = "child_gait_assessments";

// Local storage management for assessment records
export function getStoredAssessments(): AssessmentRecord[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveStoredAssessment(record: AssessmentRecord): void {
  if (typeof window === "undefined") return;
  try {
    const existing = getStoredAssessments();
    const updated = [record, ...existing.filter((item) => item.id !== record.id)];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));

    // Also persist asynchronously to the backend database table `gait_records`
    fetch(`${API_BASE_URL}/api/records`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    }).catch(() => {
      // Backend offline; record is safely stored locally
    });
  } catch (err) {
    console.error("Failed to save assessment locally", err);
  }
}

export function removeStoredAssessment(id: string): void {
  if (typeof window === "undefined") return;
  try {
    const existing = getStoredAssessments();
    const updated = existing.filter((item) => item.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));

    // Also delete from backend database
    fetch(`${API_BASE_URL}/api/records/${encodeURIComponent(id)}`, {
      method: "DELETE",
    }).catch(() => {
      // Ignore if backend offline
    });
  } catch (err) {
    console.error("Failed to delete assessment locally", err);
  }
}

// Predict gait via backend ML service and persist in database
export async function predictGait(input: GaitInput): Promise<PredictionResponse> {
  const res = await fetch(`${API_BASE_URL}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!res.ok) {
    throw new Error(`Server responded with ${res.status}`);
  }

  const data = await res.json();
  return data;
}

// Fetch assessments from backend database table `gait_records` or fallback to local storage
export async function fetchAssessments(childId?: string): Promise<AssessmentRecord[]> {
  try {
    const url = childId
      ? `${API_BASE_URL}/api/records?childId=${encodeURIComponent(childId)}`
      : `${API_BASE_URL}/api/records`;

    const res = await fetch(url);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        return data.map((item) => ({
          id: item.id || `rec-${item.created_at}`,
          date: item.created_at || item.date || new Date().toISOString(),
          childId: item.child_id || item.childId,
          age: Number(item.age),
          gender: item.gender,
          heelPressure: Number(item.heel_pressure ?? item.heelPressure),
          toePressure: Number(item.toe_pressure ?? item.toePressure),
          tiltAngle: Number(item.tilt_angle ?? item.tiltAngle),
          stepDuration: Number(item.step_duration ?? item.stepDuration),
          strideLength: Number(item.stride_length ?? item.strideLength),
          walkingSpeed: Number(item.walking_speed ?? item.walkingSpeed),
          prediction: item.gait_class || item.prediction || "Normal",
          confidence: item.confidence ?? undefined,
          recommendations: item.recommendations ?? undefined,
        }));
      }
    }
  } catch {
    // Backend offline; fallback to local storage
  }

  const local = getStoredAssessments();
  if (childId) {
    return local.filter((r) => r.childId.toLowerCase() === childId.toLowerCase());
  }
  return local;
}
