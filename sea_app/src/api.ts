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

export interface IDocumentSearchResult {
    file_name: string;
    file_hash: string;
}

export class SeaApiClient {
    private token: string | null = null;

    constructor(private baseUrl: string, token: string | undefined | null = undefined) {
        this.updateToken(token);
    }

    get isAuthenticated(): boolean {
        return !!this.token;
    }

    private updateToken(token?: string | null) {
        if(token === undefined && this.token === null) {
            this.token = localStorage.getItem("app.token");
        } else if(token !== undefined) {
            this.token = token;
        }

        if(this.token) {
            localStorage.setItem("app.token", this.token);
            Cookies.set("X-Authorization-Token", this.token);
        } else {
            localStorage.removeItem("app.token");
            Cookies.remove("X-Authorization-Token");
        }
    }

    private async request(method: "POST" | "GET", url: string, options: {
        query?: Record<string, any>,
        body?: any;
        token?: string | null;
    }): Promise<any> {
        if(options.query) {
            url = url + "?" + new URLSearchParams(options.query);
        }

        console.log(`Sending API request to ${method} ${url}:`);

        if(options.body) {
            console.log(options.body);
        }

        const response = await fetch(new URL(url, this.baseUrl), {
            method,
            body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
            credentials: "include",
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

    clearToken(): void {
        this.updateToken(null);
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

    async searchDocuments(query: string): Promise<IDocumentSearchResult[]> {
        return await this.request("GET", "search_documents", {
            query: {
                query,
            },
        });
    }

    buildDocumentUrl(hash: string): string {
        return (new URL(`document/${hash}`, this.baseUrl)).toString();
    }
}
