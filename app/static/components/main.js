import { fetchVideo, fetchVideoCount, fetchPlayers } from "../helpers/api.js"
import { getRandomNumber, mod } from "../helpers/utils.js"

export class Main {
    constructor() {
        this.state = {
            videoCount: 0,
            video: {},
            minVideoId: 0,
            maxVideoId: 0,
            hasPlayerRated: false,
            selectedPlayer: {
                id: null,
                name: "All",
                elementId: "player-all"
            },
            players: [],
        }

        this.elements = {
            main: document.getElementById("main"),
            video: document.getElementById("videoElement"),
            index: document.getElementById("videoIndex"),
            playerDate: document.getElementById("playerDate"),
            videoSource: document.getElementById("videoSource"),
            ratings: document.getElementById("ratings"),
            prev: document.getElementById("prev"),
            next: document.getElementById("next"),
            random: document.getElementById("random"),
            latest: document.getElementById("latest"),
            videoCount: document.getElementById("videoCount"),
            playerBoard: document.getElementById("playerBoard"),
            playerTable: document.getElementById("playerTable"),
            playerTableBody: document.getElementById("playerTableBody"),
        }
        this.addListeners()
    }

    addListeners() {
        this.elements.prev.addEventListener("click", () => this.getPrevVideo())
        this.elements.next.addEventListener("click", () => this.getNextVideo())
        this.elements.random.addEventListener("click", () => this.getRandomVideo())
        this.elements.latest.addEventListener("click", () => this.getLatestVideo())
        this.elements.playerTable.addEventListener("click", event => {
            if (event.target.classList.contains("player")) {
                this.handleClickPlayer(event)
            }
        })
    }

    async render() {
        await this.getVideoCount()
        await this.getPlayers()
        await this.getRandomVideo()
    }

    async getRandomVideo() {
        const index = getRandomNumber(this.getMaxVideoId())
        await this.getVideo(index)
    }

    async getNextVideo() {
        const index = mod(this.state.video.id + 1, this.getMaxVideoId()) + this.getMinVideoId() - 1
        await this.getVideo(index, 'next')
    }

    async getPrevVideo() {
        const index = mod(this.state.video.id - 1 - this.getMinVideoId(), this.getMaxVideoId()) + this.getMinVideoId()
        await this.getVideo(index, 'prev')
    }

    async getLatestVideo() {
        const index = this.getMaxVideoId()
        await this.getVideo(index)
    }

    getMaxVideoId() {
        return this.state.selectedPlayer.max_video_id || this.state.maxVideoId
    }

    getMinVideoId() {
        return this.state.selectedPlayer.min_video_id || this.state.minVideoId
    }

    async getVideo(index, action = null) {
        const videoData = await fetchVideo(index, this.state.selectedPlayer.id, action)
        this.elements.videoSource.src = videoData.path
        this.elements.video.load()
        this.elements.video.play()
        this.setVideoStates(videoData)
        this.updateMetaElements()
    }

    setVideoStates(videoData) {
        this.state.video = videoData
        this.state.hasPlayerRated = !!videoData.user_rating
    }

    updateMetaElements() {
        this.elements.playerDate.textContent = this.state.video.player_name + " | " + this.state.video.name.slice(-23, -4)
        this.elements.index.textContent = "[" + this.state.video.id + "/" + this.getMaxVideoId() + "]"
    }

    async getVideoCount() {
        this.state.videoCount = await fetchVideoCount(this.state.selectedPlayer.id)
        this.elements.videoCount.textContent = this.state.videoCount
    }

    handleClickPlayer(event) {
        this.selectPlayer(event.target)
        this.getRandomVideo()
        this.getVideoCount()
        this.updateMetaElements()
    }

    async getPlayers() {
        const playerList = await fetchPlayers()
        this.state.players = playerList
        this.state.maxVideoId = Math.max(...playerList.map(item => item.max_video_id));
        this.state.minVideoId = Math.min(...playerList.map(item => item.min_video_id));
        this.updatePlayerBoard()
    }

    updatePlayerBoard() {
        this.elements.playerTableBody.innerHTML = "";
        this.state.players.forEach(item => {
            const tr = document.createElement('tr');
            const playerCell = document.createElement('td')

            playerCell.textContent = item["name"]
            playerCell.id = "player-"+item["name"]
            playerCell.classList = "player clickableText"

            tr.appendChild(playerCell)
            this.elements.playerTableBody.appendChild(tr);
        });
    }

    selectPlayer(playerElement) {
        document.getElementById(this.state.selectedPlayer.elementId).classList.remove("selectedPlayer")
        let player = null
        if (playerElement.textContent === "All") {
            player = {
                id: null,
                name: "All", 
            }
        } else {
            player = this.state.players.find(item => item.name === playerElement.textContent)
        }
        this.state.selectedPlayer = { ...player, elementId: playerElement.id}
        playerElement.classList.add("selectedPlayer")
    }
}