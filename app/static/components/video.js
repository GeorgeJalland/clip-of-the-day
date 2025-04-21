export class Video {
    constructor(getNextVideo, getPrevVideo) {
        this.state = {
            video: {},
            userHasClickedPlay: false,
            controlsVisible: true,
            overlaysVisible: true,
            loading: false,
        }

        this.elements = {
            video: document.getElementById("videoElement"),
            videoSource: document.getElementById("videoSource"),
            progressBar: document.getElementById("progressBar"),
            loadingProgressBar: document.getElementById("loadingProgressBar"),
            progressContainer: document.getElementById("progressContainer"),
            customControls: document.getElementById("customControls"),
            pauseplayButton: document.getElementById("pauseplayButton"),
            loader: document.getElementById("loader"),
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
        this.elements.video.addEventListener("waiting", () => this.handleVideoWaiting());
        this.elements.video.addEventListener("playing", () => this.handleVideoPlaying());
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
            this.hideControls()
            if (document.fullscreenElement) {
                this.hideOverlayElements()
            }
        } else {
            this.showControls()
            this.showOverlayElements()
        }
        this.resetProgressBars()
    }

    resetProgressBars() {
        this.updateProgressBar(0);
        this.updateLoadingProgressBar(0);
    }

    handleVideoWaiting() {
        this.state.loading = true
        if (!this.state.controlsVisible) {
            this.showLoader()
        }
    }

    handleVideoPlaying() {
        this.state.loading = false
        this.hideLoader()
    }

    showLoader() {
        this.elements.loader.classList.remove("hidden")
    }

    hideLoader() {
        this.elements.loader.classList.add("hidden");
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
                this.tempShowOverlayElements()
            }
        }
    }

    tempShowControls() {
        if (this.state.controlsVisible) {
            this.hideControls()
        } else {
            this.showControls()
            if (this.state.loading) {
                this.hideLoader()
            }
            this.hideControlsTimeout = setTimeout(() => {
                this.hideControls()
                if (this.state.loading) {
                    this.showLoader()
                }
            }, 2500);
        }
    }

    showControls() {
        clearTimeout(this.hideControlsTimeout);
        this.elements.customControls.classList.add("visible");
        this.state.controlsVisible = true;
    }

    hideControls() {
        clearTimeout(this.hideControlsTimeout);
        this.elements.customControls.classList.remove("visible");
        this.state.controlsVisible = false;
    }

    tempShowOverlayElements() {
        if (this.state.overlaysVisible) {
            this.hideOverlayElements()
        } else {
            this.showOverlayElements()
            this.hideOverlayTimeout = setTimeout(() => {
                this.hideOverlayElements()
            }, 2500);
        }
    }

    showOverlayElements() {
        this.clearHideTimeout()
        this.elements.disappearingOverlays.forEach(element => {
            element.classList.remove("hidden")
        });
        this.state.overlaysVisible = true;
    }

    hideOverlayElements() {
        this.clearHideTimeout()
        this.elements.disappearingOverlays.forEach(element => {
            element.classList.add("hidden")
        });
        this.state.overlaysVisible = false;
    }

    clearHideTimeout() {
        clearInterval(this.hideOverlayTimeout);
    }

    pauseplay() {
        if (this.state.userHasClickedPlay === false) {
            this.state.userHasClickedPlay = true;
        }
        if (this.isVideoPaused()) {
            this.elements.video.play();
            this.hideControls()
            if (document.fullscreenElement) {
                this.hideOverlayElements()
            }
        } else {
            this.elements.video.pause();
            this.showControls()
            if (document.fullscreenElement) {
                this.showOverlayElements()
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

    isVideoPaused() {
        return this.elements.video.paused
    }
}
