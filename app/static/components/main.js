import { fetchVideo, fetchVideoCount } from "../helpers/api.js"
import { getRandomNumber, mod } from "../helpers/utils.js"
import { PlayerBoard } from "./playerboard.js"

export class Main {
    constructor() {
        this.state = {
            video: null,
            player: null,
            hasPlayerRated: false,
            videoCount: 0,
        }

        this.elements = {
            main: document.getElementById("main"),
            video: document.getElementById("videoElement"),
            index: document.getElementById("videoIndex"),
            playerDate: document.getElementById("playerDate"),
            videoSource: document.getElementById("videoSource"),
            playerBoard: document.getElementById("playerBoard"),
            ratings: document.getElementById("ratings"),
            prev: document.getElementById("prev"),
            next: document.getElementById("next"),
            random: document.getElementById("random"),
            latest: document.getElementById("latest"),
            videoCount: document.getElementById("videoCount"),
        }

        this.playerBoard = new PlayerBoard()
        this.addListeners()
    }

    addListeners() {
        this.elements.prev.addEventListener("click", () => this.getPrevVideo())
        this.elements.next.addEventListener("click", () => this.getNextVideo())
        this.elements.random.addEventListener("click", () => this.getRandomVideo())
        this.elements.latest.addEventListener("click", () => {})
    }

    async render() {
        await this.getVideoCount()
        await this.getRandomVideo()
        await this.playerBoard.render()
    }

    async getRandomVideo() {
        const index = getRandomNumber(this.state.videoCount)
        await this.getVideo(index)
    }

    async getNextVideo() {
        const index = mod(this.state.video.id, this.state.videoCount) + 1
        await this.getVideo(index)
    }

    async getPrevVideo() {
        const index = mod(this.state.video.id - 2, this.state.videoCount) + 1
        await this.getVideo(index)
    }

    async getVideo(index) {
        const videoData = await fetchVideo(index)
        this.elements.videoSource.src = videoData.path
        this.elements.video.load()
        this.elements.video.play()
        this.setVideoStates(videoData)
        this.updateMetaElements()
    }

    setVideoStates(videoData) {
        this.state.video = videoData
        this.state.hasPlayerRated = !!videoData.user_rating
        this.state.player = videoData.player_name
    }

    updateMetaElements() {
        this.elements.playerDate.textContent = this.state.player + " | " + this.state.video.name.slice(-23, -4)
        this.elements.index.textContent = "[" + this.state.video.id + "/" + this.state.videoCount + "]"
    }

    async getVideoCount() {
        this.state.videoCount = await fetchVideoCount()
    }

}