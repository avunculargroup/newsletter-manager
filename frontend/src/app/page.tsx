import { AuthGate } from "@/components/auth/AuthGate";
import { DraftPreview } from "@/components/dashboard/DraftPreview";
import { ManualTrigger } from "@/components/dashboard/ManualTrigger";
import { RunHistory } from "@/components/dashboard/RunHistory";
import { ScheduleCard } from "@/components/dashboard/ScheduleCard";
import { StatusHeader } from "@/components/dashboard/StatusHeader";
import { TopicsForm } from "@/components/dashboard/TopicsForm";

export default function Page() {
  return (
    <main className="min-h-screen bg-slate-50 pb-16">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-10">
        <StatusHeader />
        <AuthGate>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <ManualTrigger />
            <TopicsForm />
            <ScheduleCard />
          </div>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <RunHistory />
            <DraftPreview className="lg:col-span-2" />
          </div>
        </AuthGate>
      </div>
    </main>
  );
}
