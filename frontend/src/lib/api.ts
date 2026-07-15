// Typed API client — Brand → Product → creative generators.
import type {
  AnalyticsSummary,
  AppSettings,
  Brand,
  CreativeScore,
  ExportItem,
  GeneratedCopy,
  GeneratedImage,
  GeneratedVideo,
  Idea,
  Product,
  SystemInfo,
  UGCScript,
} from "./types";

const BASE =
  (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "") +
  "/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(detail, res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

const get = <T>(p: string) => request<T>(p);
const post = <T>(p: string, body?: unknown) =>
  request<T>(p, { method: "POST", body: body ? JSON.stringify(body) : undefined });
const patch = <T>(p: string, body?: unknown) =>
  request<T>(p, { method: "PATCH", body: body ? JSON.stringify(body) : undefined });
const del = <T>(p: string) => request<T>(p, { method: "DELETE" });

export const api = {
  base: BASE,

  brands: {
    list: () => get<Brand[]>("/brands"),
    get: (id: string) => get<Brand>(`/brands/${id}`),
    create: (body: Partial<Brand> & { name: string }) => post<Brand>("/brands", body),
    scrape: (url: string) => post<Brand>("/brands/scrape", { url }),
    update: (id: string, body: Partial<Brand>) => patch<Brand>(`/brands/${id}`, body),
    remove: (id: string) => del<{ message: string }>(`/brands/${id}`),
    products: (id: string) => get<Product[]>(`/brands/${id}/products`),
    createProduct: (
      id: string,
      body: { name: string; source_type: "url" | "manual"; source_url?: string | null } & Record<string, unknown>
    ) => post<Product>(`/brands/${id}/products`, body),
  },

  products: {
    get: (pid: string) => get<Product>(`/products/${pid}`),
    update: (pid: string, body: Partial<Product>) => patch<Product>(`/products/${pid}`, body),
    remove: (pid: string) => del<{ message: string }>(`/products/${pid}`),
    analyze: (pid: string) => post<Product>(`/products/${pid}/analyze`),
    updateAnalysis: (pid: string, analysis: Record<string, unknown>) =>
      patch<Product>(`/products/${pid}/analysis`, { analysis }),
    rescrape: (pid: string) => post<Product>(`/products/${pid}/rescrape`),
  },

  ideas: {
    list: (pid: string) => get<Idea[]>(`/products/${pid}/ideas`),
    generate: (pid: string, body: { prompt: string; count?: number }) =>
      post<Idea[]>(`/products/${pid}/ideas`, body),
    select: (pid: string, id: string) => post<Idea>(`/products/${pid}/ideas/${id}/select`),
    setStatus: (pid: string, id: string, status: string) =>
      patch<Idea>(`/products/${pid}/ideas/${id}`, { status }),
  },

  copy: {
    list: (pid: string) => get<GeneratedCopy[]>(`/products/${pid}/copy`),
    generate: (pid: string, body: { platform: string; tone: string; variations?: number; instructions?: string }) =>
      post<GeneratedCopy>(`/products/${pid}/copy`, body),
    save: (pid: string, id: string, is_saved: boolean) =>
      patch<GeneratedCopy>(`/products/${pid}/copy/${id}/save`, { is_saved }),
    remove: (pid: string, id: string) => del<{ message: string }>(`/products/${pid}/copy/${id}`),
  },

  images: {
    list: (pid: string) => get<GeneratedImage[]>(`/products/${pid}/images`),
    generate: (
      pid: string,
      body: { category: string; format: string; count?: number; prompt?: string; headline?: string; cta?: string }
    ) => post<GeneratedImage[]>(`/products/${pid}/images`, body),
    save: (pid: string, id: string, is_saved: boolean) =>
      patch<GeneratedImage>(`/products/${pid}/images/${id}/save`, { is_saved }),
    remove: (pid: string, id: string) => del<{ message: string }>(`/products/${pid}/images/${id}`),
  },

  videos: {
    list: (pid: string) => get<GeneratedVideo[]>(`/products/${pid}/videos`),
    createScript: (pid: string, body: { duration: string; format: string; instructions?: string; idea_id?: string }) =>
      post<GeneratedVideo>(`/products/${pid}/videos`, body),
    update: (pid: string, id: string, body: { script?: string; voiceover?: string; status?: string }) =>
      patch<GeneratedVideo>(`/products/${pid}/videos/${id}`, body),
    reprompt: (pid: string, id: string, instructions: string) =>
      post<GeneratedVideo>(`/products/${pid}/videos/${id}/reprompt`, { instructions }),
    frames: (pid: string, id: string) => post<GeneratedVideo>(`/products/${pid}/videos/${id}/frames`),
    render: (pid: string, id: string) => post<GeneratedVideo>(`/products/${pid}/videos/${id}/render`),
    save: (pid: string, id: string, is_saved: boolean) =>
      patch<GeneratedVideo>(`/products/${pid}/videos/${id}/save`, { is_saved }),
    remove: (pid: string, id: string) => del<{ message: string }>(`/products/${pid}/videos/${id}`),
  },

  ugc: {
    list: (pid: string) => get<UGCScript[]>(`/products/${pid}/ugc`),
    generate: (pid: string, body: { voice_style: string; emotion: string; audience?: string; instructions?: string }) =>
      post<UGCScript>(`/products/${pid}/ugc`, body),
    save: (pid: string, id: string, is_saved: boolean) =>
      patch<UGCScript>(`/products/${pid}/ugc/${id}/save`, { is_saved }),
    remove: (pid: string, id: string) => del<{ message: string }>(`/products/${pid}/ugc/${id}`),
  },

  scoring: {
    list: (pid: string) => get<CreativeScore[]>(`/products/${pid}/scores`),
    score: (pid: string, body: { target_type: string; target_id?: string; text?: string }) =>
      post<CreativeScore>(`/products/${pid}/score`, body),
  },

  exports: {
    list: (productId?: string) =>
      get<ExportItem[]>(`/exports${productId ? `?product_id=${productId}` : ""}`),
    create: (body: { product_id?: string | null; kind: string; label?: string; asset_ids?: string[] }) =>
      post<ExportItem>("/exports", body),
  },

  analytics: { summary: (days = 14) => get<AnalyticsSummary>(`/analytics/summary?days=${days}`) },

  settings: {
    get: () => get<AppSettings>("/settings"),
    update: (body: Partial<AppSettings>) => patch<AppSettings>("/settings", body),
    system: () => get<SystemInfo>("/settings/system"),
  },
};
