"use client";

import { useQuery } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const statusCopy: Record<string, string> = {
  completed: "Draft ready",
  running: "Processing",
  failed: "Needs attention",
  queued: "Queued",
};

export function RunHistory() {
  const {
    data,
    isFetching,
    refetch,
  } = useQuery({
    queryKey: ["runs"],
    queryFn: api.getRuns,
    refetchInterval: 15000,
  });

  return (
    <Card>
      <CardHeader className="items-start">
        <div>
          <CardTitle>Run history</CardTitle>
          <CardDescription>Live view of the most recent pipeline executions.</CardDescription>
        </div>
        <Button variant="ghost" onClick={() => refetch()} disabled={isFetching}>
          Refresh
        </Button>
      </CardHeader>
      <div className="space-y-4">
        {data?.map((run) => {
          const badgeVariant = ["completed", "running", "failed", "queued"].includes(run.status)
            ? (run.status as "completed" | "running" | "failed" | "queued")
            : undefined;
          return (
            <div key={run.id} className="rounded-xl border border-slate-100 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-900">{run.topics?.join(", ") || "Ad-hoc"}</p>
                  <p className="text-xs text-slate-500">
                    {run.created_at
                      ? formatDistanceToNow(new Date(run.created_at), { addSuffix: true })
                      : "draft"}
                  </p>
                </div>
                <Badge variant={badgeVariant}>{statusCopy[run.status] ?? run.status}</Badge>
              </div>
              {run.message && <p className="mt-2 text-xs text-slate-500">{run.message}</p>}
            </div>
          );
        })}
        {!data?.length && <p className="text-sm text-slate-500">No runs yet.</p>}
      </div>
    </Card>
  );
}
