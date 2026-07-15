"use client";

import { ArrowUpRight, Boxes, Globe, PenLine, Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";
import { FadeItem, StaggerGroup } from "@/components/animations/motion";
import { BrandAvatar } from "@/components/shared/brand-avatar";
import { PageHeader } from "@/components/shared/page-header";
import { Badge } from "@/components/ui/badge";
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
import { useActiveBrand, useBrands, useCreateBrand, useScrapeBrand } from "@/lib/hooks";

export default function BrandsPage() {
  const { data: brands, isLoading } = useBrands();
  const { setActiveId } = useActiveBrand();
  const router = useRouter();

  function openBrand(id: string) {
    setActiveId(id);
    router.push("/products");
  }

  return (
    <div>
      <PageHeader
        icon={Boxes}
        title="Brands"
        description="Each brand holds its products, voice, and creative memory."
        actions={<CreateBrandDialog onCreated={openBrand} />}
      />

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-40" />
          ))}
        </div>
      ) : !brands || brands.length === 0 ? (
        <EmptyState
          icon={Boxes}
          title="No brands yet"
          description="Create your first brand to start listing products and generating creative."
          action={<CreateBrandDialog onCreated={openBrand} />}
        />
      ) : (
        <StaggerGroup className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {brands.map((b) => (
            <FadeItem key={b.id}>
              <button onClick={() => openBrand(b.id)} className="w-full text-left">
                <Card className="group h-full hover-lift">
                  <CardContent className="flex flex-col gap-4 p-5">
                    <div className="flex items-start justify-between gap-3">
                      <BrandAvatar
                        name={b.name}
                        logoUrl={b.logo_url}
                        className="h-12 w-12 rounded-2xl shadow-glow"
                        textClass="text-sm"
                      />
                      <ArrowUpRight className="h-5 w-5 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                    </div>
                    <div>
                      <p className="font-display text-lg font-semibold">{b.name}</p>
                      {b.tagline && (
                        <p className="mt-0.5 line-clamp-1 text-sm text-muted-foreground">
                          {b.tagline}
                        </p>
                      )}
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="secondary">
                        {b.product_count} product{b.product_count === 1 ? "" : "s"}
                      </Badge>
                      {(b.brand_colors ?? []).slice(0, 4).map((c) => (
                        <span
                          key={c}
                          className="h-4 w-4 rounded-full ring-1 ring-white/20"
                          style={{ background: c }}
                        />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </button>
            </FadeItem>
          ))}
        </StaggerGroup>
      )}
    </div>
  );
}

function CreateBrandDialog({ onCreated }: { onCreated: (id: string) => void }) {
  const create = useCreateBrand();
  const scrape = useScrapeBrand();
  const [open, setOpen] = React.useState(false);

  // URL mode
  const [url, setUrl] = React.useState("");
  // Manual mode
  const [name, setName] = React.useState("");
  const [website, setWebsite] = React.useState("");
  const [tagline, setTagline] = React.useState("");
  const [voice, setVoice] = React.useState("");
  const [audience, setAudience] = React.useState("");
  const [colors, setColors] = React.useState("");

  function done(id: string) {
    setOpen(false);
    setUrl("");
    setName("");
    setWebsite("");
    setTagline("");
    setVoice("");
    setAudience("");
    setColors("");
    onCreated(id);
  }

  function submitUrl() {
    if (!url.trim()) return;
    scrape.mutate(url.trim(), { onSuccess: (b) => done(b.id) });
  }

  function submitManual() {
    if (!name.trim()) return;
    create.mutate(
      {
        name: name.trim(),
        website: website.trim() || null,
        tagline: tagline.trim() || null,
        brand_voice: voice.trim() || null,
        target_audience: audience.trim() || null,
        brand_colors: colors
          .split(",")
          .map((c) => c.trim())
          .filter(Boolean),
      },
      { onSuccess: (b) => done(b.id) }
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="aurora">
          <Plus className="h-4 w-4" /> New Brand
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create a brand</DialogTitle>
          <DialogDescription>
            Paste the brand&apos;s website to auto-fill it, or enter the identity by hand.
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
              <Label htmlFor="b-url">Brand website</Label>
              <Input
                id="b-url"
                placeholder="https://yourbrand.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                autoFocus
              />
              <p className="text-xs text-muted-foreground">
                We pull in the name, logo, colours and tagline, then infer the brand voice.
              </p>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button variant="aurora" onClick={submitUrl} disabled={!url.trim() || scrape.isPending}>
                {scrape.isPending ? "Importing…" : "Auto-fill & add"}
              </Button>
            </DialogFooter>
          </TabsContent>

          <TabsContent value="manual" className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="b-name">Brand name</Label>
              <Input
                id="b-name"
                placeholder="e.g. Aura Athletics"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label htmlFor="b-web">Website</Label>
                <Input
                  id="b-web"
                  placeholder="https://…"
                  value={website}
                  onChange={(e) => setWebsite(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="b-tag">Tagline</Label>
                <Input
                  id="b-tag"
                  placeholder="Move with intent"
                  value={tagline}
                  onChange={(e) => setTagline(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="b-voice">Brand voice</Label>
              <Textarea
                id="b-voice"
                placeholder="Warm, confident, a little playful…"
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1.5">
                <Label htmlFor="b-aud">Target audience</Label>
                <Input
                  id="b-aud"
                  placeholder="Urban runners, 22–35"
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="b-col">Brand colors</Label>
                <Input
                  id="b-col"
                  placeholder="#111, #FA5400"
                  value={colors}
                  onChange={(e) => setColors(e.target.value)}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button variant="aurora" onClick={submitManual} disabled={!name.trim() || create.isPending}>
                {create.isPending ? "Creating…" : "Create brand"}
              </Button>
            </DialogFooter>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
