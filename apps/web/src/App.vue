<template>
  <div>
    <nav>
      <router-link to="/">홈</router-link>
      <router-link to="/events">이벤트</router-link>
      <router-link to="/assets">자산</router-link>
      <router-link to="/assets/impacts">자산별 영향</router-link>
      <router-link to="/crawl-sources">수집 소스</router-link>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
nav { padding: 0.5rem 1rem; border-bottom: 1px solid #eee; }
nav a { margin-right: 1rem; }
main { padding: 1rem; }
</style>
