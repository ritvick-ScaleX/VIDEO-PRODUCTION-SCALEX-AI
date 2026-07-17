// TypeScript mirror of the backend schemas — Brand → Product → creative.

export interface ProductAnalysis {
  brand_voice?: string;
  customer_persona?: string;
  pain_points?: string[];
  benefits?: string[];
  marketing_angles?: string[];
  offers?: string[];
  hooks?: string[];
  cta_suggestions?: string[];
  emotional_triggers?: string[];
  usp?: string;
  strategy_summary?: string;
  [key: string]: unknown;
}

export interface Brand {
  id: string;
  name: string;
  website: string | null;
  logo_url: string | null;
  brand_colors: string[];
  fonts: string[];
  brand_voice: string | null;
  writing_style: string | null;
  target_audience: string | null;
  tagline: string | null;
  mission: string | null;
  meta: Record<string, unknown>;
  product_count: number;
  created_at: string;
  updated_at: string;
}

export type ProductStatus = "draft" | "scraping" | "analyzing" | "ready" | "error";
export type SourceType = "url" | "manual";

export interface Product {
  id: string;
  brand_id: string;
  name: string;
  source_type: SourceType;
  source_url: string | null;
  status: ProductStatus;
  description: string | null;
  features: string[];
  benefits: string[];
  ingredients: string[];
  price: string | null;
  target_audience: string | null;
  cta: string | null;
  images: string[];
  selected_images: string[];
  logo_url: string | null;
  brand_colors: string[];
  hero_content: string | null;
  reviews: Record<string, unknown>[];
  faqs: Record<string, unknown>[];
  thumbnail_url: string | null;
  raw_scrape: Record<string, unknown>;
  analysis: ProductAnalysis;
  created_at: string;
  updated_at: string;
}

export type IdeaStatus = "pending" | "selected" | "rejected";

export type IdeaKind = "image" | "video";

export interface Idea {
  id: string;
  product_id: string;
  prompt: string | null;
  batch_id: string | null;
  kind: IdeaKind;
  title: string | null;
  angle: string | null;
  description: string | null;
  hook: string | null;
  status: IdeaStatus;
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export type CopyPlatform =
  | "facebook" | "instagram" | "google" | "linkedin"
  | "twitter" | "landing_page" | "email" | "headline";
export type Tone = "luxury" | "professional" | "friendly" | "minimal";

export interface CopyVariation {
  headline: string;
  body: string;
  cta: string;
  angle?: string;
}

export interface GeneratedCopy {
  id: string;
  product_id: string;
  platform: CopyPlatform;
  tone: Tone;
  headline: string | null;
  body: string | null;
  cta: string | null;
  variations: CopyVariation[];
  meta: Record<string, unknown>;
  is_saved: boolean;
  created_at: string;
  updated_at: string;
}

export type ImageFormat =
  | "square" | "portrait" | "landscape" | "story" | "carousel" | "poster" | "lifestyle";
export type ImageCategory = "white_background" | "creative" | "product_shot";

export type ReviewStatus = "pending" | "accepted" | "rejected";

export interface GeneratedImage {
  id: string;
  product_id: string;
  category: ImageCategory;
  format: ImageFormat;
  prompt: string | null;
  url: string;
  width: number;
  height: number;
  meta: Record<string, unknown>;
  is_saved: boolean;
  review_status: ReviewStatus;
  review_comment: string | null;
  created_at: string;
  updated_at: string;
}

export interface StoryboardScene {
  scene: string;
  visual: string;
  voiceover: string;
  on_screen_text: string;
  duration: string;
}

export type VideoStatus = "draft" | "frames_ready" | "rendering" | "ready" | "error";

export interface GeneratedVideo {
  id: string;
  product_id: string;
  idea_id: string | null;
  duration: string;
  format: string;
  script: string | null;
  storyboard: StoryboardScene[];
  voiceover: string | null;
  captions: string[];
  transitions: string[];
  frame_urls: string[];
  thumbnail_url: string | null;
  video_url: string | null;
  status: VideoStatus;
  progress: number;
  meta: Record<string, unknown>;
  is_saved: boolean;
  created_at: string;
  updated_at: string;
}

export interface UGCScene {
  scene: string;
  action: string;
  dialogue: string;
  duration: string;
}

export interface UGCScript {
  id: string;
  product_id: string;
  hook: string | null;
  script: string | null;
  camera_directions: string[];
  scene_breakdown: UGCScene[];
  b_roll: string[];
  cta: string | null;
  voice_style: string | null;
  emotion: string | null;
  audience: string | null;
  meta: Record<string, unknown>;
  is_saved: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreativeScore {
  id: string;
  product_id: string;
  target_type: "copy" | "image" | "video" | "ugc";
  target_id: string | null;
  overall: number;
  hook_strength: number;
  readability: number;
  brand_consistency: number;
  visual_hierarchy: number;
  cta_quality: number;
  emotion: number;
  conversion_potential: number;
  suggestions: string[];
  summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExportItem {
  id: string;
  product_id: string | null;
  kind: "png" | "jpg" | "mp4" | "pdf" | "zip";
  label: string;
  url: string;
  size_bytes: number;
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface StatCard {
  key: string;
  label: string;
  value: number;
  delta: number;
}

export interface TimeseriesPoint {
  date: string;
  brands: number;
  products: number;
  ideas: number;
  images: number;
  videos: number;
  exports: number;
  [key: string]: string | number;
}

export interface ActivityItem {
  id: string;
  brand_id: string | null;
  product_id: string | null;
  event_type: string;
  meta: Record<string, unknown>;
  created_at: string;
}

export interface AnalyticsSummary {
  stats: StatCard[];
  timeseries: TimeseriesPoint[];
  activity: ActivityItem[];
  platform_breakdown: Record<string, number>;
  avg_score: number;
}

export interface AppSettings {
  id: string;
  theme: string;
  language: string;
  ai_model: string;
  storage_backend: string;
  generation_prefs: Record<string, unknown>;
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface SystemInfo {
  app_name: string;
  version: string;
  environment: string;
  storage_backend: string;
  text_provider: string;
  text_model: string;
  text_mode: "live" | "mock";
  image_provider: string;
  image_mode: "live" | "mock";
  video_provider: string;
  video_mode: "live" | "mock";
  ai_mode: "live" | "mock";
  ai_model: string;
}
