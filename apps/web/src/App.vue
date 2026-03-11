<template>
  <div>
    <nav>
      <router-link to="/">홈</router-link>
      <router-link to="/events">이벤트</router-link>
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
