import { fetchVideo, fetchVideoCount, fetchPlayers } from "../helpers/api.js"
import { getRandomNumber, mod } from "../helpers/utils.js"
import { Ratings } from "./ratings.js"
import { Video } from "./video.js"

export class Main {
    constructor() {
        this.state = {
            videoCount: 0,
            videoMeta: {},
            selectedPlayer: {
                id: null,
                name: "All",
                elementId: "player-all"
            },
            players: [],
        }

        this.elements = {
            main: document.getElementById("mainContainer"),
            index: document.getElementById("videoIndex"),
            playerDate: document.getElementById("playerDate"),
            prev: document.getElementById("prev"),
            next: document.getElementById("next"),
            random: document.getElementById("random"),
            latest: document.getElementById("latest"),
            videoCount: document.getElementById("videoCount"),
            playerBoard: document.getElementById("playerBoard"),
            playerTable: document.getElementById("playerTable"),
            playerTableBody: document.getElementById("playerTableBody"),
            fullscreenButton: document.getElementById("fsButton"),
            exitFullscreenButton: document.getElementById("exitFullscreen"),
        }
        this.video = new Video(() => this.getNextVideo(), () => this.getPrevVideo(), [this.elements.playerDate, this.elements.index, this.elements.playerBoard])
        this.ratings = new Ratings()
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
        this.elements.fullscreenButton.addEventListener("click", () => this.handleClickFullscreen())
        this.elements.exitFullscreenButton.addEventListener("click", () => this.handleClickExitFullscreen())
        document.addEventListener('fullscreenchange', () => {
            if (!document.fullscreenElement) {
              this.handleClickExitFullscreen()
            }
          });
    }

    async render() {
        await this.getVideoCount()
        await this.getPlayers()
        await this.getRandomVideo()
    }

    async getRandomVideo() {
        const index = getRandomNumber(this.state.videoCount)
        await this.getVideo(index)
    }

    async getNextVideo() {
        const index = mod(this.state.videoMeta.position, this.state.videoCount) + 1
        await this.getVideo(index)
    }

    async getPrevVideo() {
        const index = mod(this.state.videoMeta.position - 2, this.state.videoCount) + 1
        await this.getVideo(index)
    }

    async getLatestVideo() {
        await this.getVideo(1)
    }

    async getVideo(index) {
        const videoData = await fetchVideo(index, this.state.selectedPlayer.id)
        this.video.render(videoData)
        this.setVideoStates(videoData)
        this.updateMetaElements()
    }

    setVideoStates(videoData) {
        this.state.videoMeta = videoData
        this.ratings.setState(
            {
                videoId: videoData.id,
                totalVideoRating: videoData.total_rating,
                avgVideoRating: videoData.average_rating,
                hasUserRated: !!videoData.user_rating,
                userRating: videoData.user_rating,
            }
        )
    }

    updateMetaElements() {
        this.elements.playerDate.textContent = this.state.videoMeta.player_name + " | " + this.state.videoMeta.name.slice(-23, -4)
        this.elements.index.textContent = "[" + this.state.videoMeta.position + "/" + this.state.videoCount + "]"
        this.ratings.render()
    }

    async getVideoCount() {
        this.state.videoCount = await fetchVideoCount(this.state.selectedPlayer.id)
        this.elements.videoCount.textContent = this.state.videoCount
    }

    async handleClickPlayer(event) {
        this.selectPlayer(event.target)
        await this.getVideoCount()
        await this.getRandomVideo()
    }

    async getPlayers() {
        const playerList = await fetchPlayers()
        this.state.players = playerList
        this.updatePlayerBoard()
    }

    updatePlayerBoard() {
        this.elements.playerTableBody.innerHTML = "";
        this.state.players.forEach(item => {
            const tr = document.createElement('tr');
            const playerCell = document.createElement('td');
            const ratingCell = document.createElement('td');
            const totalRatingSpan = document.createElement('span');
            const imgElement = document.getElementById('ratingIcon').cloneNode();

            playerCell.textContent = item["name"]
            playerCell.id = "player-"+item["name"]
            playerCell.classList = "player clickableText padRight"

            ratingCell.classList = "flexCell"
            totalRatingSpan.textContent = item["sum_ratings"]
            ratingCell.appendChild(imgElement)
            ratingCell.appendChild(totalRatingSpan)

            tr.appendChild(playerCell)
            tr.appendChild(ratingCell)

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

    async handleClickFullscreen() {
        const fullscreenApi = this.elements.main.requestFullscreen
        || container.webkitRequestFullScreen
        || container.mozRequestFullScreen
        || container.msRequestFullscreen;
        if (!document.fullscreenElement) {
            fullscreenApi.call(this.elements.main);
            if (screen.orientation && screen.orientation.lock) {
                // Attempt to lock the orientation to landscape
                await screen.orientation.lock('landscape');
                console.log('Orientation locked to landscape');
            }
            if (!this.video.isVideoPaused()) {
                this.video.hidePassedElements()
            }
        }
    }

    handleClickExitFullscreen() {
        if (document.fullscreenElement) {
            document.exitFullscreen()
        }
        this.video.unhidePassedElements()
        this.video.clearHideTimeout()
    }
}