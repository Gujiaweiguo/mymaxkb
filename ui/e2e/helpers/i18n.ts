function escapeRegex(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

export function exactText(...labels: string[]) {
  return new RegExp(`^(?:${labels.map(escapeRegex).join('|')})$`)
}
