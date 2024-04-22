export class Video {
    constructor(getNextVideo, getPrevVideo, elementsToHide) {
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
        this.getNextVideo = getNextVideo
        this.getPrevVideo = getPrevVideo
        this.elementsToHide = elementsToHide
        this.hideControlsTimeout = null;
        this.addListeners()
    }

    touchStartY = 0;
    touchEndY = 0;

    addListeners() {
        this.elements.video.addEventListener("timeupdate", () => this.updateProgressBar());
        this.elements.video.addEventListener("click", () => this.handleClickVideo())
        this.elements.pauseplayButton.addEventListener("click", () => this.pauseplay())
        this.elements.video.addEventListener('touchstart', (e) => {
            if (document.fullscreenElement) {
                this.touchStartY = e.changedTouches[0].screenY;
            }
        });
        this.elements.video.addEventListener('touchend', (e) => {
            if (document.fullscreenElement) {
                this.touchEndY = e.changedTouches[0].screenY;
                this.handleSwipeGesture();
            }
        });
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
            this.elements.customControls.classList.remove("visible");
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
        if (!this.isVideoPaused()) {
            this.tempShowControls()
            if (document.fullscreenElement) {
                this.tempShowAdditionalElements()
            }
        }
    }

    tempShowControls() {
        this.elements.customControls.classList.add("visible");
        clearTimeout(this.hideControlsTimeout);
        this.hideControlsTimeout = setTimeout(() => {
            this.elements.customControls.classList.remove("visible");
        }, 2500);
    }

    tempShowAdditionalElements() {
        this.unhidePassedElements()
        this.hideAdditionalTimeout = setTimeout(() => {
            this.hidePassedElements()
        }, 2500);
    }

    pauseplay() {
        if (this.isVideoPaused()) {
            this.elements.video.play();
            this.elements.customControls.classList.remove("visible");
            if (document.fullscreenElement) {
                this.hidePassedElements()
            }
        } else {
            this.elements.video.pause();
            clearTimeout(this.hideControlsTimeout);
            clearInterval(this.hideAdditionalTimeout);
            this.elements.customControls.classList.add("visible");
            if (document.fullscreenElement) {
                this.unhidePassedElements()
            }
        }
    }

    handleSwipeGesture() {
        const swipeDistance = this.touchEndY - this.touchStartY;
        if (Math.abs(swipeDistance) < 30) return;

        if (swipeDistance > 0) {
            this.elements.video.classList.add("slide-transition")
            this.elements.video.classList.add("slide-out-down")
            this.getPrevVideo()
            setTimeout(() => {
                this.elements.video.classList.remove("slide-out-down")
                this.elements.video.classList.remove("slide-transition")
            }, 1000);
        } else {
            this.elements.video.classList.add("slide-transition")
            this.elements.video.classList.add("slide-out-up")
            this.getNextVideo()
            setTimeout(() => {
                this.elements.video.classList.remove("slide-out-up")
                this.elements.video.classList.remove("slide-transition")
            }, 500);
        }
    }

    hidePassedElements() {
        this.elementsToHide.forEach(element => {
            element.classList.add("hidden")
        });
    }

    unhidePassedElements() {
        this.elementsToHide.forEach(element => {
            element.classList.remove("hidden")
        });
    }

    clearHideTimeout() {
        clearInterval(this.hideAdditionalTimeout);
    }

    isVideoPaused() {
        return this.elements.video.paused
    }
}
