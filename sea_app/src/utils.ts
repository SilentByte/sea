/*
 * SEA / SMART ENGINEERING ASSISTANT
 * Copyright (c) 2024 SilentByte <https://silentbyte.com/>
 */

export async function sleep(seconds: number): Promise<void> {
    return new Promise((resolve) => {
        setTimeout(resolve, seconds * 1000);
    });
}
