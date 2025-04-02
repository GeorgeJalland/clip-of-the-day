
import { fetchPlayers } from "../helpers/api.js"

export class PlayerBoard {
    constructor() {
        this.state = {
            players: [],
            selectedPlayer: {
                name: "All",
                id: "player-all"
            },
        }

        this.elements = {
            main: document.getElementById("playerBoard"),
            table: document.getElementById("playerTable"),
            body: document.getElementById("playerTableBody"),
        }

        this.addListeners()
    }

    addListeners() {
        this.elements.table.addEventListener("click", event => {
            if (event.target.classList.contains("player")) {
                this.handleClickPlayer(event)
            }
        })
    }

    handleClickPlayer(event) {
        this.selectPlayer(event.target)
        // need to fetch new video at this point, do i need to pass down some method
        // from main.js?
        // need the get video methods to take player arg
    }

    async render() {
        await this.getPlayers()
    }

    async getPlayers() {
        const playerList = await fetchPlayers()
        this.updatePlayerBoard(playerList)
    }

    updatePlayerBoard(playerList) {
        this.elements.body.innerHTML = "";
        playerList.forEach(item => {
            const tr = document.createElement('tr');
            const playerCell = document.createElement('td')

            playerCell.textContent = item["player"]
            playerCell.id = "player-"+item["player"]
            playerCell.classList = "player"

            tr.appendChild(playerCell)
            this.elements.body.appendChild(tr);
        });
    }

    selectPlayer(playerElement) {
        document.getElementById(this.state.selectedPlayer.id).classList.remove("selectedPlayer")
        this.state.selectedPlayer = {
            name: playerElement.textContent,
            id: playerElement.id
        }
        playerElement.classList.add("selectedPlayer")
    }


}