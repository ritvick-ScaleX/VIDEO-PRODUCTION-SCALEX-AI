"use client";

import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCircle2,
  Circle,
  Clapperboard,
  Download,
  FileText,
  Film,
  Globe,
  Image as ImageIcon,
  Layers,
  Lightbulb,
  Package,
  Play,
  RefreshCw,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  Trash2,
  Wand2,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import * as React from "react";
import { FadeUp } from "@/components/animations/motion";
import { CopyButton } from "@/components/shared/copy-button";
import { ImageLightbox } from "@/components/shared/image-lightbox";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner, LoadingOverlay } from "@/components/ui/spinner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
  useAnalyze,
  useCopy,
  useDeleteVideo,
  useGenerateCopy,
  useGenerateFrames,
  useGenerateIdeas,
  useGenerateImages,
  useIdeas,
  useImages,
  useProduct,
  useRenderVideo,
  useRepromptVideo,
  useRescrape,
  useReviewImage,
  useCreateScript,
  useSelectIdea,
  useUpdateProduct,
  useUpdateVideo,
  useVideos,
} from "@/lib/hooks";
import type {
  GeneratedVideo,
  Idea,
  IdeaStatus,
  ImageCategory,
  ProductStatus,
} from "@/lib/types";
import { cn, statusLabel, titleCase } from "@/lib/utils";

const STATUS_VARIANT: Record<ProductStatus, NonNullable<BadgeProps["variant"]>> = {
  ready: "success",
  error: "destructive",
  draft: "outline",
  scraping: "accent",
  analyzing: "accent",
};

