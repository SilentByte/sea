/*
 * SEA / SMART ENGINEERING ASSISTANT
 * Copyright (c) 2024 SilentByte <https://silentbyte.com/>
 */

import Cookies from "js-cookie";

export interface IAuthenticatedUser {
    display_name: string;
}

export interface IInferenceInteraction {
    originator: "user" | "agent";
    text: string;
}

export interface IInferenceSource {
    text: string;
    file_name: string;
    file_hash: string;
    start_page_no: number;
    end_page_no: number;
}

export interface IInferenceResult {
    text: string;
    sources: IInferenceSource[];
}

export class SeaApiClient {
    private token: string | null = null;

    constructor(private baseUrl: string, token: string | null = null) {
        this.updateToken(token);
    }

    private updateToken(token: string | null) {
        this.token = token;

        if(this.token) {
            localStorage.setItem("app.token", this.token);
            Cookies.set("X-Authorization-Token", this.token);
        } else {
            localStorage.removeItem("app.token");
            Cookies.remove("X-Authorization-Token");
        }
    }

    private async request(method: "POST" | "GET", url: string, options: {
        body?: any;
        token?: string | null;
    }): Promise<any> {
        console.log(`Sending API request to ${method} ${url}:`);
        console.log(options.body);

        const response = await fetch(new URL(url, this.baseUrl), {
            method,
            body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
            headers: {
                ...(options.token !== undefined ? {"Authorization": `Bearer ${options.token}`} : {}),
                ...(options.body !== undefined ? {"Content-Type": "application/json"} : {}),
            },
        });

        if(!response.ok) {
            throw new Error(`Request Failed: ${response.status} ${response.statusText}`);
        }

        const responseData = await response.json();

        console.log(`Received API response from ${method} ${url}:`);
        console.log(responseData);

        return responseData;
    }

    async authenticate(email: string, password: string): Promise<IAuthenticatedUser> {
        const response = await this.request("POST", "authenticate", {
            body: {
                email,
                credentials: password,
            },
        });

        this.updateToken(response.token);

        return {
            display_name: response.display_name,
        };
    }

    async inferenceQuery(inference_interactions: IInferenceInteraction[]): Promise<IInferenceResult> {
        return await this.request("POST", "inference/query", {
            token: this.token,
            body: {
                inference_interactions,
            },
        });
    }

    buildDocumentUrl(hash: string): string {
        return (new URL(`document/${hash}`, this.baseUrl)).toString();
    }
}
