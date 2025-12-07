"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { api } from "@/lib/api";
import { TopicPreset } from "@/lib/types";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

const schema = z.object({
  name: z.string().min(3),
  topics: z.string().min(3),
  rss_feeds: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function TopicsForm() {
  const queryClient = useQueryClient();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: "Weekly AI", topics: "AI, LLMs, Research" },
  });

  const { data: presets, isLoading } = useQuery({
    queryKey: ["topics"],
    queryFn: api.getTopics,
  });

  const mutation = useMutation({
    mutationFn: (payload: TopicPreset) => api.upsertTopic(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["topics"] });
      reset();
    },
  });

  const formatted = useMemo(() => {
    if (!presets?.length) return "No presets yet";
    return presets
      .map((preset) => `${preset.name}: ${preset.topics.join(", ")}`)
      .join("\n");
  }, [presets]);

  const onSubmit = handleSubmit((values) => {
    const payload: TopicPreset = {
      name: values.name,
      topics: values.topics.split(",").map((topic) => topic.trim()).filter(Boolean),
      rss_feeds: values.rss_feeds
        ?.split(/\s|,/)
        .map((feed) => feed.trim())
        .filter(Boolean),
    };
    mutation.mutate(payload);
  });

  return (
    <Card className="h-full">
      <CardHeader>
        <div>
          <CardTitle>Topics & Sources</CardTitle>
          <CardDescription>
            Configure default topics and supplemental RSS feeds that the pipeline pulls from.
          </CardDescription>
        </div>
      </CardHeader>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="text-sm text-slate-500">Preset name</label>
          <Input {...register("name")} />
          {errors.name && <p className="text-xs text-rose-500">{errors.name.message}</p>}
        </div>
        <div>
          <label className="text-sm text-slate-500">Topics (comma separated)</label>
          <Input {...register("topics")} />
          {errors.topics && <p className="text-xs text-rose-500">{errors.topics.message}</p>}
        </div>
        <div>
          <label className="text-sm text-slate-500">RSS feeds (optional)</label>
          <Textarea rows={3} placeholder="https://example.com/rss" {...register("rss_feeds")} />
        </div>
        <div className="flex items-center gap-3">
          <Button type="submit" loading={mutation.isPending}>
            Save preset
          </Button>
          {mutation.isError && (
            <p className="text-xs text-rose-600">{(mutation.error as Error).message}</p>
          )}
          {mutation.isSuccess && <p className="text-xs text-emerald-600">Saved!</p>}
        </div>
      </form>
      <div className="mt-6 rounded-xl bg-slate-50 p-4 text-sm text-slate-600">
        <p className="mb-2 font-medium text-slate-700">Current presets</p>
        <pre className="whitespace-pre-wrap text-xs">
          {isLoading ? "Loading…" : formatted}
        </pre>
      </div>
    </Card>
  );
}
