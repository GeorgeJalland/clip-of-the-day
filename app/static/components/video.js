export class Video {
    constructor(getNextVideo, getPrevVideo) {
        this.state = {
            video: {},
            userHasClickedPlay: false,
        }

        this.elements = {
            video: document.getElementById("videoElement"),
            videoSource: document.getElementById("videoSource"),
            progressBar: document.getElementById("progressBar"),
            loadingProgressBar: document.getElementById("loadingProgressBar"),
            progressContainer: document.getElementById("progressContainer"),
            customControls: document.getElementById("customControls"),
            pauseplayButton: document.getElementById("pauseplayButton"),
            disappearingOverlays: document.querySelectorAll('.disappaearing.overlay'),
        }
        this.getNextVideo = getNextVideo
        this.getPrevVideo = getPrevVideo
        this.hideControlsTimeout = null;
        this.addListeners()
    }

    touchStartY = 0;
    touchEndY = 0;

    addListeners() {
        this.elements.video.addEventListener("timeupdate", () => this.updateProgressBar());
        this.elements.video.addEventListener("progress", () => this.updateLoadingProgressBar());
        this.elements.progressContainer.addEventListener("click", (e) => this.seekVideo(e));
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
        if (this.state.userHasClickedPlay) {
            this.elements.video.play()
            this.elements.customControls.classList.remove("visible");
        } else {
            this.elements.customControls.classList.add("visible");
        }
        this.resetProgressBars()
    }

    resetProgressBars() {
        this.updateProgressBar(0);
        this.updateLoadingProgressBar(0);
    }

    updateProgressBar(percent = null) {
        if (percent) {
            this.elements.loadingProgressBar.style.width = percent + "%";
            return;
        }
        const percentage = (this.elements.video.currentTime / this.elements.video.duration) * 100;
        this.elements.progressBar.style.width = percentage + "%";
    }

    updateLoadingProgressBar(percent = null) {
        if (percent) {
            this.elements.loadingProgressBar.style.width = percent + "%";
            return;
        }
        const video = this.elements.video;
        const duration = video.duration;
        if (video.buffered.length > 0 && duration > 0) {
            const bufferedEnd = video.buffered.end(video.buffered.length - 1);
            const percent = (bufferedEnd / duration) * 100;
            this.elements.loadingProgressBar.style.width = percent + "%";
        }
    }

    seekVideo(event) {
        const container = this.elements.progressContainer;
        const rect = container.getBoundingClientRect();

        const clickX = event.clientX - rect.left;
        const percent = clickX / rect.width;

        const newTime = this.elements.video.duration * percent;
        this.elements.video.currentTime = newTime;

        this.updateProgressBar(percent);
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
        this.unhideOverlayElements()
        this.hideAdditionalTimeout = setTimeout(() => {
            this.hideOverlayElements()
        }, 2500);
    }

    pauseplay() {
        if (this.state.userHasClickedPlay === false) {
            this.state.userHasClickedPlay = true;
        }
        if (this.isVideoPaused()) {
            this.elements.video.play();
            this.elements.customControls.classList.remove("visible");
            if (document.fullscreenElement) {
                this.hideOverlayElements()
            }
        } else {
            this.elements.video.pause();
            clearTimeout(this.hideControlsTimeout);
            clearInterval(this.hideAdditionalTimeout);
            this.elements.customControls.classList.add("visible");
            if (document.fullscreenElement) {
                this.unhideOverlayElements()
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

    hideOverlayElements() {
        this.elements.disappearingOverlays.forEach(element => {
            element.classList.add("hidden")
        });
    }

    unhideOverlayElements() {
        this.elements.disappearingOverlays.forEach(element => {
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
