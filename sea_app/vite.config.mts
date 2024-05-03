/*
 * SEA / SMART ENGINEERING ASSISTANT
 * Copyright (c) 2024 SilentByte <https://silentbyte.com/>
 */

import Components from "unplugin-vue-components/vite";
import Vue from "@vitejs/plugin-vue";
import ViteFonts from "unplugin-fonts/vite";
import Vuetify, { transformAssetUrls } from "vite-plugin-vuetify";

import { defineConfig } from "vite";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
    plugins: [
        Vue({
            template: {transformAssetUrls},
        }),
        Vuetify(),
        Components(),
        ViteFonts({
            google: {
                families: [{
                    name: "Ubuntu",
                    styles: "wght@100;300;400;500;700;900",
                }],
            },
        }),
    ],
    define: {"process.env": {}},
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
        extensions: [
            ".js",
            ".json",
            ".jsx",
            ".mjs",
            ".ts",
            ".tsx",
            ".vue",
        ],
    },
    server: {
        port: 3000,
    },
});
