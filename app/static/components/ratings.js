import { submitRating } from "../helpers/api.js"

export class Ratings {
    constructor() {
        this.state = {
            videoId: null,
            totalVideoRating: 0,
            avgVideoRating: 0,
            hasPlayerRated: false,
            userRating: null,
        }

        this.elements = {
            totalRating: document.getElementById("totalRating"),
            avgRating: document.getElementById("avgRating"),
            submitRatings: document.getElementById("submitRatings"),
        }
        this.addListeners()
    }

    addListeners() {
        document.getElementById("submitRatings").addEventListener("click", (event) => {
            if (event.target.classList.contains("rating")) {
                const ratingValue = parseInt(event.target.dataset.value);
                this.postRating(ratingValue, this.state.videoId)
            }
        });
    }

    render() {
        this.elements.totalRating.textContent = this.state.totalVideoRating
        this.elements.avgRating.textContent = this.state.avgVideoRating
    }

    postRating(rating, videoId) {
        submitRating(rating, videoId)
    }

    setState(newState) {
        this.state = {...this.state, ...newState}
    }

}