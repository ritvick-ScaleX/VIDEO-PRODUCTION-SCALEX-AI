"use client";

import { Boxes } from "lucide-react";
import Link from "next/link";
import { EmptyState } from "@/components/ui/empty-state";
import { Button } from "@/components/ui/button";

export function NoBrand({ feature = "get started" }: { feature?: string }) {
  return (
    <EmptyState
      icon={Boxes}
      title="Create a brand first"
      description={`Add a brand, then list its products to ${feature}.`}
      action={
        <Button asChild variant="aurora">
          <Link href="/brands">Create your first brand</Link>
        </Button>
      }
    />
  );
}
