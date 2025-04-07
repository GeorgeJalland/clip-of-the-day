export class Video {
    constructor() {
        this.state = {
            video: {},
        }

        this.elements = {
            video: document.getElementById("videoElement"),
            videoSource: document.getElementById("videoSource"),
        }
        this.addListeners()
    }

    addListeners() {
    }

    setState(newState) {
        this.state = {...this.state, ...newState}
    }

    render(videoData) {
        this.state.video = videoData
        this.elements.videoSource.src = videoData.path
        this.elements.video.load()
        this.elements.video.play()
    }
}
