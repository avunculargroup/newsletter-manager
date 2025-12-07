import { HTMLAttributes } from "react";
import { clsx } from "clsx";

const palette: Record<string, string> = {
  completed: "bg-emerald-100 text-emerald-700",
  running: "bg-blue-100 text-blue-700",
  failed: "bg-rose-100 text-rose-700",
  queued: "bg-amber-100 text-amber-700",
  neutral: "bg-slate-100 text-slate-600",
};

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  variant?: keyof typeof palette;
};

export function Badge({ className, variant = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-3 py-0.5 text-xs font-medium capitalize",
        palette[variant] ?? palette.neutral,
        className,
      )}
      {...props}
    />
  );
}