export default function ProductStudioPage() {
  const params = useParams();
  const id = String(params.id);
  const { data: product, isLoading } = useProduct(id);
  const { data: ideas } = useIdeas(id);
  const analyze = useAnalyze(id);
  const rescrape = useRescrape(id);

  const [tab, setTab] = React.useState("overview");
  const [activeIdeaId, setActiveIdeaId] = React.useState<string | null>(null);
  const [activeImageIdeaId, setActiveImageIdeaId] = React.useState<string | null>(null);

  // Default the active video idea to the one marked "done" (selected).
  React.useEffect(() => {
    if (!activeIdeaId && ideas?.length) {
      const sel = ideas.find((i) => i.status === "selected" && i.kind !== "image");
      if (sel) setActiveIdeaId(sel.id);
    }
  }, [ideas, activeIdeaId]);

  const openIdeaInVideo = React.useCallback((ideaId: string) => {
    setActiveIdeaId(ideaId);
    setTab("video");
  }, []);
  const openIdeaInImages = React.useCallback((ideaId: string) => {
    setActiveImageIdeaId(ideaId);
    setTab("images");
  }, []);

  const activeIdea = ideas?.find((i) => i.id === activeIdeaId) ?? null;

  if (isLoading) return <LoadingOverlay label="Loading product…" />;
  if (!product) {
    return (
      <EmptyState
        icon={Package}
        title="Product not found"
        description="It may have been removed."
        action={
          <Button asChild variant="aurora">
            <Link href="/products">Back to products</Link>
          </Button>
        }
      />
    );
  }

  return (
    <div>
      <FadeUp className="mb-6">
        <Button asChild variant="ghost" size="sm" className="mb-4">
          <Link href="/products">
            <ArrowLeft className="h-4 w-4" /> Products
          </Link>
        </Button>
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex items-start gap-4">
            <div className="grid h-14 w-14 shrink-0 place-items-center overflow-hidden rounded-2xl bg-aurora-line text-white shadow-glow">
              {product.thumbnail_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={product.thumbnail_url} alt={product.name} className="h-full w-full object-cover" />
              ) : (
                <Package className="h-7 w-7" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-display text-2xl font-bold tracking-tight sm:text-3xl">
                  {product.name}
                </h1>
                <Badge variant={STATUS_VARIANT[product.status] ?? "outline"}>
                  {statusLabel(product.status)}
                </Badge>
              </div>
              {product.source_url && (
                <a
                  href={product.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-1 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
                >
                  <Globe className="h-3.5 w-3.5" /> {new URL(product.source_url).hostname}
                </a>
              )}
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            {product.source_type === "url" && (
              <Button variant="glass" onClick={() => rescrape.mutate()} disabled={rescrape.isPending}>
                {rescrape.isPending ? <Spinner /> : <RefreshCw className="h-4 w-4" />} Refresh data
              </Button>
            )}
            <Button variant="aurora" onClick={() => analyze.mutate()} disabled={analyze.isPending}>
              {analyze.isPending ? <Spinner /> : <Sparkles className="h-4 w-4" />} Analyze
            </Button>
          </div>
        </div>
      </FadeUp>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="flex-wrap">
          <TabsTrigger value="overview"><Layers className="h-4 w-4" /> Product Info</TabsTrigger>
          <TabsTrigger value="ideas"><Lightbulb className="h-4 w-4" /> Market Angles</TabsTrigger>
          <TabsTrigger value="images"><ImageIcon className="h-4 w-4" /> Images</TabsTrigger>
          <TabsTrigger value="video"><Film className="h-4 w-4" /> Video</TabsTrigger>
          <TabsTrigger value="copy"><FileText className="h-4 w-4" /> Copy</TabsTrigger>
        </TabsList>

        <TabsContent value="overview"><OverviewTab productId={id} /></TabsContent>
        <TabsContent value="ideas">
          <IdeasTab productId={id} onOpenIdea={openIdeaInVideo} onOpenImageIdea={openIdeaInImages} />
        </TabsContent>
        <TabsContent value="images">
          <ImagesTab
            productId={id}
            activeImageIdeaId={activeImageIdeaId}
            onChangeImageIdea={setActiveImageIdeaId}
          />
        </TabsContent>
        <TabsContent value="video"><VideoTab productId={id} activeIdea={activeIdea} /></TabsContent>
        <TabsContent value="copy"><CopyTab productId={id} /></TabsContent>
      </Tabs>
    </div>
  );
}

/* ------------------------------------------------------------------ Overview */
function OverviewTab({ productId }: { productId: string }) {
  const { data: product } = useProduct(productId);
  if (!product) return null;
  const a = product.analysis ?? {};

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="space-y-6 lg:col-span-2">
        <Card>
          <CardHeader><CardTitle>Product info</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {product.description && (
              <p className="text-sm text-muted-foreground">{product.description}</p>
            )}
            {product.ingredients.length > 0 && (
              <div>
                <p className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Key ingredients
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {product.ingredients.map((ing) => (
                    <Badge key={ing} variant="secondary">{ing}</Badge>
                  ))}
                </div>
              </div>
            )}
            <div className="grid gap-4 sm:grid-cols-2">
              <DetailList title="Features" items={product.features} />
              <DetailList title="Benefits" items={product.benefits} />
            </div>
            <div className="flex flex-wrap gap-4 text-sm">
              {product.price && <Fact label="Price" value={product.price} />}
              {product.target_audience && <Fact label="Target audience" value={product.target_audience} />}
              {product.cta && <Fact label="CTA" value={product.cta} />}
            </div>
          </CardContent>
        </Card>

        {(a.usp || a.strategy_summary || (a.marketing_angles?.length ?? 0) > 0) && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" /> AI analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {a.usp && <Fact label="USP" value={a.usp} />}
              {a.strategy_summary && (
                <p className="text-sm text-muted-foreground">{a.strategy_summary}</p>
              )}
              <div className="grid gap-4 sm:grid-cols-2">
                <DetailList title="Marketing angles" items={a.marketing_angles} />
                <DetailList title="Hooks" items={a.hooks} />
                <DetailList title="Pain points" items={a.pain_points} />
                <DetailList title="Emotional triggers" items={a.emotional_triggers} />
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <div>
        <ImagePicker productId={product.id} />
      </div>
    </div>
  );
}

/** Pick which imported images the AI may use (imports often include stray page images). */
function ImagePicker({ productId }: { productId: string }) {
  const { data: product } = useProduct(productId);
  const save = useUpdateProduct(productId);
  const [preview, setPreview] = React.useState<string | null>(null);
  const images = React.useMemo(() => product?.images ?? [], [product?.images]);

  // Default: everything selected (empty stored selection == "use all").
  const [selected, setSelected] = React.useState<Set<string>>(new Set());
  React.useEffect(() => {
    const stored = product?.selected_images ?? [];
    setSelected(new Set(stored.length ? stored : images));
  }, [product?.selected_images, images]);

  const stored = product?.selected_images ?? [];
  const baseline = stored.length ? stored : images;
  const dirty =
    baseline.length !== selected.size || baseline.some((u) => !selected.has(u));

  function toggle(url: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(url)) next.delete(url);
      else next.add(url);
      return next;
    });
  }

  return (
    <Card>
      <CardHeader className="flex-row items-start justify-between space-y-0">
        <div className="space-y-1">
          <CardTitle>Product images</CardTitle>
          <p className="text-xs text-muted-foreground">
            Tap to choose which the AI uses — {selected.size}/{images.length} selected
          </p>
        </div>
        {images.length > 0 && (
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={() => setSelected(new Set(images))}>
              All
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setSelected(new Set())}>
              None
            </Button>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {images.length === 0 ? (
          <p className="text-sm text-muted-foreground">No images found. Refresh data or add manually.</p>
        ) : (
          <>
            <p className="text-[11px] text-muted-foreground">
              Tap an image to preview · tap the circle to select
            </p>
            <div className="grid grid-cols-2 gap-3">
              {images.map((src, i) => {
                const on = selected.has(src);
                return (
                  <div
                    key={i}
                    className={
                      "group relative aspect-square overflow-hidden rounded-xl ring-1 transition " +
                      (on ? "ring-2 ring-primary" : "ring-white/10 hover:ring-white/25")
                    }
                  >
                    <button
                      type="button"
                      onClick={() => setPreview(src)}
                      className="block h-full w-full"
                      aria-label={`Preview image ${i + 1}`}
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={src}
                        alt={`option ${i + 1}`}
                        className={"h-full w-full cursor-zoom-in object-cover transition " + (on ? "" : "opacity-50 grayscale")}
                      />
                    </button>
                    <button
                      type="button"
                      onClick={() => toggle(src)}
                      className="absolute right-1.5 top-1.5 rounded-full drop-shadow"
                      aria-label={on ? "Deselect image" : "Select image"}
                    >
                      {on ? (
                        <CheckCircle2 className="h-5 w-5 text-primary" fill="white" />
                      ) : (
                        <Circle className="h-5 w-5 text-white/70" />
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
            {dirty && (
              <Button
                variant="aurora"
                size="sm"
                className="w-full"
                disabled={save.isPending}
                onClick={() => save.mutate({ selected_images: Array.from(selected) })}
              >
                {save.isPending ? <Spinner /> : <Check className="h-4 w-4" />} Save selection
              </Button>
            )}
          </>
        )}
        <ImageLightbox src={preview} onClose={() => setPreview(null)} downloadable={false} />
      </CardContent>
    </Card>
  );
}

function DetailList({ title, items }: { title: string; items?: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <p className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        {title}
      </p>
      <ul className="space-y-1">
        {items.map((it, i) => (
          <li key={i} className="flex items-start gap-2 text-sm">
            <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="text-sm font-medium">{value}</p>
    </div>
  );
}

/* -------------------------------------------------------------------- Images */
const IMAGE_CATEGORIES: { value: ImageCategory; label: string; desc: string }[] = [
  { value: "white_background", label: "White background", desc: "Clean e-commerce packshot on pure white" },
  { value: "product_shot", label: "Product shot", desc: "Product only, staged in a real scene — no model" },
  { value: "creative", label: "Creative", desc: "Lifestyle scene with a realistic human model" },
];
// Meta ad placements: square (feed) and story (9:16 Stories/Reels) only.
const IMAGE_FORMATS = ["square", "story"];

function ImagesTab({
  productId,
  activeImageIdeaId,
  onChangeImageIdea,
}: {
  productId: string;
  activeImageIdeaId: string | null;
  onChangeImageIdea: (id: string | null) => void;
}) {
  const { data: images, isLoading } = useImages(productId);
  const { data: allIdeas } = useIdeas(productId);
  const generate = useGenerateImages(productId);
  const review = useReviewImage(productId);
  const [category, setCategory] = React.useState<ImageCategory>("creative");
  const [format, setFormat] = React.useState("square");
  const [count, setCount] = React.useState("2");
  const [prompt, setPrompt] = React.useState("");
  const [preview, setPreview] = React.useState<string | null>(null);
  // Reject flow: which image is being rejected + the feedback comment.
  const [rejectId, setRejectId] = React.useState<string | null>(null);
  const [rejectComment, setRejectComment] = React.useState("");

  const imageIdeas = (allIdeas ?? []).filter((i) => i.kind === "image");
  const activeIdea = imageIdeas.find((i) => i.id === activeImageIdeaId) ?? null;

  function run() {
    generate.mutate({
      category,
      format,
      count: Number(count),
      prompt: prompt.trim() || undefined,
      idea_id: activeImageIdeaId ?? undefined,
    });
  }

  function submitReject() {
    if (!rejectId) return;
    review.mutate(
      { id: rejectId, status: "rejected", comment: rejectComment.trim() || undefined },
      {
        onSuccess: () => {
          setRejectId(null);
          setRejectComment("");
        },
      }
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Card className="lg:col-span-1 h-fit">
        <CardHeader><CardTitle>Generate images</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label>Market angle</Label>
            <Select
              value={activeImageIdeaId ?? "none"}
              onValueChange={(v) => onChangeImageIdea(v === "none" ? null : v)}
            >
              <SelectTrigger><SelectValue placeholder="No angle — freestyle" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">No angle — freestyle</SelectItem>
                {imageIdeas.map((i) => (
                  <SelectItem key={i.id} value={i.id}>{i.title ?? "Untitled"}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {activeIdea ? (
              <p className="line-clamp-2 text-xs text-muted-foreground">{activeIdea.description}</p>
            ) : (
              <p className="text-xs text-muted-foreground">
                Pick an image idea from Market Angles to art-direct the scene.
              </p>
            )}
          </div>
          <div className="space-y-1.5">
            <Label>Category</Label>
            <Select value={category} onValueChange={(v) => setCategory(v as ImageCategory)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {IMAGE_CATEGORIES.map((c) => (
                  <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {IMAGE_CATEGORIES.find((c) => c.value === category)?.desc}
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Format</Label>
              <Select value={format} onValueChange={setFormat}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {IMAGE_FORMATS.map((f) => (
                    <SelectItem key={f} value={f}>{titleCase(f)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Count</Label>
              <Select value={count} onValueChange={setCount}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {[1, 2, 3, 4].map((n) => (
                    <SelectItem key={n} value={String(n)}>{n}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>Extra direction (optional)</Label>
            <Textarea
              placeholder="e.g. golden-hour lighting, on a marble surface"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>
          <Button variant="aurora" className="w-full" onClick={run} disabled={generate.isPending}>
            {generate.isPending ? <Spinner /> : <Wand2 className="h-4 w-4" />}
            {generate.isPending ? "Generating…" : "Generate"}
          </Button>
        </CardContent>
      </Card>

      <div className="lg:col-span-2">
        {isLoading ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className={format === "story" ? "aspect-[9/16]" : "aspect-square"} />
            ))}
          </div>
        ) : generate.isPending || (images && images.length > 0) ? (
          <div className="columns-2 gap-4 sm:columns-3">
            {/* Masonry catalog — mixed square / 9:16 story tiles pack tightly, no gaps. */}
            {/* Mount-based fade (not viewport-gated) so freshly generated images appear at once. */}
            {/* Placeholder tiles while generating — new images drop in here automatically. */}
            {generate.isPending &&
              Array.from({ length: Math.max(1, Number(count)) }).map((_, i) => (
                <div
                  key={`pending-${i}`}
                  className={cn(
                    "mb-4 flex break-inside-avoid flex-col items-center justify-center gap-2 rounded-2xl glass ring-1 ring-white/10",
                    format === "story" ? "aspect-[9/16]" : "aspect-square"
                  )}
                >
                  <Spinner className="h-5 w-5 text-primary" />
                  <span className="text-xs text-muted-foreground">Generating…</span>
                </div>
              ))}
            {(images ?? []).map((img) => (
              <FadeUp key={img.id} className="mb-4 break-inside-avoid">
                <div
                  className={cn(
                    "group relative overflow-hidden rounded-2xl ring-1 transition",
                    img.review_status === "accepted"
                      ? "ring-2 ring-success/70"
                      : img.review_status === "rejected"
                        ? "ring-2 ring-destructive/60"
                        : "ring-white/10"
                  )}
                >
                  <button
                    type="button"
                    onClick={() => setPreview(img.url)}
                    className="block w-full"
                    aria-label="Preview image"
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={img.url}
                      alt={img.prompt ?? "Generated"}
                      className={cn(
                        "w-full cursor-zoom-in object-cover",
                        img.format === "story" ? "aspect-[9/16]" : "aspect-square",
                        img.review_status === "rejected" && "opacity-60"
                      )}
                    />
                  </button>
                  {/* review tag */}
                  {img.review_status !== "pending" && (
                    <span
                      className={cn(
                        "pointer-events-none absolute left-2 top-2 rounded-full px-2 py-0.5 text-[10px] font-semibold text-white shadow",
                        img.review_status === "accepted" ? "bg-emerald-500/90" : "bg-red-500/90"
                      )}
                      title={img.review_comment ?? undefined}
                    >
                      {img.review_status === "accepted" ? "Accepted" : "Rejected"}
                    </span>
                  )}
                  <div className="pointer-events-none absolute inset-x-0 bottom-0 flex items-center justify-between gap-1.5 bg-gradient-to-t from-black/75 to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100">
                    <Badge variant="secondary" className="capitalize">{img.category.replace("_", " ")}</Badge>
                    <span className="flex items-center gap-1.5">
                      <Button
                        variant="glass"
                        size="icon"
                        className="pointer-events-auto h-8 w-8 text-emerald-400 hover:text-emerald-300"
                        aria-label="Accept image"
                        disabled={review.isPending}
                        onClick={() => review.mutate({ id: img.id, status: "accepted" })}
                      >
                        <ThumbsUp className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="glass"
                        size="icon"
                        className="pointer-events-auto h-8 w-8 text-red-400 hover:text-red-300"
                        aria-label="Reject image"
                        disabled={review.isPending}
                        onClick={() => {
                          setRejectId(img.id);
                          setRejectComment(img.review_comment ?? "");
                        }}
                      >
                        <ThumbsDown className="h-4 w-4" />
                      </Button>
                      <Button asChild variant="glass" size="icon" className="pointer-events-auto h-8 w-8">
                        <a href={img.url} download target="_blank" rel="noopener noreferrer">
                          <Download className="h-4 w-4" />
                        </a>
                      </Button>
                    </span>
                  </div>
                </div>
              </FadeUp>
            ))}
          </div>
        ) : (
          <EmptyState icon={ImageIcon} title="No images yet" description="Generate your first product images on the left." />
        )}
      </div>
      <ImageLightbox src={preview} onClose={() => setPreview(null)} />

      {/* Reject + feedback dialog — the comment becomes avoid-context for the next run */}
      <Dialog open={!!rejectId} onOpenChange={(o) => !o && setRejectId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject this image</DialogTitle>
            <DialogDescription>
              Tell the AI what&apos;s wrong — it remembers this and avoids the same mistakes in
              the next generation.
            </DialogDescription>
          </DialogHeader>
          <Textarea
            placeholder="e.g. label unreadable, skin looks plastic, wrong background…"
            value={rejectComment}
            onChange={(e) => setRejectComment(e.target.value)}
            className="min-h-[90px]"
            autoFocus
          />
          <DialogFooter>
            <Button variant="ghost" onClick={() => setRejectId(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={submitReject} disabled={review.isPending}>
              {review.isPending ? <Spinner /> : <ThumbsDown className="h-4 w-4" />} Reject image
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

/* -------------------------------------------------------------- Market Angles */
function IdeasTab({
  productId,
  onOpenIdea,
  onOpenImageIdea,
}: {
  productId: string;
  onOpenIdea: (id: string) => void;
  onOpenImageIdea: (id: string) => void;
}) {
  const { data: ideas, isLoading } = useIdeas(productId);
  const { data: videos } = useVideos(productId);
  const { data: images } = useImages(productId);
  const generate = useGenerateIdeas(productId);
  const select = useSelectIdea(productId);
  const [prompt, setPrompt] = React.useState("");

  // "Done" = an asset was actually CREATED from this idea (a rendered video, or a
  // generated image) — NOT merely that the idea was opened/selected.
  const doneVideoIdeaIds = React.useMemo(
    () => new Set((videos ?? []).filter((v) => v.idea_id && v.video_url).map((v) => v.idea_id as string)),
    [videos]
  );
  const doneImageIdeaIds = React.useMemo(
    () =>
      new Set(
        (images ?? [])
          .map((i) => (i.meta as { idea_id?: string | null })?.idea_id)
          .filter((x): x is string => !!x)
      ),
    [images]
  );
  const isDone = (idea: Idea) =>
    idea.kind === "image" ? doneImageIdeaIds.has(idea.id) : doneVideoIdeaIds.has(idea.id);

  function run() {
    if (!prompt.trim()) return;
    generate.mutate({ prompt: prompt.trim(), count: 6 });
  }
  function openVideo(id: string) {
    // Selecting carries the idea into the Video tab; it does NOT mark it done.
    select.mutate(id, { onSuccess: () => onOpenIdea(id) });
  }

  const byRank = (a: Idea, b: Idea) => {
    const rank = (s: IdeaStatus) => (s === "selected" ? 0 : s === "pending" ? 1 : 2);
    return rank(a.status) - rank(b.status);
  };
  const imageIdeas = (ideas ?? []).filter((i) => i.kind === "image").sort(byRank);
  const videoIdeas = (ideas ?? []).filter((i) => i.kind !== "image").sort(byRank);
  const total = imageIdeas.length + videoIdeas.length;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Describe your campaign</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="e.g. summer launch for Meta ads — fresh, young, beach-day energy…"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="min-h-[100px]"
          />
          <Button variant="aurora" onClick={run} disabled={generate.isPending || !prompt.trim()}>
            {generate.isPending ? <Spinner /> : <Lightbulb className="h-4 w-4" />}
            {generate.isPending ? "Thinking…" : "Generate market angles"}
          </Button>
          <p className="text-xs text-muted-foreground">
            Generates Meta-ad angles: image concepts (open in Images) and video concepts (open in
            Video). All angles stay saved.
          </p>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-44" />
          ))}
        </div>
      ) : total === 0 ? (
        <EmptyState icon={Lightbulb} title="No angles yet" description="Describe your campaign above — you'll get image and video ad concepts to run with." />
      ) : (
        <div className="space-y-8">
          {imageIdeas.length > 0 && (
            <div>
              <h3 className="mb-3 flex items-center gap-2 font-display text-lg font-semibold">
                <ImageIcon className="h-5 w-5 text-accent" /> Image ideas
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                {imageIdeas.map((idea) => (
                  <FadeUp key={idea.id}>
                    <IdeaCard idea={idea} busy={false} done={isDone(idea)} onOpen={() => onOpenImageIdea(idea.id)} />
                  </FadeUp>
                ))}
              </div>
            </div>
          )}
          {videoIdeas.length > 0 && (
            <div>
              <h3 className="mb-3 flex items-center gap-2 font-display text-lg font-semibold">
                <Film className="h-5 w-5 text-primary" /> Video ideas
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                {videoIdeas.map((idea) => (
                  <FadeUp key={idea.id}>
                    <IdeaCard idea={idea} busy={select.isPending} done={isDone(idea)} onOpen={() => openVideo(idea.id)} />
                  </FadeUp>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function IdeaCard({ idea, onOpen, busy, done }: { idea: Idea; onOpen: () => void; busy: boolean; done: boolean }) {
  const isImage = idea.kind === "image";
  return (
    <Card className={"group h-full transition-all hover-lift " + (done ? "ring-2 ring-primary/60" : "")}>
      <button type="button" onClick={onOpen} disabled={busy} className="block w-full text-left">
        <CardContent className="flex h-full flex-col gap-3 p-5">
          <div className="flex items-start justify-between gap-2">
            <p className="font-display text-base font-semibold">{idea.title ?? "Untitled idea"}</p>
            <Badge variant={done ? "success" : isImage ? "accent" : "outline"} className="shrink-0 gap-1">
              {done && <Check className="h-3 w-3" />}
              {done ? "Done" : isImage ? "Image" : "Video"}
            </Badge>
          </div>
          {idea.angle && <p className="text-xs font-medium text-accent">{idea.angle}</p>}
          {idea.description && (
            <p className="line-clamp-3 text-sm text-muted-foreground">{idea.description}</p>
          )}
          {idea.hook && (
            <p className="rounded-xl bg-secondary/40 px-3 py-2 text-sm italic">“{idea.hook}”</p>
          )}
          <div className="mt-auto flex items-center gap-1.5 pt-1 text-sm font-medium text-primary">
            {busy ? <Spinner /> : isImage ? <ImageIcon className="h-4 w-4" /> : <Film className="h-4 w-4" />}
            {isImage ? "Create image from this" : done ? "Open video" : "Build video from this"}
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </div>
        </CardContent>
      </button>
    </Card>
  );
}

/* --------------------------------------------------------------------- Video */
const VIDEO_STATUS_VARIANT: Record<string, NonNullable<BadgeProps["variant"]>> = {
  draft: "outline",
  frames_ready: "accent",
  rendering: "accent",
  ready: "success",
  error: "destructive",
};

function VideoTab({ productId, activeIdea }: { productId: string; activeIdea: Idea | null }) {
  const { data: videos, isLoading } = useVideos(productId);
  const createScript = useCreateScript(productId);

  const [duration, setDuration] = React.useState("15s");
  const [format, setFormat] = React.useState("reel");
  const [instructions, setInstructions] = React.useState("");

  // Show only the active idea's videos (or everything when browsing directly).
  const list = React.useMemo(() => {
    const all = videos ?? [];
    return activeIdea ? all.filter((v) => v.idea_id === activeIdea.id) : all;
  }, [videos, activeIdea]);

  function create() {
    createScript.mutate({
      duration,
      format,
      instructions: instructions.trim() || undefined,
      idea_id: activeIdea?.id,
    });
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clapperboard className="h-5 w-5 text-primary" /> New video script
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {activeIdea ? (
            <div className="rounded-xl bg-secondary/40 px-3 py-2 text-sm">
              Building on idea:{" "}
              <span className="font-medium text-foreground">{activeIdea.title}</span>
              <span className="text-muted-foreground"> — switch ideas in the Ideas tab</span>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Pick an idea in the Ideas tab to build on it, or draft a generic script here.
            </p>
          )}
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>Duration</Label>
              <Select value={duration} onValueChange={setDuration}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {["15s", "30s", "60s"].map((d) => (
                    <SelectItem key={d} value={d}>{d}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Format</Label>
              <Select value={format} onValueChange={setFormat}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {["reel", "story", "square", "landscape"].map((f) => (
                    <SelectItem key={f} value={f}>{titleCase(f)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>Direction (optional)</Label>
            <Textarea
              placeholder="e.g. energetic, festive, model walking through a busy market"
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
            />
          </div>
          <Button variant="aurora" onClick={create} disabled={createScript.isPending}>
            {createScript.isPending ? <Spinner /> : <Sparkles className="h-4 w-4" />}
            {createScript.isPending
              ? "Writing script…"
              : activeIdea
                ? "New script for this idea"
                : "Draft script"}
          </Button>
        </CardContent>
      </Card>

      {isLoading || (createScript.isPending && list.length === 0) ? (
        <Skeleton className="h-64" />
      ) : list.length === 0 ? (
        <EmptyState
          icon={Film}
          title="No video yet"
          description={
            activeIdea
              ? `Hit “New script for this idea” above to draft the script for “${activeIdea.title}”, then generate frames and render.`
              : "Draft a script above, then generate frames and render an AI video."
          }
        />
      ) : (
        <div className="space-y-6">
          {list.map((v) => (
            <VideoCard key={v.id} productId={productId} video={v} />
          ))}
        </div>
      )}
    </div>
  );
}

function VideoCard({ productId, video }: { productId: string; video: GeneratedVideo }) {
  const update = useUpdateVideo(productId);
  const reprompt = useRepromptVideo(productId);
  const frames = useGenerateFrames(productId);
  const render = useRenderVideo(productId);
  const remove = useDeleteVideo(productId);

  const [script, setScript] = React.useState(video.script ?? "");
  const [instructions, setInstructions] = React.useState("");
  const [preview, setPreview] = React.useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = React.useState(false);
  const dirty = script !== (video.script ?? "");

  const meta = (video.meta ?? {}) as { model_label?: string; is_variant?: boolean };
  const modelLabel = meta.model_label ?? "Custom Model";
  const isVariant = !!meta.is_variant;

  React.useEffect(() => {
    setScript(video.script ?? "");
  }, [video.script]);

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2 text-base">
          {titleCase(video.format)} · {titleCase(video.duration)}
          <Badge variant="default" className="gap-1">
            <Film className="h-3 w-3" /> {modelLabel}
          </Badge>
        </CardTitle>
        <div className="flex items-center gap-2">
          <Badge variant={VIDEO_STATUS_VARIANT[video.status] ?? "outline"}>
            {titleCase(video.status.replace("_", " "))}
          </Badge>
          {confirmDelete ? (
            <div className="flex items-center gap-1">
              <Button
                size="sm"
                variant="destructive"
                onClick={() => remove.mutate(video.id)}
                disabled={remove.isPending}
              >
                {remove.isPending ? <Spinner /> : "Delete"}
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setConfirmDelete(false)}>
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8 text-muted-foreground hover:text-destructive"
              onClick={() => setConfirmDelete(true)}
              aria-label="Delete this reel"
              title="Delete this reel"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Rendered video / thumbnail */}
        {video.video_url ? (
          <video
            src={video.video_url}
            poster={video.thumbnail_url ?? undefined}
            controls
            className="w-full max-w-sm rounded-2xl ring-1 ring-white/10"
          />
        ) : video.thumbnail_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={video.thumbnail_url}
            alt="thumbnail"
            className="w-full max-w-sm rounded-2xl ring-1 ring-white/10"
          />
        ) : null}

        {video.status === "rendering" && (
          <div className="space-y-2">
            <Progress value={video.progress || 40} />
            <p className="text-xs text-muted-foreground">
              Rendering with {modelLabel}… this takes a few minutes and updates here automatically.
            </p>
          </div>
        )}
        {isVariant && video.status === "error" && (
          <p className="rounded-xl bg-destructive/10 px-3 py-2 text-xs text-destructive">
            {(video.meta as { render_error?: string })?.render_error ?? "This model couldn't render."}
          </p>
        )}

        {!isVariant && (
        <>
        {/* Script editor */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label>Script</Label>
            <CopyButton value={script} label="Copy" variant="ghost" size="sm" />
          </div>
          <Textarea
            value={script}
            onChange={(e) => setScript(e.target.value)}
            className="min-h-[140px] font-mono text-xs leading-relaxed"
          />
          {dirty && (
            <Button
              size="sm"
              variant="glass"
              onClick={() => update.mutate({ id: video.id, body: { script } })}
              disabled={update.isPending}
            >
              {update.isPending ? <Spinner /> : <Check className="h-4 w-4" />} Save edits
            </Button>
          )}
        </div>

        {video.voiceover && (
          <div className="space-y-1.5">
            <Label>Voiceover (Hinglish)</Label>
            <p className="rounded-xl bg-secondary/40 px-3 py-2 text-sm text-muted-foreground">
              {video.voiceover}
            </p>
          </div>
        )}

        {/* Reprompt */}
        <div className="space-y-1.5">
          <Label>Reprompt / refine</Label>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Input
              placeholder="e.g. punchier hook, mention the festive discount"
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
            />
            <Button
              variant="glass"
              onClick={() => {
                if (!instructions.trim()) return;
                reprompt.mutate(
                  { id: video.id, instructions: instructions.trim() },
                  { onSuccess: () => setInstructions("") }
                );
              }}
              disabled={reprompt.isPending || !instructions.trim()}
            >
              {reprompt.isPending ? <Spinner /> : <RefreshCw className="h-4 w-4" />} Regenerate
            </Button>
          </div>
        </div>

        {/* Frames */}
        {video.frame_urls.length > 0 && (
          <div className="space-y-2">
            <Label>Frames</Label>
            <div className="grid grid-cols-3 gap-3 sm:grid-cols-5">
              {video.frame_urls.map((f, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setPreview(f)}
                  className="block overflow-hidden rounded-xl ring-1 ring-white/10 transition hover:ring-white/30"
                  aria-label={`Preview frame ${i + 1}`}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={f}
                    alt={`frame ${i + 1}`}
                    className="aspect-[9/16] w-full cursor-zoom-in object-cover"
                  />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Stage actions */}
        {(() => {
          const rendering = video.status === "rendering";
          return (
            <>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="glass"
                  onClick={() => frames.mutate(video.id)}
                  disabled={frames.isPending || render.isPending || rendering}
                >
                  {frames.isPending ? <Spinner /> : <ImageIcon className="h-4 w-4" />}
                  {video.frame_urls.length > 0 ? "Regenerate frames" : "Generate frames"}
                </Button>
                <Button
                  variant="aurora"
                  onClick={() => render.mutate(video.id)}
                  disabled={
                    render.isPending || frames.isPending || rendering || video.frame_urls.length === 0
                  }
                >
                  {render.isPending || rendering ? <Spinner /> : <Play className="h-4 w-4" />}
                  {rendering ? "Rendering…" : render.isPending ? "Starting…" : "Render video"}
                </Button>
              </div>
              {rendering && (
                <p className="text-xs text-muted-foreground">
                  Rendering your multi-shot video — this takes a few minutes and updates here
                  automatically. You can leave this page.
                </p>
              )}
              {!rendering && video.frame_urls.length === 0 && (
                <p className="text-xs text-muted-foreground">Generate frames before rendering.</p>
              )}
              {!rendering && video.frame_urls.length > 0 && (
                <p className="text-xs text-muted-foreground">
                  Every generated frame becomes a shot in the final reel, in order.
                </p>
              )}
            </>
          );
        })()}
        </>
        )}
        <ImageLightbox src={preview} onClose={() => setPreview(null)} />
      </CardContent>
    </Card>
  );
}

/* ---------------------------------------------------------------------- Copy */
const PLATFORMS = ["instagram", "facebook", "google", "linkedin", "twitter", "email", "landing_page"];
const TONES = ["luxury", "professional", "friendly", "minimal"];

function CopyTab({ productId }: { productId: string }) {
  const { data: copies, isLoading } = useCopy(productId);
  const generate = useGenerateCopy(productId);
  const [platform, setPlatform] = React.useState("instagram");
  const [tone, setTone] = React.useState("friendly");
  const [variations, setVariations] = React.useState("3");

  function run() {
    generate.mutate({ platform, tone, variations: Number(variations) });
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Card className="h-fit lg:col-span-1">
        <CardHeader><CardTitle>Generate copy</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label>Platform</Label>
            <Select value={platform} onValueChange={setPlatform}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {PLATFORMS.map((p) => (
                  <SelectItem key={p} value={p}>{titleCase(p)}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Tone</Label>
              <Select value={tone} onValueChange={setTone}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {TONES.map((t) => (
                    <SelectItem key={t} value={t}>{titleCase(t)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Variations</Label>
              <Select value={variations} onValueChange={setVariations}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <SelectItem key={n} value={String(n)}>{n}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button variant="aurora" className="w-full" onClick={run} disabled={generate.isPending}>
            {generate.isPending ? <Spinner /> : <FileText className="h-4 w-4" />}
            {generate.isPending ? "Writing…" : "Generate copy"}
          </Button>
        </CardContent>
      </Card>

      <div className="space-y-4 lg:col-span-2">
        {isLoading ? (
          <Skeleton className="h-40" />
        ) : !copies || copies.length === 0 ? (
          <EmptyState icon={FileText} title="No copy yet" description="Pick a platform and tone, then generate ad copy variations." />
        ) : (
          <div className="space-y-4">
            {copies.flatMap((c) =>
              (c.variations.length ? c.variations : [{ headline: c.headline ?? "", body: c.body ?? "", cta: c.cta ?? "" }]).map(
                (v, i) => (
                  <FadeUp key={`${c.id}-${i}`}>
                    <Card>
                      <CardContent className="space-y-2 p-5">
                        <div className="flex items-center justify-between gap-2">
                          <Badge variant="secondary" className="capitalize">
                            {titleCase(c.platform)} · {titleCase(c.tone)}
                          </Badge>
                          <CopyButton
                            value={`${v.headline}\n\n${v.body}\n\n${v.cta}`}
                            label="Copy"
                            variant="ghost"
                            size="sm"
                          />
                        </div>
                        {v.headline && <p className="font-display text-base font-semibold">{v.headline}</p>}
                        {v.body && <p className="whitespace-pre-wrap text-sm text-muted-foreground">{v.body}</p>}
                        {v.cta && <p className="text-sm font-medium text-primary">{v.cta}</p>}
                      </CardContent>
                    </Card>
                  </FadeUp>
                )
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
}
