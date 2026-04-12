export const socket = (url: string) => {
  let protocol = 'ws://'
  if (window.location.protocol === 'https:') {
    protocol = 'wss://'
  }

  let uri = protocol + window.location.host + url
  if (!import.meta.env.DEV) {
    uri = protocol + window.location.host + import.meta.env.VITE_BASE_PATH + url
  }
  return new WebSocket(uri)
}
