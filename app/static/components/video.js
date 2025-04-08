export class Video {
    constructor() {
        this.state = {
            video: {},
            userHasClickedPlay: false,
        }

        this.elements = {
            video: document.getElementById("videoElement"),
            videoSource: document.getElementById("videoSource"),
            progressBar: document.getElementById("progressBar"),
            customControls: document.getElementById("customControls"),
            pauseplayButton: document.getElementById("pauseplayButton"),
        }
        this.hideControlsTimeout = null;
        this.addListeners()
    }

    addListeners() {
        this.elements.video.addEventListener("timeupdate", () => this.updateProgressBar());
        this.elements.video.addEventListener("click", () => this.handleClickVideo())
        this.elements.pauseplayButton.addEventListener("click", () => this.pauseplay())
    }

    setState(newState) {
        this.state = {...this.state, ...newState}
    }

    render(videoData) {
        this.state.video = videoData
        this.elements.videoSource.src = videoData.path
        this.elements.video.load()
        if (this.userHasClickedPlay) {
            this.elements.video.play()
        } else {
            this.elements.customControls.classList.add("visible");
            this.userHasClickedPlay = true;
        }
        this.resetProgressBar()
    }

    updateProgressBar() {
        const percent = (this.elements.video.currentTime / this.elements.video.duration) * 100;
        this.elements.progressBar.style.width = percent + "%";
    }

    resetProgressBar() {
        this.elements.progressBar.style.width = "0%";
    }

    handleClickVideo() {
        if (!this.elements.video.paused) {
            this.tempShowControlsAndMeta()
        }
    }

    tempShowControlsAndMeta() {
        this.elements.customControls.classList.add("visible");
        clearTimeout(this.hideControlsTimeout);
        this.hideControlsTimeout = setTimeout(() => {
            this.elements.customControls.classList.remove("visible");
        }, 2000);
    }

    pauseplay() {
        if (this.elements.video.paused) {
            this.elements.video.play();
            this.elements.customControls.classList.remove("visible");
        } else {
            this.elements.video.pause();
            clearTimeout(this.hideControlsTimeout);
            this.elements.customControls.classList.add("visible");
        }
    }
}
