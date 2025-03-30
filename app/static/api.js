const isLocal = window.location.hostname === "localhost"
const apiBase = window.location.protocol + '//' + window.location.hostname
const apiRoot = "/api"
const apiPort = isLocal ? "5000" : ""

export function buildApiString(endpoint) {
    return apiBase + ':' + apiPort + apiRoot + endpoint
}

export async function fetchVideo(id) {
    const api_uri = id ? "/video" + "/" + id : "/video"
    try {
        const response = await fetch(buildApiString(api_uri), {
            method: "GET",
        });
        if (!response.ok) throw new Error("Failed to fetch");

        let data = await response.json();
        data["path"] = buildApiString("/videos/" + data.path)
        return data

    } catch (error) {
        console.error("Error:", error);
    }
}

export async function fetchVideoCount() {
    try {
        const response = await fetch(buildApiString("/video-count"), {
            method: "GET",
        });
        if (!response.ok) throw new Error("Failed to fetch");

        return await response.json();

    } catch (error) {
        console.error("Error:", error);
    }
}