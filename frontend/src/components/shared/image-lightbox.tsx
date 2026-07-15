"use client";

import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from "@/components/ui/dialog";

/** Full-size image preview popup. Controlled by `src` (null = closed). */
export function ImageLightbox({
  src,
  alt = "Preview",
  onClose,
  downloadable = true,
}: {
  src: string | null;
  alt?: string;
  onClose: () => void;
  downloadable?: boolean;
}) {
  return (
    <Dialog open={!!src} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-4xl border-white/10 bg-background/80 p-3">
        <DialogTitle className="sr-only">{alt}</DialogTitle>
        {src && (
          <div className="flex flex-col gap-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={src}
              alt={alt}
              className="max-h-[78vh] w-full rounded-2xl object-contain"
            />
            {downloadable && (
              <div className="flex justify-center">
                <Button asChild variant="glass" size="sm">
                  <a href={src} target="_blank" rel="noopener noreferrer" download>
                    <Download className="h-4 w-4" /> Download
                  </a>
                </Button>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
