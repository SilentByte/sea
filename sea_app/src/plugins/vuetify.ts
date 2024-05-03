/*
 * SEA / SMART ENGINEERING ASSISTANT
 * Copyright (c) 2024 SilentByte <https://silentbyte.com/>
 */

import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";

import { createVuetify } from "vuetify";
import { md3 } from "vuetify/blueprints";

export default createVuetify({
    blueprint: md3,
    theme: {
        defaultTheme: "light",
    },
});
