<template>
  <div class="auth-root flex flex-center q-pa-md">
    <q-card flat bordered class="auth-card q-pa-lg">
      <q-card-section class="text-center q-pt-none">
        <div class="text-h6 text-primary">{{ $t("appTitle") }}</div>
      </q-card-section>
      <q-card-section>
        <router-view />
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.auth-root {
  min-height: 100vh;
  background: #f5f5f5;
}
.body--dark .auth-root {
  background: #121212;
}
.auth-card {
  width: 100%;
  max-width: 420px;
}
</style>
