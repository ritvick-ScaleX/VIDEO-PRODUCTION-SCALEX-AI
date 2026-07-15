"use client";

import { ArrowUpRight, Package, Plus } from "lucide-react";
import Link from "next/link";
import { FadeItem, StaggerGroup } from "@/components/animations/motion";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useActiveBrand, useProducts } from "@/lib/hooks";
import type { ProductStatus } from "@/lib/types";
import { initials, statusLabel, timeAgo } from "@/lib/utils";

const STATUS_VARIANT: Record<ProductStatus, NonNullable<BadgeProps["variant"]>> = {
  ready: "success",
  error: "destructive",
  draft: "outline",
  scraping: "accent",
  analyzing: "accent",
};

export function RecentProducts() {
  const { activeId, active } = useActiveBrand();
  const { data, isLoading } = useProducts(activeId ?? undefined);

  const products = [...(data ?? [])]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  return (
    <Card className="h-full">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div className="space-y-1.5">
          <CardTitle>Recent products</CardTitle>
          <CardDescription>
            {active ? `In ${active.name}` : "Your latest products"}
          </CardDescription>
        </div>
        <Button asChild variant="ghost" size="sm">
          <Link href="/products">View all</Link>
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3 rounded-2xl p-2.5">
                <Skeleton className="h-11 w-11 rounded-xl" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-3.5 w-2/5" />
                  <Skeleton className="h-3 w-1/4" />
                </div>
              </div>
            ))}
          </div>
        ) : products.length === 0 ? (
          <EmptyState
            icon={Package}
            title="No products yet"
            description="Add a product by URL or manually to start generating creative."
            action={
              <Button asChild variant="aurora" size="sm">
                <Link href="/products">
                  <Plus className="h-4 w-4" />
                  New Product
                </Link>
              </Button>
            }
          />
        ) : (
          <StaggerGroup className="space-y-1">
            {products.map((product) => (
              <FadeItem key={product.id}>
                <Link
                  href={`/products/${product.id}`}
                  className="group flex items-center gap-3 rounded-2xl p-2.5 transition-colors hover:bg-white/[0.03] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
                >
                  <Avatar className="h-11 w-11 rounded-xl">
                    {product.thumbnail_url && (
                      <AvatarImage
                        src={product.thumbnail_url}
                        alt={product.name}
                        className="rounded-xl object-cover"
                      />
                    )}
                    <AvatarFallback className="rounded-xl text-sm">
                      {initials(product.name || "New")}
                    </AvatarFallback>
                  </Avatar>

                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-foreground">
                      {product.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {timeAgo(product.created_at)}
                    </p>
                  </div>

                  <Badge variant={STATUS_VARIANT[product.status] ?? "outline"}>
                    {statusLabel(product.status)}
                  </Badge>
                  <ArrowUpRight className="h-4 w-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
                </Link>
              </FadeItem>
            ))}
          </StaggerGroup>
        )}
      </CardContent>
    </Card>
  );
}

export default RecentProducts;
