import fs from 'node:fs'
import path from 'node:path'

export function getSidebar(rootDir: string, subDir: string, title: string) {
  const fullPath = path.resolve(rootDir, subDir)

  if (!fs.existsSync(fullPath)) {
    return []
  }

  const files = fs.readdirSync(fullPath)
    .filter(file => file.endsWith('.md') && file !== 'index.md')
    .sort()

  const items = files.map(file => {
    const filePath = path.join(fullPath, file)
    const content = fs.readFileSync(filePath, 'utf-8')

    // Try to find first H1 header
    const match = content.match(/^#\s+(.+)$/m)
    const text = match ? match[1].trim() : file.replace('.md', '')

    // Normalize path separators to forward slashes for URLs
    const urlPath = subDir.split(path.sep).join('/')
    const link = `/${urlPath}/${file.replace('.md', '')}`

    return { text, link }
  })

  return [
    {
      text: title,
      items: items,
      collapsed: false
    }
  ]
}
