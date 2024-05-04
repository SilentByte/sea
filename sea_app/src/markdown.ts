/*
 * SEA / SMART ENGINEERING ASSISTANT
 * Copyright (c) 2024 SilentByte <https://silentbyte.com/>
 */

import { marked } from "marked";
import DOMPurify from "dompurify";

const purify = DOMPurify(window);

export function toHtml(markdown: string): string {
    return purify.sanitize(marked(markdown, {async: false}) as string);
}
