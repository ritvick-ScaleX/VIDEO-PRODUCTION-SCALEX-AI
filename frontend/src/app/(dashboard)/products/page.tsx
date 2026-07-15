"use client";

import { ArrowUpRight, Globe, Package, PenLine, Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";
import { FadeItem, StaggerGroup } from "@/components/animations/motion";
import { NoBrand } from "@/components/shared/no-brand";
import { PageHeader } from "@/components/shared/page-header";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { useActiveBrand, useCreateProduct, useProducts } from "@/lib/hooks";
import type { ProductStatus } from "@/lib/types";
import { initials, statusLabel, timeAgo, titleCase } from "@/lib/utils";

const STATUS_VARIANT: Record<ProductStatus, NonNullable<BadgeProps["variant"]>> = {
  ready: "success",
  error: "destructive",
  draft: "outline",
  scraping: "accent",
  analyzing: "accent",
};

export default function ProductsPage() {
  const { activeId, active, isLoading: brandsLoading } = useActiveBrand();
  const { data: products, isLoading } = useProducts(activeId ?? undefined);

  if (!brandsLoading && !active) {
    return (
      <div>
        <PageHeader icon={Package} title="Products" description="List products under a brand." />
        <NoBrand feature="add products" />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        icon={Package}
        title="Products"
        description={active ? `Products in ${active.name}` : "Products"}
        actions={activeId ? <CreateProductDialog brandId={activeId} /> : undefined}
      />

      {isLoading || brandsLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-44" />
          ))}
        </div>
      ) : !products || products.length === 0 ? (
        <EmptyState
          icon={Package}
          title="No products yet"
          description="Add a product by pasting its URL (we auto-fill it) or enter details manually."
          action={activeId ? <CreateProductDialog brandId={activeId} /> : undefined}
        />
      ) : (
        <StaggerGroup className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((p) => (
            <FadeItem key={p.id}>
              <a href={`/products/${p.id}`} className="block">
                <Card className="group h-full hover-lift">
                  <CardContent className="flex flex-col gap-4 p-5">
                    <div className="flex items-start gap-3">
                      <Avatar className="h-14 w-14 rounded-2xl">
                        {p.thumbnail_url && (
                          <AvatarImage src={p.thumbnail_url} alt={p.name} className="rounded-2xl object-cover" />
                        )}
                        <AvatarFallback className="rounded-2xl text-sm">
                          {initials(p.name || "New")}
                        </AvatarFallback>
                      </Avatar>
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-display text-base font-semibold">{p.name}</p>
                        <p className="mt-0.5 flex items-center gap-1 text-xs text-muted-foreground">
                          {p.source_type === "url" ? (
                            <Globe className="h-3 w-3" />
                          ) : (
                            <PenLine className="h-3 w-3" />
                          )}
                          {timeAgo(p.created_at)}
                        </p>
                      </div>
                      <ArrowUpRight className="h-5 w-5 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                    </div>
                    {p.description && (
                      <p className="line-clamp-2 text-sm text-muted-foreground">{p.description}</p>
                    )}
                    <div className="mt-auto flex items-center justify-between">
                      <Badge variant={STATUS_VARIANT[p.status] ?? "outline"}>
                        {statusLabel(p.status)}
                      </Badge>
                      {p.price && <span className="text-sm font-medium">{p.price}</span>}
                    </div>
                  </CardContent>
                </Card>
              </a>
            </FadeItem>
          ))}
        </StaggerGroup>
      )}
    </div>
  );
}

function CreateProductDialog({ brandId }: { brandId: string }) {
  const create = useCreateProduct(brandId);
  const router = useRouter();
  const [open, setOpen] = React.useState(false);

  // URL mode
  const [url, setUrl] = React.useState("");
  // Manual mode
  const [name, setName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [price, setPrice] = React.useState("");
  const [features, setFeatures] = React.useState("");

  function submitUrl() {
    if (!url.trim()) return;
    const guessName = (() => {
      try {
        const u = new URL(url.trim());
        const seg = u.pathname.split("/").filter(Boolean).pop() ?? u.hostname;
        return titleCase(decodeURIComponent(seg).replace(/[-_]+/g, " ")).slice(0, 60) || u.hostname;
      } catch {
        return "New product";
      }
    })();
    create.mutate(
      { name: guessName, source_type: "url", source_url: url.trim() },
      {
        onSuccess: (p) => {
          setOpen(false);
          setUrl("");
          router.push(`/products/${p.id}`);
        },
      }
    );
  }

  function submitManual() {
    if (!name.trim()) return;
    create.mutate(
      {
        name: name.trim(),
        source_type: "manual",
        description: description.trim() || null,
        price: price.trim() || null,
        features: features
          .split("\n")
          .map((f) => f.trim())
          .filter(Boolean),
      },
      {
        onSuccess: (p) => {
          setOpen(false);
          setName("");
          setDescription("");
          setPrice("");
          setFeatures("");
          router.push(`/products/${p.id}`);
        },
      }
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="aurora">
          <Plus className="h-4 w-4" /> New Product
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add a product</DialogTitle>
          <DialogDescription>
            Paste a product URL to import it automatically, or enter details by hand.
          </DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="url">
          <TabsList className="w-full">
            <TabsTrigger value="url" className="flex-1">
              <Globe className="h-4 w-4" /> From URL
            </TabsTrigger>
            <TabsTrigger value="manual" className="flex-1">
              <PenLine className="h-4 w-4" /> Manual
            </TabsTrigger>
          </TabsList>

          <TabsContent value="url" className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="p-url">Product URL</Label>
              <Input
                id="p-url"
                placeholder="https://store.com/product/…"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                autoFocus
              />
              <p className="text-xs text-muted-foreground">
                We&apos;ll pull in the title, images, price, and description automatically.
              </p>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button variant="aurora" onClick={submitUrl} disabled={!url.trim() || create.isPending}>
                {create.isPending ? "Importing…" : "Add product"}
              </Button>
            </DialogFooter>
          </TabsContent>

          <TabsContent value="manual" className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="p-name">Product name</Label>
              <Input
                id="p-name"
                placeholder="e.g. Beige Linen Shirt"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="p-desc">Description</Label>
              <Textarea
                id="p-desc"
                placeholder="What is it and who is it for?"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label htmlFor="p-price">Price</Label>
                <Input
                  id="p-price"
                  placeholder="₹1,499"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="p-feat">Features (one per line)</Label>
                <Textarea
                  id="p-feat"
                  placeholder={"100% linen\nBreathable weave"}
                  value={features}
                  onChange={(e) => setFeatures(e.target.value)}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button
                variant="aurora"
                onClick={submitManual}
                disabled={!name.trim() || create.isPending}
              >
                {create.isPending ? "Adding…" : "Add product"}
              </Button>
            </DialogFooter>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
