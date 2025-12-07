"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Image from "next/image";
import { clsx } from "clsx";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DraftSection } from "@/lib/types";
import { useState } from "react";

type Props = {
  className?: string;
};

export function DraftPreview({ className }: Props) {
  const { data, refetch, isFetching } = useQuery({
    queryKey: ["draft"],
    queryFn: api.getLatestDraft,
    refetchInterval: 20000,
  });
  const [copied, setCopied] = useState(false);

  const copyHtml = async () => {
    if (!data?.html) return;
    await navigator.clipboard.writeText(data.html);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className={clsx("col-span-2", className)}>
      <CardHeader className="items-start">
        <div>
          <CardTitle>Latest draft</CardTitle>
          <CardDescription>Preview the MJML output before approving.</CardDescription>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => refetch()} disabled={isFetching}>
            Refresh
          </Button>
          <Button variant="secondary" onClick={copyHtml} disabled={!data?.html}>
            {copied ? "Copied" : "Copy HTML"}
          </Button>
        </div>
      </CardHeader>
      {!data ? (
        <p className="text-sm text-slate-500">Trigger a run to generate a draft.</p>
      ) : (
        <div className="space-y-4">
          {data.hero && (
            <div className="overflow-hidden rounded-2xl">
              <div className="relative h-64 w-full">
                <Image
                  src={data.hero.url}
                  alt="Hero"
                  fill
                  priority
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, 50vw"
                />
              </div>
              <p className="bg-slate-50 px-3 py-2 text-xs text-slate-500">{data.hero.attribution}</p>
            </div>
          )}
          <div className="space-y-6">
            {data.sections?.map((section: DraftSection) => (
              <article key={section.title} className="rounded-2xl border border-slate-100 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-blue-600">
                  {section.hook}
                </p>
                <h4 className="mt-1 text-xl font-semibold text-slate-900">{section.title}</h4>
                <p className="mt-2 text-sm text-slate-600">{section.summary}</p>
                <a
                  href={section.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-3 inline-flex text-sm font-semibold text-blue-600"
                >
                  {section.call_to_action}
                </a>
              </article>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
