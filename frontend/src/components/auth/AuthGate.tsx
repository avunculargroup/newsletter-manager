"use client";

import { FormEvent, ReactNode, useEffect, useState } from "react";
import type { Session } from "@supabase/supabase-js";
import { getSupabaseClient } from "@/lib/supabase";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function AuthGate({ children }: { children: ReactNode }) {
  const supabase = getSupabaseClient();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState<Session | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data: listener } = supabase.auth.onAuthStateChange((_event, sess) => {
      setSession(sess);
    });
    return () => {
      listener.subscription.unsubscribe();
    };
  }, [supabase]);

  if (!supabase) {
    return <>{children}</>;
  }

  if (session) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white/70 px-4 py-3 text-sm text-slate-600">
          Signed in as {session.user.email}
          <Button
            variant="ghost"
            onClick={() => {
              supabase.auth.signOut();
            }}
          >
            Sign out
          </Button>
        </div>
        {children}
      </div>
    );
  }

  const requestMagicLink = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const { error } = await supabase.auth.signInWithOtp({ email, options: { emailRedirectTo: window.location.origin } });
      if (error) throw error;
      setMessage("Check your inbox for the magic link");
    } catch (err) {
      setMessage((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={requestMagicLink}
      className="max-w-md space-y-4 rounded-2xl border border-slate-200 bg-white/70 p-6"
    >
      <p className="text-sm text-slate-600">Sign in to access the dashboard</p>
      <Input
        type="email"
        placeholder="you@example.com"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        required
      />
      <Button type="submit" loading={loading} className="w-full">
        Email me a magic link
      </Button>
      {message && <p className="text-xs text-slate-500">{message}</p>}
    </form>
  );
}
