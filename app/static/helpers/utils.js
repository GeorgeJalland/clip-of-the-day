export function getRandomNumber(n) {
    return Math.floor(Math.random() * n) + 1;
}

export function mod(n, m) {
    return ((n % m) + m) % m;
}

export function updateCanonicalLinkWithUrl() {
    const url = window.location.href
    let canonicalLink = document.getElementById('canonicalLink');
    canonicalLink.setAttribute("href", url);
}