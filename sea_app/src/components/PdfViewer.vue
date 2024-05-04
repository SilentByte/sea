<!--
    SEA / SMART ENGINEERING ASSISTANT
    Copyright (c) 2024 SilentByte <https://silentbyte.com/>
-->

<template>
    <div>
        <vue-pdf-app class="pdf-viewer"
                     v-model:theme="pdfTheme"
                     :pdf="pdfDataUrl"
                     :page-number="pageNumber" />
    </div>
</template>

<script setup lang="ts">

import "vue3-pdf-app/dist/icons/main.css";

import {
    ref,
    toRefs,
    computed,
} from "vue";

import { useTheme } from "vuetify";

import VuePdfApp from "vue3-pdf-app";

import * as utils from "@/utils";

const props = defineProps<{
    url: string;
    pageNumber: number;
}>();

const propRefs = toRefs(props);
const theme = useTheme();

const pdfDataUrl = ref("");

const pdfTheme = computed(() => {
    console.log(theme.global.current.value.dark ? "dark" : "light");
    return theme.global.current.value.dark ? "dark" : "light";
});

async function fetchPdfDataFromUrl(url: string) {
    const response = await fetch(url, {
        credentials: "include",
    });

    const blob = await response.blob();

    return utils.blobToDataURL(blob);
}

(async() => {
    pdfDataUrl.value = await fetchPdfDataFromUrl(propRefs.url.value);
})();

</script>

<style lang="scss" scoped>

.pdf-viewer {
    height: calc(100vh - 64px);
}

</style>

<style lang="scss">

.pdf-app.dark {
    --pdf-toolbar-color: #2a2a2a !important;
    --pdf-app-background-color: #212121 !important;
    --pdf-button-hover-font-color: 0 !important;
    --pdf-input-color: #424242 !important;
}

.pdf-app.light {
    --pdf-toolbar-color: #2a2a2a !important;
    --pdf-app-background-color: #dddddd !important;
    --pdf-button-hover-font-color: 0 !important;
    --pdf-input-color: #424242 !important;
}

</style>
