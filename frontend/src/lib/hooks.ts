"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as React from "react";
import { toast } from "sonner";
import { api } from "./api";
import type { Brand, GeneratedImage, Product } from "./types";

export const qk = {
  brands: ["brands"] as const,
  brand: (id: string) => ["brand", id] as const,
  products: (brandId: string) => ["products", brandId] as const,
  product: (id: string) => ["product", id] as const,
  ideas: (id: string) => ["ideas", id] as const,
  copy: (id: string) => ["copy", id] as const,
  images: (id: string) => ["images", id] as const,
  videos: (id: string) => ["videos", id] as const,
  ugc: (id: string) => ["ugc", id] as const,
  scores: (id: string) => ["scores", id] as const,
  exports: (id?: string) => ["exports", id ?? "all"] as const,
  analytics: (days: number) => ["analytics", days] as const,
  settings: ["settings"] as const,
  system: ["system"] as const,
};

// --------------------------------------------------------------------------- //
// Brands + active brand
// --------------------------------------------------------------------------- //
export const useBrands = () => useQuery({ queryKey: qk.brands, queryFn: api.brands.list });
export const useBrand = (id?: string) =>
  useQuery({ queryKey: qk.brand(id!), queryFn: () => api.brands.get(id!), enabled: !!id });

export function useCreateBrand() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<Brand> & { name: string }) => api.brands.create(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.brands });
      toast.success("Brand created");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useScrapeBrand() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (url: string) => api.brands.scrape(url),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.brands });
      toast.success("Brand added");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useUpdateBrand(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<Brand>) => api.brands.update(id, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.brands });
      qc.invalidateQueries({ queryKey: qk.brand(id) });
      toast.success("Brand saved");
    },
  });
}
export function useDeleteBrand() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.brands.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.brands });
      toast.success("Brand deleted");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

// --------------------------------------------------------------------------- //
// Shared active-brand store — a single source of truth across every component
// (top-bar selector, products page, dashboard) so switching brands updates all
// of them at once. Backed by an external store + localStorage for persistence.
// --------------------------------------------------------------------------- //
const ACTIVE_BRAND_KEY = "scalex:activeBrandId";
let _activeBrandId: string | null = null;
let _hydrated = false;
const _brandListeners = new Set<() => void>();

function _emitBrand() {
  for (const l of _brandListeners) l();
}
function _setActiveBrandId(id: string | null) {
  if (id === _activeBrandId) return;
  _activeBrandId = id;
  if (typeof window !== "undefined" && id) localStorage.setItem(ACTIVE_BRAND_KEY, id);
  _emitBrand();
}
function _subscribeBrand(cb: () => void) {
  _brandListeners.add(cb);
  return () => {
    _brandListeners.delete(cb);
  };
}
function _brandSnapshot() {
  return _activeBrandId;
}
function _brandServerSnapshot(): string | null {
  return null;
}

export function useActiveBrand() {
  const { data: brands, isLoading } = useBrands();
  const activeId = React.useSyncExternalStore(_subscribeBrand, _brandSnapshot, _brandServerSnapshot);

  // Hydrate the store from localStorage once on the client.
  React.useEffect(() => {
    if (_hydrated || typeof window === "undefined") return;
    _hydrated = true;
    const stored = localStorage.getItem(ACTIVE_BRAND_KEY);
    if (stored && !_activeBrandId) _setActiveBrandId(stored);
  }, []);

  // Fall back to the first brand if nothing is selected or the selection vanished.
  React.useEffect(() => {
    if (brands && brands.length && (!activeId || !brands.some((b) => b.id === activeId))) {
      _setActiveBrandId(brands[0].id);
    }
  }, [brands, activeId]);

  const setActiveId = React.useCallback((id: string) => _setActiveBrandId(id), []);

  const active = brands?.find((b) => b.id === activeId) ?? brands?.[0] ?? null;
  return { activeId: active?.id ?? null, active, brands: brands ?? [], setActiveId, isLoading };
}

// --------------------------------------------------------------------------- //
// Products
// --------------------------------------------------------------------------- //
export const useProducts = (brandId?: string) =>
  useQuery({ queryKey: qk.products(brandId!), queryFn: () => api.brands.products(brandId!), enabled: !!brandId });
export const useProduct = (id?: string) =>
  useQuery({ queryKey: qk.product(id!), queryFn: () => api.products.get(id!), enabled: !!id });

export function useCreateProduct(brandId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { name: string; source_type: "url" | "manual"; source_url?: string | null } & Record<string, unknown>) =>
      api.brands.createProduct(brandId, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.products(brandId) });
      qc.invalidateQueries({ queryKey: qk.brands });
      toast.success("Product added");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useUpdateProduct(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<Product>) => api.products.update(id, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.product(id) });
      toast.success("Saved");
    },
  });
}
export function useDeleteProduct(brandId?: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.products.remove(id),
    onSuccess: () => {
      if (brandId) qc.invalidateQueries({ queryKey: qk.products(brandId) });
      qc.invalidateQueries({ queryKey: ["products"] });
      toast.success("Product deleted");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useAnalyze(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.products.analyze(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.product(id) });
      toast.success("Analysis complete");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useRescrape(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.products.rescrape(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.product(id) });
      toast.success("Data refreshed");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

// --------------------------------------------------------------------------- //
// Ideas
// --------------------------------------------------------------------------- //
export const useIdeas = (pid?: string) =>
  useQuery({ queryKey: qk.ideas(pid!), queryFn: () => api.ideas.list(pid!), enabled: !!pid });
export function useGenerateIdeas(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { prompt: string; count?: number }) => api.ideas.generate(pid, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.ideas(pid) });
      toast.success("Ideas generated");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useSelectIdea(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.ideas.select(pid, id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.ideas(pid) });
      toast.success("Idea selected");
    },
  });
}

