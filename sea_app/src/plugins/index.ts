/*
 * SEA / SMART ENGINEERING ASSISTANT
 * Copyright (c) 2024 SilentByte <https://silentbyte.com/>
 */

import vuetify from "./vuetify";

import type { App } from "vue";

export function registerPlugins(app: App) {
    app.use(vuetify);
}
