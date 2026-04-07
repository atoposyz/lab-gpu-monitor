import { createRouter, createWebHistory } from "vue-router";
import OverviewPage from "../pages/OverviewPage.vue";
import LoginPage from "../pages/LoginPage.vue";
import ApplyAccountPage from "../pages/ApplyAccountPage.vue";
import AdminApplicationsPage from "../pages/AdminApplicationsPage.vue";
import AnnouncementsPage from "../pages/AnnouncementsPage.vue";
import { useAuth } from "../composables/useAuth";

const routes = [
  { path: "/", name: "Overview", component: OverviewPage },
  { path: "/login", name: "Login", component: LoginPage },
  { path: "/apply", name: "ApplyAccount", component: ApplyAccountPage, meta: { requiresAuth: true } },
  { path: "/admin/applications", name: "AdminApplications", component: AdminApplicationsPage, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: "/announcements", name: "Announcements", component: AnnouncementsPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuth();
  if (auth.token.value && !auth.user.value) {
    try {
      await auth.fetchMe();
    } catch {
      auth.logout();
    }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated.value) {
    return { name: "Login" };
  }
  if (to.meta.requiresAdmin && !auth.isAdmin.value) {
    return { name: "Overview" };
  }

  return true;
});

export default router;
