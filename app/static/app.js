import { Main } from "./components/main.js"
import { updateCanonicalLinkWithUrl } from "./helpers/utils.js"

const pathVars = window.location.pathname.split("/")
const queryParams = new URLSearchParams(window.location.search)

const main = new Main()

if (pathVars[3]) {
    main.renderFromUrl(pathVars[3], queryParams.get("player"))
} else {
    main.render()
}

window.addEventListener('popstate', (event) => {
    console.log("popping state: ", event.state.state)
    if (event.state.id) {
        updateCanonicalLinkWithUrl()
        main.renderWithState(event.state.state)
    }
});