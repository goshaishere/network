<template>
  <q-layout>
    <q-page-container>
      <q-page class="flex flex-center column q-pa-md">
        <div class="text-h4">404</div>
        <p>{{ $t("notFound.title") }}</p>
        <q-btn color="primary" :label="$t('notFound.back')" to="/" />
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts"></script>
