export type TopicPreset = {
  id?: string;
  name: string;
  topics: string[];
  rss_feeds?: string[];
  updated_at?: string;
};

export type RunStatus = {
  id: string;
  status: "queued" | "running" | "completed" | "failed" | string;
  message?: string;
  created_at?: string;
  topics?: string[];
};

export type DraftSection = {
  title: string;
  hook: string;
  summary: string;
  call_to_action: string;
  keywords: string[];
  source_url: string;
};

export type DraftPayload = {
  run_id: string;
  hero?: {
    url: string;
    attribution: string;
    photographer?: string;
  } | null;
  sections: DraftSection[];
  html: string;
};

export type TriggerPayload = {
  topics: string[];
  title: string;
  subject: string;
  preheader?: string;
  hero_query?: string;
  rss_feeds?: string[];
};
