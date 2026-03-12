<template>
  <div class="home">
    <h1>Multi-Asset Invest</h1>
    <p>대시보드 진입점</p>
    <ul class="entry-links">
      <li><router-link to="/events">이벤트 목록</router-link></li>
      <li><router-link to="/assets">지원 자산 목록</router-link></li>
      <li><router-link to="/assets/impacts">자산별 영향</router-link></li>
      <li><router-link to="/crawl-sources">수집 소스 설정</router-link></li>
    </ul>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.entry-links { margin-top: 1rem; list-style: none; padding: 0; }
.entry-links li { margin: 0.5rem 0; }
.entry-links a { margin-right: 0.5rem; }
</style>
