"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  Check,
  Clapperboard,
  Film,
  Globe,
  Image as ImageIcon,
  Lightbulb,
  Sparkles,
  Volume2,
  VolumeX,
} from "lucide-react";
import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * An auto-playing, looping "product video" of the ScaleX AI pipeline:
 * add a product link → pick an idea → script + frames → realistic AI video.
 * Uses the real Multi Vitamin SPF 50 photos and its actual AI-generated
 * storyboard frames (in /public/demo). Loops forever like a demo reel.
 */

const STAGE_MS = 3600;

const STAGES = [
  { key: "import", label: "Import", icon: Globe },
  { key: "ideas", label: "Ideas", icon: Lightbulb },
  { key: "script", label: "Script", icon: Clapperboard },
  { key: "video", label: "Video", icon: Film },
] as const;

const PRODUCT_PHOTOS = [
  "/demo/product-1.jpg",
  "/demo/product-2.jpg",
  "/demo/product-3.jpg",
  "/demo/product-4.jpg",
];

const FRAMES = [
  "/demo/frame-1.jpg",
  "/demo/frame-2.jpg",
  "/demo/frame-3.jpg",
  "/demo/frame-4.jpg",
  "/demo/frame-5.jpg",
];

const IDEAS = [
  { title: "Own the Moment", hook: "Vitamins meet the ocean breeze." },
  { title: "Glow On Duty", hook: "Skin ka daily bodyguard." },
  { title: "No White Cast", hook: "Bas glow, kuch aur nahi." },
  { title: "Beach-Proof", hook: "Waves se pehle, SPF." },
];

const SCRIPT_LINES = [
  "S1 — Ocean close-up; camera pans to the bottle on the sand.",
  "S2 — Bottle opens; vitamins A, B3, B5, E & F spiral in the breeze.",
  "S3 — Vitamins wrap her face — she smiles, product in hand.",
  "S4 — She walks the beach, sun-bright, skin glowing.",
  "S5 — CTA: “Multi Vitamin SPF 50 se, own the moment!”",
];

const pop = {
  initial: { opacity: 0, y: 10, scale: 0.96 },
  animate: { opacity: 1, y: 0, scale: 1 },
};

function SceneShell({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -14 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      className="absolute inset-0 flex flex-col gap-3 p-4 sm:p-5"
    >
      {children}
    </motion.div>
  );
}

/** Stage 1 — a product link becomes a product card + its real photos. */
function ImportScene() {
  return (
    <SceneShell>
      <div className="flex items-center gap-2 rounded-xl border border-white/[0.08] bg-background/50 px-3 py-2">
        <Globe className="h-3.5 w-3.5 shrink-0 text-accent" />
        <span className="overflow-hidden whitespace-nowrap">
          <motion.span
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ duration: 1.1, delay: 0.2, ease: "easeOut" }}
            className="block overflow-hidden text-xs text-muted-foreground"
          >
            beminimalist.co/multi-vitamin-spf-50…
          </motion.span>
        </span>
        <motion.span
          {...pop}
          transition={{ delay: 1.4 }}
          className="ml-auto shrink-0 rounded-full bg-success/15 px-2 py-0.5 text-[10px] font-medium text-success"
        >
          Imported
        </motion.span>
      </div>

      <motion.div
        {...pop}
        transition={{ delay: 1.5 }}
        className="glass flex items-center gap-3 rounded-2xl p-3"
      >
        <div className="h-11 w-11 shrink-0 overflow-hidden rounded-xl bg-white">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/demo/product-1.jpg" alt="Multi Vitamin SPF 50" className="h-full w-full object-contain" />
        </div>
        <div className="min-w-0">
          <p className="truncate font-display text-sm font-semibold">Multi Vitamin SPF 50</p>
          <p className="text-xs text-muted-foreground">₹399 · 12 photos · details captured</p>
        </div>
        <span className="ml-auto rounded-full bg-primary/15 px-2 py-0.5 text-[10px] font-medium text-primary">
          Ready
        </span>
      </motion.div>

      <div className="grid grid-cols-4 gap-2">
        {PRODUCT_PHOTOS.map((src, i) => (
          <motion.div
            key={src}
            {...pop}
            transition={{ delay: 1.8 + i * 0.14 }}
            className="relative h-20 overflow-hidden rounded-xl bg-white ring-1 ring-white/10 sm:h-24"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={src} alt={`Product photo ${i + 1}`} className="h-full w-full object-contain p-1" />
            {i < 2 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 2.5 + i * 0.15, type: "spring", stiffness: 400 }}
                className="absolute right-1 top-1 grid h-4 w-4 place-items-center rounded-full bg-primary text-white"
              >
                <Check className="h-2.5 w-2.5" />
              </motion.span>
            )}
          </motion.div>
        ))}
      </div>
      <p className="mt-auto text-[11px] text-muted-foreground">
        Pick which photos the AI is allowed to use.
      </p>
    </SceneShell>
  );
}

