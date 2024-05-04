/*
 * SEA / SMART ENGINEERING ASSISTANT
 * Copyright (c) 2024 SilentByte <https://silentbyte.com/>
 */

import "@/styles/app.scss";

import { createApp } from "vue";
import { createPinia } from "pinia";

import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import { md3 } from "vuetify/blueprints";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import App from "@/App.vue";
import router from "@/router";

const vuetify = createVuetify({
    theme: {
        defaultTheme: "seaDark",
        themes: {
            seaLight: {
                dark: false,
                colors: {
                    primary: "#28487b",
                },
            },
            seaDark: {
                dark: true,
                colors: {
                    primary: "#28487b",
                },
            },
        },
    },

    blueprint: md3,
    components,
    directives,
});

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(vuetify);

app.mount("#app");
