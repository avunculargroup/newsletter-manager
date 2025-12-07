"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

const schema = z.object({
  topics: z.string().min(3),
  subject: z.string().min(3),
  title: z.string().min(3),
  preheader: z.string().optional(),
  hero_query: z.string().optional(),
  rss_feeds: z.string().optional(),
});

type ManualTriggerForm = z.infer<typeof schema>;

export function ManualTrigger() {
  const queryClient = useQueryClient();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ManualTriggerForm>({
    resolver: zodResolver(schema),
    defaultValues: {
      topics: "AI, Startups, Research",
      subject: "Weekly Brief — Fresh Signals",
      title: "Weekly Brief",
      preheader: "Hand-picked stories generated in minutes",
    },
  });

  const mutation = useMutation({
    mutationFn: (payload: ManualTriggerForm) =>
      api.triggerRun({
        ...payload,
        topics: payload.topics.split(",").map((topic) => topic.trim()).filter(Boolean),
        rss_feeds: payload.rss_feeds
          ?.split(/\\s|,/)
          .map((feed) => feed.trim())
          .filter(Boolean),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
      queryClient.invalidateQueries({ queryKey: ["draft"] });
      reset();
    },
  });

  const onSubmit = handleSubmit((values) => {
    mutation.mutate(values);
  });

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Manual trigger</CardTitle>
          <CardDescription>Override the scheduler and kick off a run immediately.</CardDescription>
        </div>
      </CardHeader>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="text-sm text-slate-500">Topics</label>
          <Textarea rows={2} {...register("topics")} />
          {errors.topics && <p className="text-xs text-rose-600">{errors.topics.message}</p>}
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="text-sm text-slate-500">Subject</label>
            <Input {...register("subject")} />
          </div>
          <div>
            <label className="text-sm text-slate-500">Title</label>
            <Input {...register("title")} />
          </div>
        </div>
        <div>
          <label className="text-sm text-slate-500">Preheader</label>
          <Input {...register("preheader")} />
        </div>
        <div>
          <label className="text-sm text-slate-500">Hero image hint</label>
          <Input placeholder="Generative AI" {...register("hero_query")} />
        </div>
        <div>
          <label className="text-sm text-slate-500">RSS feeds (optional)</label>
          <Textarea rows={2} placeholder="https://example.com/rss" {...register("rss_feeds")} />
        </div>
        <Button type="submit" loading={mutation.isPending} className="w-full">
          Trigger run
        </Button>
        {mutation.isError && (
          <p className="text-xs text-rose-600">{(mutation.error as Error).message}</p>
        )}
        {mutation.isSuccess && <p className="text-xs text-emerald-600">Run queued successfully</p>}
      </form>
    </Card>
  );
}
