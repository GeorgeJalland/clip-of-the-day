import { fetchVideo, fetchVideoCount } from "./api.js"
import { getRandomNumber, mod } from "./utils.js"

export class Main {
    constructor() {
        this.state = {
            videoId: null,
            player: null,
            hasPlayerRated: false,
            userRating: null,
            avgRating: 0,
            totalRating: 0,
            videoCount: 0,
            videoTitle: "",
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

        console.log(this.elements.next)

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
    }

    async getRandomVideo() {
        const index = getRandomNumber(this.state.videoCount)
        await this.getVideo(index)
    }

    async getNextVideo() {
        const index = mod(this.state.videoId, this.state.videoCount) + 1
        await this.getVideo(index)
    }

    async getPrevVideo() {
        const index = mod(this.state.videoId - 2, this.state.videoCount) + 1
        await this.getVideo(index)
        console.log(this.state.videoId)
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
        this.state.videoId = videoData.id
        this.state.hasPlayerRated = !!videoData.user_rating
        this.state.userRating = videoData.user_rating
        this.state.avgRating = videoData.avg_rating
        this.state.totalRating = videoData.total_rating
        this.state.player = videoData.player
        this.state.videoTitle = videoData.video_name
    }

    updateMetaElements() {
        this.elements.playerDate.textContent = this.state.player + " | " + this.state.videoTitle.slice(-23, -4)
        this.elements.index.textContent = "[" + this.state.videoId + "/" + this.state.videoCount + "]"
    }

    async getVideoCount() {
        this.state.videoCount = await fetchVideoCount()
    }

}