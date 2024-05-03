/*
 * SEA / SMART ENGINEERING ASSISTANT
 * Copyright (c) 2024 SilentByte <https://silentbyte.com/>
 */

import { registerPlugins } from "@/plugins";

import App from "./App.vue";

import { createApp } from "vue";

const app = createApp(App);

registerPlugins(app);

app.mount("#app");
