const LOWERCASE = 'abcdefghjkmnpqrstuvwxyz'
const UPPERCASE = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
const DIGITS = '2345689'
const SPECIALS = '-_!@#$%^&*`~.()+='
const ALL = `${LOWERCASE}${UPPERCASE}${DIGITS}${SPECIALS}`

function getRandomIndex(max: number) {
  const buffer = new Uint32Array(1)
  window.crypto.getRandomValues(buffer)
  return buffer[0] % max
}

function pick(chars: string) {
  return chars[getRandomIndex(chars.length)]
}

function shuffle(values: string[]) {
  for (let index = values.length - 1; index > 0; index -= 1) {
    const target = getRandomIndex(index + 1)
    ;[values[index], values[target]] = [values[target], values[index]]
  }
  return values
}

export function generateTemporaryPassword(length = 12) {
  const size = Math.max(length, 8)
  const password = [pick(LOWERCASE), pick(UPPERCASE), pick(DIGITS), pick(SPECIALS)]

  while (password.length < size) {
    password.push(pick(ALL))
  }

  return shuffle(password).join('')
}
