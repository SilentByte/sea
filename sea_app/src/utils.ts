/*
 * SEA / SMART ENGINEERING ASSISTANT
 * Copyright (c) 2024 SilentByte <https://silentbyte.com/>
 */

import { v4 as uuid4 } from "uuid";

export function uuid(): string {
    return uuid4();
}

export async function sleep(seconds: number): Promise<void> {
    return new Promise((resolve) => {
        setTimeout(resolve, seconds * 1000);
    });
}

export function openUrlInTab(url: string) {
    window.open(url, "_blank");
}

export async function blobToDataURL(blob: Blob): Promise<string> {
    return new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = () => reject(reader.error);
        reader.onabort = () => reject(new Error("Failed to convert blob into data URL"));
        reader.readAsDataURL(blob);
    });
}
