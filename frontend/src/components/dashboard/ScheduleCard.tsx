"use client";

import { useState } from "react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function ScheduleCard() {
  const [cron, setCron] = useState(() => {
    if (typeof window === "undefined") return "0 15 * * 1";
    return localStorage.getItem("newsletter-cron") ?? "0 15 * * 1";
  });
  const [timezone, setTimezone] = useState(() => {
    if (typeof window === "undefined") return "UTC";
    return localStorage.getItem("newsletter-timezone") ?? "UTC";
  });
  const [message, setMessage] = useState<string | null>(null);

  const save = () => {
    localStorage.setItem("newsletter-cron", cron);
    localStorage.setItem("newsletter-timezone", timezone);
    setMessage("Saved locally — wire this into Celery beat to automate");
    setTimeout(() => setMessage(null), 4000);
  };

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Scheduler</CardTitle>
          <CardDescription>Document the cron schedule that Celery beat should use.</CardDescription>
        </div>
      </CardHeader>
      <div className="space-y-4">
        <div>
          <label className="text-sm text-slate-500">Cron expression</label>
          <Input value={cron} onChange={(event) => setCron(event.target.value)} />
        </div>
        <div>
          <label className="text-sm text-slate-500">Timezone</label>
          <Input value={timezone} onChange={(event) => setTimezone(event.target.value)} />
        </div>
        <Button variant="secondary" onClick={save}>
          Save
        </Button>
        {message && <p className="text-xs text-slate-500">{message}</p>}
        <p className="text-xs text-slate-500">
          Deployers: update `backend/app/tasks.py` schedule or Celery beat config to use the saved cron.
        </p>
      </div>
    </Card>
  );
}
