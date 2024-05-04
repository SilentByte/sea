<!--
    SEA / SMART ENGINEERING ASSISTANT
    Copyright (c) 2024 SilentByte <https://silentbyte.com/>
-->

<template>
    <v-app>
        <v-app-bar class="border-b-thin">
            <v-btn height="80"
                   color="primary"
                   class="ms-0 rounded-s-0 rounded-e-pill"
                   variant="flat">
                <img alt="S.E.A. / Smart Engineering Assistant"
                     src="@/assets/logo.svg"
                     height="42" />

                <div class="mx-2"
                     style="font-family: Ubuntu, Roboto, sans-serif; font-size: 22px">
                    S.E.A.
                </div>
            </v-btn>

            <v-spacer />

            <v-responsive max-width="300">
                <v-text-field flat hide-details
                              density="compact"
                              rounded="pill"
                              variant="solo-filled"
                              placeholder="Search..." />
            </v-responsive>

            <v-spacer />

            <v-btn class="mx-1"
                   size="small"
                   icon="mdi-robot-excited-outline"
                   :active="chatDrawerVisible"
                   @click="onToggleChat" />

            <v-btn class="ms-1 me-2"
                   size="small"
                   icon="mdi-theme-light-dark"
                   @click="onToggleTheme" />
        </v-app-bar>

        <v-navigation-drawer rail>
            <v-avatar class="d-block text-center mx-auto mt-4"
                      color="grey-darken-1"
                      size="36" />

            <v-divider class="mx-3 my-5" />

            <v-avatar v-for="n in 6" :key="n"
                      class="d-block text-center mx-auto mb-9"
                      color="grey-lighten-1"
                      size="28" />
        </v-navigation-drawer>

        <v-main>
            Main Content
        </v-main>

        <v-navigation-drawer floating permanent
                             class="border-s-thin"
                             location="right"
                             width="600"
                             v-model="chatDrawerVisible">
            <v-card v-if="chatHistory.length === 0"
                    variant="flat"
                    class="pa-2 fill-height overflow-y-auto d-flex align-center justify-center flex-column">
                <div>
                    <img alt="S.E.A. / Smart Engineering Assistant"
                         src="@/assets/logo.svg"
                         height="200"
                         style="opacity: 0.1" />
                </div>
                <div class="mt-4"
                     style="opacity: 0.25; font-family: Ubuntu, Roboto, sans-serif; font-size: 24px">
                    I'm Eugene, how may I help?
                </div>
            </v-card>
            <v-card v-else
                    variant="flat"
                    class="pa-2 fill-height overflow-y-auto">
                <v-card-text>
                    <v-row>
                        <v-col v-for="(ch, chatHistoryIndex) in chatHistory" :key="chatHistoryIndex"
                               cols="12">
                            <template v-if="ch.inferenceInteraction.originator === 'agent'">
                                <v-avatar class="me-2 pa-1"
                                          color="primary"
                                          size="30">
                                    <img alt="Agent"
                                         src="@/assets/logo.svg"
                                         width="100%"
                                         height="100%" />
                                </v-avatar>

                                <strong>Eugene: </strong>

                                <MarkdownDiv class="mt-2"
                                             :markdown="ch.inferenceInteraction.text" />
                            </template>
                            <template v-else>
                                <v-avatar class="me-2"
                                          size="30">
                                    <v-img alt="Agent"
                                           src="https://rab-stuff.web.app/sea/avatar.png" />
                                </v-avatar>

                                <strong>You: </strong>

                                {{ ch.inferenceInteraction.text }}
                            </template>

                            <div v-if="ch.sources.length > 0"
                                 class="text-center">
                                <v-chip v-for="(s, sourceIndex) in ch.sources" :key="sourceIndex"
                                        class="ma-1"
                                        size="x-small"
                                        rounded="pill"
                                        :title="formatSourceName(s, false)"
                                        @click="onOpenSource(s)">
                                    {{ formatSourceName(s, true) }}
                                </v-chip>
                            </div>
                        </v-col>

                        <v-col v-if="chatInteractionPending"
                               cols="12">
                            <v-avatar class="me-2 pa-1"
                                      color="primary"
                                      size="30">
                                <img alt="Agent"
                                     src="@/assets/logo.svg"
                                     width="100%"
                                     height="100%" />
                            </v-avatar>

                            <strong>Eugene: </strong>

                            <v-skeleton-loader type="text@4" />
                        </v-col>
                    </v-row>
                </v-card-text>

                <div ref="chatHistoryEndMarker" />
            </v-card>

            <template v-slot:append>
                <v-textarea flat hide-details auto-grow no-resize rounded
                            class="ma-2 hide-scrollbar outlined-textarea-scrollbar-fix"
                            density="compact"
                            variant="outlined"
                            rows="1"
                            max-rows="6"
                            placeholder="What's your question?"
                            v-model="currentMessage"
                            @keydown=onChatKeyDown>
                    <template v-slot:append-inner>
                        <v-btn variant="flat"
                               color="primary"
                               size="x-small"
                               icon="mdi-chevron-right"
                               :loading="chatInteractionPending"
                               @click="onSendMessage" />
                    </template>
                </v-textarea>
            </template>
        </v-navigation-drawer>
    </v-app>
