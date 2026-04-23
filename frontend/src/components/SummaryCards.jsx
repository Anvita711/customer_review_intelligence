import {
  MessageSquareText,
  CheckCircle2,
  ShieldAlert,
  Copy,
} from "lucide-react";
import clsx from "clsx";

const CARDS = [
  {
    key: "total_input",
    label: "Total Reviews",
    icon: MessageSquareText,
    color: "indigo",
  },
  {
    key: "processed",
    label: "Processed",
    icon: CheckCircle2,
    color: "emerald",
  },
  {
    key: "flagged_spam",
    label: "Spam Detected",
    icon: ShieldAlert,
    color: "red",
  },
  {
    key: "flagged_duplicate",
    label: "Duplicates",
    icon: Copy,
    color: "amber",
  },
];

const BG = {
  indigo: "bg-indigo-50",
  emerald: "bg-emerald-50",
  red: "bg-red-50",
  amber: "bg-amber-50",
};
const ICON_COLOR = {
  indigo: "text-indigo-600",
  emerald: "text-emerald-600",
  red: "text-red-600",
  amber: "text-amber-600",
};
const NUM_COLOR = {
  indigo: "text-indigo-700",
  emerald: "text-emerald-700",
  red: "text-red-700",
  amber: "text-amber-700",
};

export default function SummaryCards({ data }) {
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {CARDS.map(({ key, label, icon: Icon, color }, i) => (
        <div
          key={key}
          className="card animate-slide-up px-5 py-5"
          style={{ animationDelay: `${i * 60}ms` }}
        >
          <div className="flex items-center gap-3">
            <div
              className={clsx(
                "flex h-10 w-10 items-center justify-center rounded-lg",
                BG[color],
              )}
            >
              <Icon className={clsx("h-5 w-5", ICON_COLOR[color])} />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500">{label}</p>
              <p
                className={clsx(
                  "text-2xl font-bold leading-tight",
                  NUM_COLOR[color],
                )}
              >
                {data[key]}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