/** Stage 2 — AI ideas appear, one gets chosen. */
function IdeasScene() {
  return (
    <SceneShell>
      <p className="text-xs text-muted-foreground">
        “Make it feel fresh, young, beach-day energy…”
      </p>
      <div className="grid flex-1 grid-cols-2 gap-2">
        {IDEAS.map((idea, i) => (
          <motion.div
            key={idea.title}
            {...pop}
            transition={{ delay: 0.25 + i * 0.16 }}
            className="relative flex flex-col justify-center rounded-2xl border border-white/[0.07] bg-white/[0.03] p-3"
          >
            {i === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.6 }}
                className="absolute inset-0 rounded-2xl ring-2 ring-primary/70"
              />
            )}
            <p className="font-display text-xs font-semibold sm:text-sm">{idea.title}</p>
            <p className="mt-0.5 truncate text-[10px] italic text-muted-foreground sm:text-[11px]">
              “{idea.hook}”
            </p>
            {i === 0 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 1.75, type: "spring", stiffness: 380 }}
                className="absolute -right-1.5 -top-1.5 inline-flex items-center gap-0.5 rounded-full bg-success px-1.5 py-0.5 text-[9px] font-semibold text-white shadow"
              >
                <Check className="h-2.5 w-2.5" /> Done
              </motion.span>
            )}
          </motion.div>
        ))}
      </div>
      <p className="text-[11px] text-muted-foreground">
        4 directions generated — click one to build its video.
      </p>
    </SceneShell>
  );
}

/** Stage 3 — the 5-scene script writes itself + its real AI frames land. */
function ScriptScene() {
  return (
    <SceneShell>
      <div className="glass min-h-0 flex-1 space-y-1 overflow-hidden rounded-2xl p-3">
        <div className="flex items-center gap-1.5 text-[11px] font-medium text-primary">
          <Sparkles className="h-3 w-3" /> Script · Own the Moment
        </div>
        {SCRIPT_LINES.map((line, i) => (
          <motion.p
            key={line}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.25 + i * 0.24 }}
            className="truncate font-mono text-[9px] leading-snug text-foreground/85 sm:text-[10.5px]"
          >
            {line}
          </motion.p>
        ))}
      </div>
      <div className="flex justify-center gap-2">
        {FRAMES.map((src, i) => (
          <motion.div
            key={src}
            {...pop}
            transition={{ delay: 1.6 + i * 0.14 }}
            className="aspect-[9/16] h-20 overflow-hidden rounded-lg ring-1 ring-white/10 sm:h-[88px]"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={src} alt={`Frame ${i + 1}`} className="h-full w-full object-cover" />
          </motion.div>
        ))}
      </div>
      <p className="text-center text-[11px] text-muted-foreground">
        Frames generated — review before render.
      </p>
    </SceneShell>
  );
}