</template>

<script setup lang="ts">

import {
    nextTick,
    ref,
} from "vue";

import { useTheme } from "vuetify";

import type { IInferenceInteraction, IInferenceSource } from "@/api";
import { SeaApiClient } from "@/api";
import MarkdownDiv from "@/components/MarkdownDiv.vue";

interface IChatHistory {
    inferenceInteraction: IInferenceInteraction;
    sources: IInferenceSource[];
}

const theme = useTheme();

const chatDrawerVisible = ref(true);
const currentMessage = ref("");
const chatHistoryEndMarker = ref(null);
const chatHistory = ref<IChatHistory[]>([]);
const chatInteractionPending = ref(false);

const BASE_URL = "http://localhost:8000/api/";
const TEST_TOKEN = "";

const apiClient = new SeaApiClient(BASE_URL, TEST_TOKEN);

function formatSourceName(s: IInferenceSource, truncate: boolean) {
    const MAX_TRUNCATED_LENGTH = 28;

    let name = s.file_name;

    if(truncate && s.file_name.length > MAX_TRUNCATED_LENGTH) {
        name = name.substring(0, MAX_TRUNCATED_LENGTH - 1) + "…";
    }

    if(s.start_page_no === s.end_page_no) {
        return `${name} p. ${s.start_page_no}`;
    }

    return `${name} pp. ${s.start_page_no}-${s.end_page_no}`;
}

async function scrollChatHistoryToBottom() {
    const element = (chatHistoryEndMarker.value as any);
    if(element) {
        await nextTick();
        element.scrollIntoView({behavior: "smooth"});
    }
}

function onToggleTheme() {
    theme.global.name.value = theme.global.current.value.dark ? "seaLight" : "seaDark";
}

function onToggleChat() {
    chatDrawerVisible.value = !chatDrawerVisible.value;
}

async function onSendMessage() {
    if(chatInteractionPending.value) {
        return;
    }

    const message = currentMessage.value.trim();

    if(!message) {
        return;
    }

    chatInteractionPending.value = true;
    currentMessage.value = "";

    try {
        chatHistory.value.push({
            inferenceInteraction: {
                originator: "user",
                text: message,
            },
            sources: [],
        });

        await scrollChatHistoryToBottom();

        const response = await apiClient.inferenceQuery(chatHistory.value.map(ch => ch.inferenceInteraction));

        chatHistory.value.push({
            inferenceInteraction: {
                originator: "agent",
                text: response.text,
            },
            sources: response.sources,
        });

        await scrollChatHistoryToBottom();
    } finally {
        chatInteractionPending.value = false;
    }
}

function onChatKeyDown(e: KeyboardEvent) {
    if(e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        onSendMessage();
    }
}

function onOpenSource(source: IInferenceSource) {
    console.log(source);
}

</script>
