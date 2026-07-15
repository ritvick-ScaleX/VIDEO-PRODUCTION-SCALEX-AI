"use client";

import {
  Download,
  FileArchive,
  FileText,
  FileType,
  Image as ImageIcon,
  Video,
} from "lucide-react";
import * as React from "react";
import { FadeItem, StaggerGroup } from "@/components/animations/motion";
import { NoBrand } from "@/components/shared/no-brand";
import { PageHeader } from "@/components/shared/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useActiveBrand, useCreateExport, useExports, useProducts } from "@/lib/hooks";
import type { ExportItem } from "@/lib/types";
import { timeAgo } from "@/lib/utils";

type Kind = "pdf" | "png" | "jpg" | "zip" | "mp4";

const KINDS: { kind: Kind; label: string; icon: typeof FileText; desc: string }[] = [
  { kind: "pdf", label: "PDF Summary", icon: FileText, desc: "Full product brief" },
  { kind: "png", label: "PNG", icon: ImageIcon, desc: "Top creative image" },
  { kind: "jpg", label: "JPG", icon: FileType, desc: "Compressed image" },
  { kind: "zip", label: "ZIP Package", icon: FileArchive, desc: "Everything bundled" },
  { kind: "mp4", label: "Video Package", icon: Video, desc: "Script + thumbnail" },
];

const KIND_VARIANT: Record<string, "default" | "accent" | "secondary" | "success"> = {
  pdf: "default",
  png: "accent",
  jpg: "accent",
  zip: "success",
  mp4: "secondary",
};

function formatBytes(b: number): string {
  if (!b) return "—";
  if (b < 1024) return `${b} B`;
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ExportsPage() {
  const { activeId, active, isLoading: brandsLoading } = useActiveBrand();
  const { data: products } = useProducts(activeId ?? undefined);
  const { data: exports, isLoading } = useExports();
  const createExport = useCreateExport();
  const [productId, setProductId] = React.useState<string>("");
  const [pending, setPending] = React.useState<Kind | null>(null);

  React.useEffect(() => {
    if (!productId && products?.length) setProductId(products[0].id);
  }, [products, productId]);

  const productName = (id: string | null) =>
    products?.find((p) => p.id === id)?.name ?? "Product";

  function runExport(kind: Kind) {
    if (!productId) return;
    setPending(kind);
    createExport.mutate(
      { product_id: productId, kind, label: `${productName(productId)} · ${kind.toUpperCase()}` },
      { onSettled: () => setPending(null) }
    );
  }

  if (!brandsLoading && !active) {
    return (
      <div>
        <PageHeader icon={Download} title="Export Center" description="Package and download your creatives." />
        <NoBrand feature="export creatives" />
      </div>
    );
  }

  return (
    <div>
      <PageHeader icon={Download} title="Export Center" description="Package and download your creatives." />

      <Card className="mb-8">
        <CardHeader><CardTitle>New export</CardTitle></CardHeader>
        <CardContent className="space-y-5">
          <div className="max-w-sm space-y-1.5">
            <label className="text-sm font-medium text-foreground/90">Product</label>
            <Select value={productId} onValueChange={setProductId}>
              <SelectTrigger><SelectValue placeholder="Select a product" /></SelectTrigger>
              <SelectContent>
                {products?.map((p) => (
                  <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {(!products || products.length === 0) && (
              <p className="text-xs text-muted-foreground">
                No products in this brand yet — add one first.
              </p>
            )}
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {KINDS.map((k) => {
              const Icon = k.icon;
              const busy = pending === k.kind;
              return (
                <button
                  key={k.kind}
                  onClick={() => runExport(k.kind)}
                  disabled={!productId || busy}
                  className="group glass hover-lift rounded-2xl p-4 text-left transition disabled:opacity-60"
                >
                  <div className="mb-3 grid h-10 w-10 place-items-center rounded-xl bg-aurora-line bg-[length:200%_200%] text-white shadow-glow group-hover:animate-gradient-pan">
                    <Icon className="h-5 w-5" />
                  </div>
                  <p className="text-sm font-semibold">{busy ? "Preparing…" : k.label}</p>
                  <p className="text-xs text-muted-foreground">{k.desc}</p>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <h2 className="mb-4 font-display text-lg font-semibold">Export history</h2>
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      ) : !exports || exports.length === 0 ? (
        <EmptyState icon={Download} title="No exports yet" description="Create an export above to download your product assets." />
      ) : (
        <StaggerGroup className="space-y-3">
          {exports.map((e: ExportItem) => (
            <FadeItem key={e.id}>
              <div className="flex items-center gap-4 rounded-2xl glass p-4">
                <Badge variant={KIND_VARIANT[e.kind] ?? "secondary"} className="uppercase">
                  {e.kind}
                </Badge>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{e.label}</p>
                  <p className="text-xs text-muted-foreground">
                    {productName(e.product_id)} · {formatBytes(e.size_bytes)} · {timeAgo(e.created_at)}
                  </p>
                </div>
                <Button asChild variant="glass" size="sm">
                  <a href={e.url} target="_blank" rel="noopener noreferrer" download>
                    <Download className="h-4 w-4" /> Download
                  </a>
                </Button>
              </div>
            </FadeItem>
          ))}
        </StaggerGroup>
      )}
    </div>
  );
}
