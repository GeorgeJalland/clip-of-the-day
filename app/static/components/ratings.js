import { submitRating } from "../helpers/api.js"

export class Ratings {
    constructor() {
        this.state = {
            videoId: null,
            totalVideoRating: 0,
            avgVideoRating: 0,
            hasUserRated: false,
            userRating: null,
        }

        this.elements = {
            totalRating: document.getElementById("totalRating"),
            avgRating: document.getElementById("avgRating"),
            submitRatings: document.getElementById("submitRatings"),
            ratings: document.querySelectorAll('#submitRatings .rating'),
        }
        this.addListeners()
    }

    addListeners() {
        document.getElementById("submitRatings").addEventListener("click", (event) => {
            if (event.target.classList.contains("rating")) {
                const ratingValue = parseInt(event.target.dataset.value);
                this.handleClickRating(event.target, ratingValue, this.state.videoId)
            }
        });
    }

    render() {
        this.elements.totalRating.textContent = this.state.totalVideoRating
        const rating = this.state.avgVideoRating
        this.elements.avgRating.textContent = Number.isInteger(rating) ? rating : rating.toFixed(2);
        this.resetRatingsElements()
        if (this.state.hasUserRated) {
            this.showUserRating()
        }
    }

    handleClickRating(element, rating, videoId) {
        element.classList.add("selectedRating")
        let sibling = element.nextElementSibling;
        while (sibling) {
            sibling.classList.add("selectedRating");
            sibling = sibling.nextElementSibling;
        }
        setTimeout(() => {
            element.classList.remove("selectedRating")
            let sibling = element.nextElementSibling;
            while (sibling) {
                sibling.classList.remove("selectedRating");
                sibling = sibling.nextElementSibling;
            }
        }, 1000);
        if (this.state.hasUserRated) {
            this.updateRating(rating, videoId)
        } else {
            this.addRating(rating, videoId)
            this.state.hasUserRated = true
        }
        this.state.userRating = rating
        this.render()
    }

    addRating(rating, videoId) {
        submitRating(rating, videoId)
        let numberOfRatings = 0;
        if (this.state.totalVideoRating > 0) {
            numberOfRatings = (this.state.totalVideoRating / this.state.avgVideoRating)
        }
        this.state.totalVideoRating += rating
        this.state.avgVideoRating = this.state.totalVideoRating / (numberOfRatings + 1)
    }

    updateRating(rating, videoId) {
        submitRating(rating, videoId)
        const numberOfRatings = (this.state.totalVideoRating / this.state.avgVideoRating)
        this.state.totalVideoRating += rating - this.state.userRating
        this.state.avgVideoRating = this.state.totalVideoRating / numberOfRatings
    }

    showUserRating() {
        this.elements.ratings.forEach((ratingElement) => {
            const ratingValue = parseInt(ratingElement.dataset.value)
            if (this.state.userRating >= ratingValue) {
                ratingElement.classList.add("rated")
            } 
        })
    }

    resetRatingsElements() {
        this.elements.ratings.forEach((ratingElement) => {
            ratingElement.classList.remove("rated") 
        })
    }

    setState(newState) {
        this.state = {...this.state, ...newState}
    }
}
