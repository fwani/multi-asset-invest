import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'Home', component: () => import('@/pages/Home.vue') },
    { path: '/events', name: 'EventsList', component: () => import('@/pages/EventsList.vue') },
    { path: '/events/:id', name: 'EventDetail', component: () => import('@/pages/EventDetail.vue') },
    { path: '/assets', name: 'AssetsList', component: () => import('@/pages/AssetsList.vue') },
    { path: '/assets/impacts', name: 'AssetImpacts', component: () => import('@/pages/AssetImpacts.vue') },
    { path: '/crawl-sources', name: 'CrawlSources', component: () => import('@/pages/CrawlSources.vue') },
  ],
})

export default router
