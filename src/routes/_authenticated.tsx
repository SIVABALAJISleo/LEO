import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { getToken } from "@/lib/leo-client";

export const Route = createFileRoute("/_authenticated")({
  beforeLoad: ({ location }) => {
    if (!getToken()) {
      throw redirect({ to: "/login", search: { redirect: location.href } as never });
    }
  },
  ssr: false,
  component: () => <Outlet />,
});
