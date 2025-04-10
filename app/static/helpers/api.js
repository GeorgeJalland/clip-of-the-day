const isLocal = window.location.hostname === "localhost"
const apiBase = window.location.protocol + '//' + window.location.hostname
const apiRoot = "/api"
const apiPort = isLocal ? "8000" : ""

export function buildApiString(endpoint) {
    return apiBase + ':' + apiPort + apiRoot + endpoint
}

export async function fetchVideo(id, playerId=null) {
    let api_uri = "/video" + "/" + id + "?"
    if (playerId !== null) {
        api_uri += "player=" + playerId + "&"
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

export async function submitRating(rating, videoId) {
    try {
        fetch(buildApiString("/rating"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                rating,
                videoId,
            }),
        });
    } catch (error) {
        console.error("Error:", error);
    }
}
