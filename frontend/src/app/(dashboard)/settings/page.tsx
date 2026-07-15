"use client";

import { Cpu, HardDrive, Info, Moon, Palette, Save, Settings as SettingsIcon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import * as React from "react";
import { FadeUp } from "@/components/animations/motion";
import { PageHeader } from "@/components/shared/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useSettings, useSystemInfo, useUpdateSettings } from "@/lib/hooks";
import { cn } from "@/lib/utils";

const LANGS = [
  { value: "en", label: "English" },
  { value: "es", label: "Español" },
  { value: "fr", label: "Français" },
  { value: "de", label: "Deutsch" },
];
const TONES = ["luxury", "professional", "friendly", "minimal"];

export default function SettingsPage() {
  const { data: settings } = useSettings();
  const { data: system } = useSystemInfo();
  const update = useUpdateSettings();
  const { theme, setTheme } = useTheme();

  const prefs = (settings?.generation_prefs ?? {}) as {
    default_tone?: string;
    default_variations?: number;
    auto_score?: boolean;
  };

  const [tone, setTone] = React.useState("professional");
  const [variations, setVariations] = React.useState("3");
  const [autoScore, setAutoScore] = React.useState(true);

  React.useEffect(() => {
    if (settings) {
      setTone(prefs.default_tone ?? "professional");
      setVariations(String(prefs.default_variations ?? 3));
      setAutoScore(prefs.auto_score ?? true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settings]);

  const isDark = theme !== "light";

  function saveGeneration() {
    update.mutate({
      generation_prefs: {
        ...prefs,
        default_tone: tone,
        default_variations: Number(variations),
        auto_score: autoScore,
      },
    });
  }

  return (
    <div>
      <PageHeader icon={SettingsIcon} title="Settings" description="Preferences & system." />

      <div className="grid gap-6 lg:grid-cols-2">
        <FadeUp>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Palette className="h-5 w-5 text-primary" /> Appearance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="flex items-center justify-between">
                <Label>Theme</Label>
                <div className="flex gap-1 rounded-xl glass p-1">
                  {[
                    { v: "dark", icon: Moon, label: "Dark" },
                    { v: "light", icon: Sun, label: "Light" },
                  ].map(({ v, icon: Icon, label }) => (
                    <button
                      key={v}
                      onClick={() => {
                        setTheme(v);
                        update.mutate({ theme: v });
                      }}
                      className={cn(
                        "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition-colors",
                        (v === "dark" ? isDark : !isDark)
                          ? "bg-primary/15 text-primary"
                          : "text-muted-foreground hover:text-foreground"
                      )}
                    >
                      <Icon className="h-4 w-4" /> {label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex items-center justify-between gap-4">
                <Label>Language</Label>
                <div className="w-44">
                  <Select
                    value={settings?.language ?? "en"}
                    onValueChange={(v) => update.mutate({ language: v })}
                  >
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {LANGS.map((l) => (
                        <SelectItem key={l.value} value={l.value}>{l.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </FadeUp>

        <FadeUp delay={0.05}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Cpu className="h-5 w-5 text-primary" /> AI engine</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>Status</Label>
                <Badge variant={system?.ai_mode === "live" ? "success" : "accent"}>
                  {system?.ai_mode === "live" ? "Live" : "Mock"}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                The ScaleX engine powers analysis, ideas, copy, scripts, images and video.
                In live mode it generates fresh, product-specific creative; otherwise every
                surface uses realistic sample content so you can explore the studio offline.
              </p>
            </CardContent>
          </Card>
        </FadeUp>

        <FadeUp delay={0.1}>
          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle>Generation preferences</CardTitle>
              <Button variant="glass" size="sm" onClick={saveGeneration} disabled={update.isPending}>
                <Save className="h-4 w-4" /> Save
              </Button>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="flex items-center justify-between gap-4">
                <Label>Default tone</Label>
                <div className="w-44">
                  <Select value={tone} onValueChange={setTone}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {TONES.map((t) => (
                        <SelectItem key={t} value={t}>{t[0].toUpperCase() + t.slice(1)}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex items-center justify-between gap-4">
                <Label>Default variations</Label>
                <div className="w-44">
                  <Select value={variations} onValueChange={setVariations}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6].map((n) => (
                        <SelectItem key={n} value={String(n)}>{n}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto-score creatives</Label>
                  <p className="text-xs text-muted-foreground">Score copy right after generating.</p>
                </div>
                <Switch checked={autoScore} onCheckedChange={setAutoScore} />
              </div>
            </CardContent>
          </Card>
        </FadeUp>

        <FadeUp delay={0.15}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><HardDrive className="h-5 w-5 text-primary" /> Storage</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Backend</Label>
                <Badge variant="secondary" className="uppercase">{system?.storage_backend ?? "local"}</Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Assets are stored locally for the MVP. S3 / Cloudflare R2 are a drop-in upgrade later.
              </p>
            </CardContent>
          </Card>
        </FadeUp>

        <FadeUp delay={0.2} className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Info className="h-5 w-5 text-primary" /> System information</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid gap-x-8 gap-y-3 sm:grid-cols-2">
                <Row label="Application" value={system?.app_name} />
                <Row label="Version" value={system?.version} />
                <Row label="Environment" value={system?.environment} />
                <Row label="Storage" value={system?.storage_backend} />
                <ModeRow label="Text & ideas" mode={system?.text_mode} />
                <ModeRow label="Images" mode={system?.image_mode} />
                <ModeRow label="Video" detail="Indian model · Hinglish · multi-shot" mode={system?.video_mode} />
              </dl>
            </CardContent>
          </Card>
        </FadeUp>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value?: string }) {
  return (
    <div className="flex items-center justify-between border-b border-border/60 pb-2">
      <dt className="text-sm text-muted-foreground">{label}</dt>
      <dd className="text-sm font-medium">{value ?? "—"}</dd>
    </div>
  );
}

function ModeRow({
  label,
  detail,
  mode,
}: {
  label: string;
  detail?: string;
  mode?: "live" | "mock";
}) {
  return (
    <div className="flex items-center justify-between border-b border-border/60 pb-2">
      <dt className="text-sm text-muted-foreground">
        {label}
        {detail && <span className="ml-1 text-xs text-muted-foreground/60">· {detail}</span>}
      </dt>
      <dd>
        <Badge variant={mode === "live" ? "success" : "accent"}>
          {mode === "live" ? "Live" : "Mock"}
        </Badge>
      </dd>
    </div>
  );
}
