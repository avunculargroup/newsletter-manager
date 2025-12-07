"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";
import { Button } from "@/components/ui/button";
import { Sparkles, RefreshCcw } from "lucide-react";

export function StatusHeader() {
  const runsQuery = useQuery({ queryKey: ["runs"], queryFn: api.getRuns });
  const draftQuery = useQuery({ queryKey: ["draft"], queryFn: api.getLatestDraft });

  const lastRun = runsQuery.data?.[0];
  const label = lastRun?.status === "completed" ? "Pipeline healthy" : "Awaiting draft";

  return (
    <div className="rounded-3xl border border-slate-200 bg-gradient-to-r from-blue-600 via-indigo-500 to-fuchsia-500 p-6 text-white shadow-lg">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-widest text-white/70">Automation status</p>
          <h1 className="text-2xl font-semibold">{label}</h1>
          <p className="text-sm text-white/80">
            {lastRun?.created_at
              ? `Last run ${formatDistanceToNow(new Date(lastRun.created_at), { addSuffix: true })}`
              : "No runs recorded"}
          </p>
          {draftQuery.data && (
            <p className="text-xs text-white/70">Draft ID: {draftQuery.data.run_id}</p>
          )}
        </div>
        <div className="flex gap-3">
          <Button
            variant="ghost"
            className="border border-white/30 bg-white/10 text-white"
            onClick={() => {
              runsQuery.refetch();
              draftQuery.refetch();
            }}
          >
            <RefreshCcw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button variant="secondary" className="bg-white text-slate-900">
            <Sparkles className="mr-2 h-4 w-4" />
            Weekly auto-run
          </Button>
        </div>
      </div>
    </div>
  );
}
