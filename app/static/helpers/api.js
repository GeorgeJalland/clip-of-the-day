const isLocal = window.location.hostname === "localhost"
const apiBase = window.location.protocol + '//' + window.location.hostname
const apiRoot = "/api"
const apiPort = isLocal ? "5000" : ""

export function buildApiString(endpoint) {
    return apiBase + ':' + apiPort + apiRoot + endpoint
}

export async function fetchVideo(id, playerId, action = null) {
    let api_uri = "/video" + "/" + id + "?"
    if (playerId !== null) {
        api_uri += "player=" + playerId + "&"
    }
    if (action !== null) {
        api_uri += "action=" + action + "&"
    }
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

export async function fetchVideoCount(playerId) {
    let api_uri = "/video-count"
    if (playerId !== null) {
        api_uri += "?player=" + playerId
    }
    try {
        const response = await fetch(buildApiString(api_uri), {
            method: "GET",
        });
        if (!response.ok) throw new Error("Failed to fetch");

        return await response.json();

    } catch (error) {
        console.error("Error:", error);
    }
}

export async function fetchPlayers() {
    try {
        const response = await fetch(buildApiString("/players"), {
            method: "GET",
        });
        if (!response.ok) throw new Error("Failed to fetch");

        return await response.json();

    } catch (error) {
        console.error("Error:", error);
    }
}