/** Stage 4 — the real rendered ad plays (muted); hovering it turns the sound on. */
function VideoScene() {
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const [sound, setSound] = React.useState(false);

  // Kick muted autoplay in case the browser missed the autoPlay attribute.
  React.useEffect(() => {
    videoRef.current?.play().catch(() => undefined);
  }, []);

  const soundOn = () => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = false;
    v.volume = 1;
    setSound(true);
    v.play()?.catch(() => {
      // Browser blocked unmuted playback (no prior interaction) — stay muted.
      v.muted = true;
      setSound(false);
      v.play().catch(() => undefined);
    });
  };
  const soundOff = () => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = true;
    setSound(false);
  };

  return (
    <SceneShell>
      <div className="flex flex-1 items-center justify-center gap-4 sm:gap-6">
        {/* Phone-frame vertical video — the actual rendered ad */}
        <div
          onMouseEnter={soundOn}
          onMouseLeave={soundOff}
          className="group relative aspect-[9/16] h-full max-h-[225px] w-auto cursor-pointer overflow-hidden rounded-2xl ring-2 ring-white/15"
        >
          <video
            ref={videoRef}
            src="/demo/ad.mp4"
            poster="/demo/frame-5.jpg"
            autoPlay
            muted
            loop
            playsInline
            className="absolute inset-0 h-full w-full object-cover"
          />
          <span
            className={cn(
              "absolute inset-x-0 bottom-0 flex items-center justify-center gap-1 bg-gradient-to-t from-black/70 to-transparent pb-1.5 pt-5 text-[9px] font-medium transition-colors",
              sound ? "text-accent" : "text-white/85"
            )}
          >
            {sound ? <Volume2 className="h-3 w-3" /> : <VolumeX className="h-3 w-3" />}
            {sound ? "Sound on" : "Hover for sound"}
          </span>
        </div>

        <div className="max-w-[190px] space-y-2.5">
          <motion.div {...pop} transition={{ delay: 0.4 }} className="flex items-center gap-1.5">
            <span className="rounded-full bg-success/15 px-2 py-0.5 text-[10px] font-semibold text-success">
              Rendered
            </span>
            <span className="text-[10px] text-muted-foreground">multi-shot · 9:16</span>
          </motion.div>
          <motion.p {...pop} transition={{ delay: 0.6 }} className="font-display text-sm font-semibold leading-snug">
            “Multi Vitamin SPF 50 se, own the moment!”
          </motion.p>
          <motion.p {...pop} transition={{ delay: 0.75 }} className="text-[11px] text-muted-foreground">
            Real presenter. Your exact product. Hinglish voice.
          </motion.p>
          {/* audio equalizer */}
          <motion.div {...pop} transition={{ delay: 0.9 }} className="flex items-end gap-1">
            <Volume2 className="mr-1 h-3.5 w-3.5 text-accent" />
            {[10, 16, 8, 18, 12, 20, 9, 14].map((h, i) => (
              <motion.span
                key={i}
                animate={{ height: [h * 0.4, h, h * 0.55, h * 0.9] }}
                transition={{ duration: 0.9, repeat: Infinity, repeatType: "mirror", delay: i * 0.08 }}
                className="w-1 rounded-full bg-aurora-line"
                style={{ height: h }}
              />
            ))}
          </motion.div>
        </div>
      </div>
    </SceneShell>
  );
}

const SCENES = [ImportScene, IdeasScene, ScriptScene, VideoScene];

