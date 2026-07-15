import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { AuthGate } from "@/components/shared/auth-gate";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGate>
      <div className="min-h-screen">
        <Sidebar />
        <div className="lg:pl-[264px]">
          <Topbar />
          <main className="relative min-h-[calc(100vh-4rem)] overflow-hidden">
            <div className="aurora-bg opacity-[0.35]" />
            <div className="mx-auto w-full max-w-[1500px] px-4 py-8 lg:px-8 lg:py-10">
              {children}
            </div>
          </main>
        </div>
      </div>
    </AuthGate>
  );
}
