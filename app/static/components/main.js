import { fetchVideo, fetchVideoCount, fetchPlayers, fetchVideoById } from "../helpers/api.js"
import { getRandomNumber, mod, updateCanonicalLinkWithUrl } from "../helpers/utils.js"
import { Ratings } from "./ratings.js"
import { Video } from "./video.js"

export class Main {
    constructor() {
        this.elements = {
            main: document.getElementById("mainContainer"),
            themeContainer: document.getElementById("themeContainer"),
            videoPosition: document.getElementById("videoPosition"),
            videoIndexCount: document.getElementById("videoIndexCount"),
            playerDate: document.getElementById("playerDate"),
            prev: document.getElementById("prev"),
            next: document.getElementById("next"),
            inOrder: document.getElementById("inOrder"),
            random: document.getElementById("random"),
            newest: document.getElementById("newest"),
            videoCount: document.getElementById("videoCount"),
            playerBoard: document.getElementById("playerBoard"),
            playerTable: document.getElementById("playerTable"),
            playerTableBody: document.getElementById("playerTableBody"),
            fullscreenButton: document.getElementById("fsButton"),
            exitFullscreenButton: document.getElementById("exitFullscreen"),
        }
        this.state = {
            videoCount: 0,
            videoMeta: {},
            selectedPlayer: {
                id: null,
                name: "All",
                elementId: "player-all"
            },
            players: [],
            iterationMode: {
                mode: "inOrder",
                elementName: "newest",
            },
            theme: "green",
        }
        this.video = new Video(() => this.handleClickNext(), () => this.handleClickPrev())
        this.ratings = new Ratings()
        this.addListeners()
    }

    addListeners() {
        this.elements.themeContainer.addEventListener("click", (e) => {
            if (e.target.dataset.color) {
                this.toggleTheme(e.target.dataset.color)
            }
        })
        this.elements.prev.addEventListener("click", () => this.handleClickPrev())
        this.elements.next.addEventListener("click", () => this.handleClickNext())
        this.elements.inOrder.addEventListener("click", () => this.handleClickInOrder())
        this.elements.random.addEventListener("click", () => this.handleClickRandom())
        this.elements.newest.addEventListener("click", () => this.handleClickNewest())
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
        await this.getLatestVideo()
        await this.handleVideoCount()
        await this.getPlayers()
        this.pushHistory()
    }

    renderWithState(state) {
        this.state = {...state}
        this.video.render(state.videoMeta)
        this.displayVideoCount()
        this.updatePlayerBoard()
        this.handleRatings(state.videoMeta)
        this.displayIndexCount()
        this.displayVideoPosition()
        this.selectPlayer(document.getElementById(state.selectedPlayer.elementId))
    }

    async renderFromUrl(videoId, player = null) {
        updateCanonicalLinkWithUrl()
        if (player !== null) {
            await this.getPlayers()
            this.selectPlayer(document.getElementById("player-"+player))
        }
        await this.getVideo(videoId, true)
        await this.handleVideoCount()

        if (player == null) {
            await this.getPlayers()
        }
        this.pushHistory(false)
    }

    toggleTheme(color) {
        document.body.classList.remove(`${this.state.theme}-theme`);
        document.body.classList.add(`${color}-theme`);
        document.getElementById(`${this.state.theme}Theme`).classList.remove("selectedTheme"),
        document.getElementById(`${color}Theme`).classList.add("selectedTheme"),
        this.state.theme = color
    }

    handleClickInOrder() {
        this.changeIterationMode("inOrder", "inOrder")
    }

    async handleClickRandom() {
        this.changeIterationMode("random", "random")
        await this.getRandomVideo()
        this.pushHistory()
    }

    async handleClickNewest() {
        this.changeIterationMode("newest", "inOrder")
        await this.getLatestVideo()
        this.pushHistory()
    }

    changeIterationMode(elementId, mode) {
        this.elements[this.state.iterationMode.elementName].classList.remove("selected")
        this.elements[elementId].classList.add("selected")
        this.state.iterationMode.mode = mode
        this.state.iterationMode.elementName = elementId
    }

    async handleClickNext() {
        const map = {
            "inOrder": () => this.getNextVideo(),
            "random": () => this.getRandomVideo()
        }
        await map[this.state.iterationMode.mode]()
        this.pushHistory()
    }

    async handleClickPrev() {
        const map = {
            "inOrder": () => this.getPrevVideo(),
            "random": () => this.getRandomVideo()
        }
        await map[this.state.iterationMode.mode]()
        this.pushHistory()
    }

    async getNextVideo() {
        const index = mod(this.state.videoMeta.position, this.state.videoCount) + 1
        await this.getVideo(index)
    }

    async getPrevVideo() {
        const index = mod(this.state.videoMeta.position - 2, this.state.videoCount) + 1
        await this.getVideo(index)
    }

    async getRandomVideo() {
        const index = getRandomNumber(this.state.videoCount)
        await this.getVideo(index)
    }

    async getLatestVideo() {
        await this.getVideo(1)
    }

    async getVideo(index, getById=false) {
        const videoData = getById ? await fetchVideoById(index, this.state.selectedPlayer.id) : await fetchVideo(index, this.state.selectedPlayer.id)
        if (videoData === null) {
            await this.getLatestVideo()
            return
        }
        this.video.render(videoData)
        this.state.videoMeta = videoData
        this.handleRatings(videoData)
        this.displayMeta()
        this.displayVideoPosition()
    }

    displayVideoPosition() {
        this.elements.videoPosition.textContent = this.state.videoMeta.position
    }

    handleRatings(videoData) {
        this.ratings.setState(
            {
                videoId: videoData.id,
                totalVideoRating: videoData.total_rating,
                avgVideoRating: videoData.average_rating,
                hasUserRated: !!videoData.user_rating,
                userRating: videoData.user_rating,
            }
        )
        this.ratings.render()
    }

    displayMeta() {
        this.elements.playerDate.textContent = this.state.videoMeta.player_name + " | " + this.state.videoMeta.name.slice(-23, -4)
    }

    async handleVideoCount() {
        await this.getVideoCount()
        this.displayVideoCount()
        this.displayIndexCount()
    }

    displayIndexCount() {
        this.elements.videoIndexCount.textContent = this.state.videoCount
    }

    async getVideoCount() {
        this.state.videoCount = await fetchVideoCount(this.state.selectedPlayer.id)
    }

    displayVideoCount() {
        this.elements.videoCount.textContent = this.state.videoCount
    }

    async handleClickPlayer(event) {
        this.selectPlayer(event.target)
        await this.handleVideoCount()
        await this.getLatestVideo()
        this.pushHistory()
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
                try {
                    await screen.orientation.lock('landscape');
                } catch (error) {
                    console.error('Error locking orientation:', error);
                }
            }
            if (!this.video.isVideoPaused()) {
                this.video.hideOverlayElements()
            }
        }
    }

    handleClickExitFullscreen() {
        if (document.fullscreenElement) {
            document.exitFullscreen()
        }
        this.video.showOverlayElements()
    }

    pushHistory(updateCanonical = true) {
        const params = this.state.selectedPlayer.id ? `?player=${this.state.selectedPlayer.name}` : ""
        history.pushState({id: Date.now(), state: this.state}, "", `/rocket-league/clip/${this.state.videoMeta.id}${params}`)
        if (updateCanonical) {
            updateCanonicalLinkWithUrl()
        }
    }
}