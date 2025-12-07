import { DraftPayload, RunStatus, TopicPreset, TriggerPayload } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || response.statusText);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  getTopics: (): Promise<TopicPreset[]> => request("/topics/"),
  upsertTopic: (payload: TopicPreset): Promise<TopicPreset> =>
    request("/topics/", { method: "POST", body: JSON.stringify(payload) }),
  getRuns: (): Promise<RunStatus[]> => request("/runs/"),
  triggerRun: (payload: TriggerPayload) =>
    request<{ run_id: string; status: string }>("/runs/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getLatestDraft: (): Promise<DraftPayload | null> => request("/runs/latest"),
};