export function DashboardPreview() {
  const [stage, setStage] = React.useState(0);
  const [epoch, setEpoch] = React.useState(0); // bumps on manual jumps → restarts the timer
  const [paused, setPaused] = React.useState(false); // hover pauses the auto-advance

  React.useEffect(() => {
    if (paused) return;
    const t = setInterval(() => setStage((s) => (s + 1) % STAGES.length), STAGE_MS);
    return () => clearInterval(t);
  }, [epoch, paused]);

  const Scene = SCENES[stage];

  return (
    <motion.div
      initial={{ opacity: 0, y: 40, rotateX: 8 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      transition={{ duration: 0.9, delay: 0.35, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -6 }}
      onHoverStart={() => setPaused(true)}
      onHoverEnd={() => {
        setPaused(false);
        setEpoch((e) => e + 1); // fresh timer (and progress bar) on resume
      }}
      style={{ perspective: 1200 }}
      className="relative mx-auto w-full max-w-5xl"
    >
      {/* Aurora glow behind the card */}
      <div className="pointer-events-none absolute -inset-8 -z-10 rounded-[2.5rem] bg-aurora-radial opacity-70 blur-2xl" />

      <div className="glass-strong overflow-hidden rounded-3xl shadow-glow">
        {/* Browser top bar */}
        <div className="flex items-center gap-4 border-b border-white/[0.06] bg-white/[0.02] px-5 py-3.5">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-destructive/80" />
            <span className="h-3 w-3 rounded-full bg-aurora-emerald/70" />
            <span className="h-3 w-3 rounded-full bg-accent/70" />
          </div>
          <div className="mx-auto hidden max-w-sm flex-1 items-center justify-center gap-2 rounded-lg border border-white/[0.06] bg-background/40 px-3 py-1.5 text-xs text-muted-foreground sm:flex">
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            scalex-ai/studio · Multi Vitamin SPF 50
          </div>
          <div className="hidden h-6 w-16 rounded-md bg-white/[0.04] sm:block" />
        </div>

        {/* Body: pipeline stepper + animated scene */}
        <div className="grid gap-4 p-4 sm:gap-5 sm:p-6 lg:grid-cols-5">
          {/* Stepper */}
          <div className="flex gap-2 lg:col-span-2 lg:flex-col lg:gap-3 lg:pr-2">
            {STAGES.map((s, i) => {
              const Icon = s.icon;
              const active = i === stage;
              const done = i < stage;
              return (
                <button
                  key={s.key}
                  type="button"
                  onClick={() => {
                    setStage(i);
                    setEpoch((e) => e + 1);
                  }}
                  className={cn(
                    "group relative flex flex-1 items-center gap-2.5 overflow-hidden rounded-2xl border px-3 py-2.5 text-left transition-colors lg:flex-none lg:px-4 lg:py-3.5",
                    active
                      ? "border-primary/40 bg-primary/10"
                      : "border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.04]"
                  )}
                >
                  <span
                    className={cn(
                      "grid h-8 w-8 shrink-0 place-items-center rounded-xl transition-colors",
                      active
                        ? "bg-aurora-line text-white shadow-glow"
                        : done
                          ? "bg-success/20 text-success"
                          : "bg-white/[0.05] text-muted-foreground"
                    )}
                  >
                    {done ? <Check className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
                  </span>
                  <span className="hidden min-w-0 sm:block">
                    <span
                      className={cn(
                        "block text-sm font-medium",
                        active ? "text-foreground" : "text-muted-foreground"
                      )}
                    >
                      {s.label}
                    </span>
                  </span>
                  {active && (
                    <span
                      key={`bar-${stage}-${epoch}`}
                      style={{
                        animation: `demo-progress ${STAGE_MS}ms linear forwards`,
                        animationPlayState: paused ? "paused" : "running",
                      }}
                      className="absolute bottom-0 left-0 h-0.5 w-0 bg-aurora-line"
                    />
                  )}
                </button>
              );
            })}
            <div className="mt-auto hidden items-center gap-2 rounded-2xl border border-white/[0.06] bg-white/[0.02] px-4 py-3 lg:flex">
              <span className="h-2 w-2 animate-pulse rounded-full bg-success shadow-[0_0_8px_hsl(var(--success))]" />
              <p className="text-xs text-muted-foreground">
                Live AI · URL → idea → script → realistic video
              </p>
            </div>
          </div>

          {/* Scene viewport */}
          <div className="relative h-[290px] overflow-hidden rounded-2xl border border-white/[0.06] bg-background/30 sm:h-[300px] lg:col-span-3">
            <AnimatePresence mode="wait">
              <Scene key={stage} />
            </AnimatePresence>
            <div className="pointer-events-none absolute right-3 top-3 hidden items-center gap-1 rounded-full bg-black/40 px-2 py-0.5 text-[10px] text-white/80 backdrop-blur sm:flex">
              <ImageIcon className="h-3 w-3" />
              demo
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