// --------------------------------------------------------------------------- //
// Copy / Images / Videos / UGC / Scores
// --------------------------------------------------------------------------- //
export const useCopy = (pid?: string) =>
  useQuery({ queryKey: qk.copy(pid!), queryFn: () => api.copy.list(pid!), enabled: !!pid });
export const useImages = (pid?: string) =>
  useQuery({ queryKey: qk.images(pid!), queryFn: () => api.images.list(pid!), enabled: !!pid });
export const useVideos = (pid?: string) =>
  useQuery({
    queryKey: qk.videos(pid!),
    queryFn: () => api.videos.list(pid!),
    enabled: !!pid,
    // While any video is rendering (background job on the server), poll for completion.
    refetchInterval: (query) =>
      (query.state.data ?? []).some((v) => v.status === "rendering") ? 5000 : false,
  });
export const useUGC = (pid?: string) =>
  useQuery({ queryKey: qk.ugc(pid!), queryFn: () => api.ugc.list(pid!), enabled: !!pid });
export const useScores = (pid?: string) =>
  useQuery({ queryKey: qk.scores(pid!), queryFn: () => api.scoring.list(pid!), enabled: !!pid });

export function useGenerateCopy(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { platform: string; tone: string; variations?: number; instructions?: string }) =>
      api.copy.generate(pid, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.copy(pid) });
      toast.success("Copy generated");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useGenerateImages(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { category: string; format: string; count?: number; prompt?: string; idea_id?: string | null; headline?: string; cta?: string }) =>
      api.images.generate(pid, body),
    onSuccess: (created) => {
      // Prepend the new images to the catalog immediately, then refetch to reconcile.
      qc.setQueryData<GeneratedImage[]>(qk.images(pid), (old) => [
        ...(created ?? []),
        ...(old ?? []),
      ]);
      qc.invalidateQueries({ queryKey: qk.images(pid) });
      toast.success(`${created?.length ?? 0} image${(created?.length ?? 0) === 1 ? "" : "s"} added to catalog`);
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useReviewImage(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status, comment }: { id: string; status: string; comment?: string | null }) =>
      api.images.review(pid, id, { status, comment }),
    onSuccess: (img) => {
      qc.setQueryData<GeneratedImage[]>(qk.images(pid), (old) =>
        (old ?? []).map((i) => (i.id === img.id ? img : i))
      );
      toast.success(
        img.review_status === "accepted"
          ? "Image accepted"
          : img.review_status === "rejected"
            ? "Image rejected — feedback saved for the next run"
            : "Review cleared"
      );
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useCreateScript(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { duration: string; format: string; instructions?: string; idea_id?: string }) =>
      api.videos.createScript(pid, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.videos(pid) });
      toast.success("Script drafted — review it");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useUpdateVideo(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: { script?: string; voiceover?: string; status?: string } }) =>
      api.videos.update(pid, id, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: qk.videos(pid) }),
  });
}
export function useRepromptVideo(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, instructions }: { id: string; instructions: string }) =>
      api.videos.reprompt(pid, id, instructions),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.videos(pid) });
      toast.success("Script regenerated");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useGenerateFrames(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.videos.frames(pid, id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.videos(pid) });
      toast.success("Frames generated");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useRenderVideo(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.videos.render(pid, id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.videos(pid) });
      toast.success("Rendering started — this takes a few minutes. It'll appear here automatically.");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useGenerateUGC(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { voice_style: string; emotion: string; audience?: string; instructions?: string }) =>
      api.ugc.generate(pid, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.ugc(pid) });
      toast.success("UGC generated");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export function useScore(pid: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { target_type: string; target_id?: string; text?: string }) =>
      api.scoring.score(pid, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.scores(pid) });
      toast.success("Scored");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}

// --------------------------------------------------------------------------- //
// Exports / analytics / settings
// --------------------------------------------------------------------------- //
export const useExports = (productId?: string) =>
  useQuery({ queryKey: qk.exports(productId), queryFn: () => api.exports.list(productId) });
export function useCreateExport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.exports.create,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["exports"] });
      toast.success("Export ready");
    },
    onError: (e: Error) => toast.error(e.message),
  });
}
export const useAnalytics = (days = 14) =>
  useQuery({ queryKey: qk.analytics(days), queryFn: () => api.analytics.summary(days) });
export const useSettings = () => useQuery({ queryKey: qk.settings, queryFn: api.settings.get });
export const useSystemInfo = () => useQuery({ queryKey: qk.system, queryFn: api.settings.system });
export function useUpdateSettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.settings.update,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.settings });
      toast.success("Settings saved");
    },
  });
}
