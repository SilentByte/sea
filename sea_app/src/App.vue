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

            <v-btn size="small"
                   icon="mdi-theme-light-dark"
                   @click="onToggleTheme" />
        </v-app-bar>

        <v-navigation-drawer rail>
            <v-avatar class="d-block text-center mx-auto mt-4"
                      color="grey-darken-1"
                      size="36" />

            <v-divider class="mx-3 my-5" />

            <v-avatar
                    v-for="n in 6"
                    :key="n"
                    class="d-block text-center mx-auto mb-9"
                    color="grey-lighten-1"
                    size="28" />
        </v-navigation-drawer>

        <v-main>
            Main Content
        </v-main>

        <v-navigation-drawer floating
                             location="right"
                             width="600">
            <v-card variant="flat"
                    class="pa-2 fill-height">
                Chat
            </v-card>

            <template v-slot:append>
                <v-textarea flat hide-details auto-grow no-resize rounded
                            class="ma-2 outlined-textarea-scrollbar-fix"
                            density="compact"
                            variant="outlined"
                            rows="1"
                            max-rows="6"
                            placeholder="What's your question?" />
            </template>
        </v-navigation-drawer>
    </v-app>
</template>

<script setup lang="ts">

import { useTheme } from "vuetify";

const theme = useTheme();

function onToggleTheme() {
    theme.global.name.value = theme.global.current.value.dark ? "seaLight" : "seaDark";
}

</script>

<style lang="scss">

</style>
