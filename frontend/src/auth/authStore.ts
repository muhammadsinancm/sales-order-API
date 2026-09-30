export function setAccessToken(token: string) {
    localStorage.setItem('access_token', token)
}

export function getAccessToken() {
    return localStorage.getItem('access_token')
}

export function setRefreshToken(token: string) {
    localStorage.setItem('refresh_token', token)
}

export function getRefreshToken() {
    return localStorage.getItem('refresh_token')
}

export function clearToken() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
}