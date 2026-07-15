import {
  BarChart3,
  Boxes,
  Download,
  LayoutDashboard,
  Package,
  Settings,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  group: "Overview" | "Manage";
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, group: "Overview" },
  { label: "Brands", href: "/brands", icon: Boxes, group: "Overview" },
  { label: "Products", href: "/products", icon: Package, group: "Overview" },
  { label: "Analytics", href: "/analytics", icon: BarChart3, group: "Manage" },
  { label: "Export Center", href: "/exports", icon: Download, group: "Manage" },
  { label: "Settings", href: "/settings", icon: Settings, group: "Manage" },
];

export const NAV_GROUPS: NavItem["group"][] = ["Overview", "Manage"];
