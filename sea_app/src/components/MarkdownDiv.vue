<!--
    SEA / SMART ENGINEERING ASSISTANT
    Copyright (c) 2024 SilentByte <https://silentbyte.com/>
-->

<template>
    <div v-html="formatMarkdown(markdown)"
         class="markdown-div" />
</template>

<script setup lang="ts">

import * as md from "@/markdown";

defineProps<{
    markdown: string;
}>();

function formatMarkdown(text: string): string {
    return md.toHtml(text);
}

</script>

<style lang="scss" scoped>

.markdown-div {
    :deep(p) {
        margin-bottom: 1em;
    }

    :deep(ol, ul) {
        margin-bottom: 1.2em;
    }

    :deep(ol, ul) {
        margin-left: 16px;
        list-style-position: outside;
        font-size: 0.8em;
    }

    :deep(li) {
        margin-bottom: 0.5em;
        padding-left: 8px;
    }
}

</style>
