import fs from 'node:fs'
import path from 'node:path'

// Helper to extract frontmatter and title from markdown file content
function getMetadata(filePath: string) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    
    // Simple frontmatter parser
    const frontmatterRegex = /^---\r?\n([\s\S]*?)\r?\n---/
    const match = content.match(frontmatterRegex)
    
    let order = 9999
    let title: string | undefined
    
    if (match) {
      const frontmatter = match[1]
      // Parse order
      const orderMatch = frontmatter.match(/^order:\s*(\d+)/m)
      if (orderMatch) {
        order = parseInt(orderMatch[1], 10)
      }
      // Parse title from frontmatter
      const titleMatch = frontmatter.match(/^title:\s*(.+)$/m)
      if (titleMatch) {
        title = titleMatch[1].trim().replace(/^['"]|['"]$/g, '')
      }
    }

    // If title not in frontmatter, look for H1
    if (!title) {
      // Remove frontmatter to avoid matching H1 inside it (though unlikely)
      const contentBody = match ? content.slice(match[0].length) : content
      const h1Match = contentBody.match(/^#\s+(.+)$/m)
      title = h1Match ? h1Match[1].trim() : path.basename(filePath, '.md')
    }

    return { title, order }
  } catch (e) {
    return {
      title: path.basename(filePath, '.md'),
      order: 9999
    }
  }
}

// Helper to recursively generate sidebar items
function getSidebarItems(rootDir: string, relativePath: string) {
  const fullPath = path.resolve(rootDir, relativePath)
  if (!fs.existsSync(fullPath)) return []

  const entries = fs.readdirSync(fullPath, { withFileTypes: true })
  
  const items: any[] = []

  for (const entry of entries) {
    const entryRelativePath = path.join(relativePath, entry.name)
    
    if (entry.isDirectory()) {
      const subItems = getSidebarItems(rootDir, entryRelativePath)
      
      // Skip empty directories
      if (subItems.length === 0) continue

      // Default metadata
      let title = entry.name
      let order = 9999
      let link: string | undefined = undefined
      
      // Check for index.md to get title, order and link
      const indexFilePath = path.join(fullPath, entry.name, 'index.md')
      if (fs.existsSync(indexFilePath)) {
        const metadata = getMetadata(indexFilePath)
        title = metadata.title
        order = metadata.order
        // Convert path separators to slashes for URL
        link = '/' + entryRelativePath.split(path.sep).join('/') + '/'
      }

      items.push({
        text: title,
        items: subItems,
        collapsed: false,
        link: link,
        order: order
      })
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      // Skip index.md as it's handled by the parent directory entry
      if (entry.name === 'index.md') continue

      const filePath = path.join(fullPath, entry.name)
      const metadata = getMetadata(filePath)
      
      // Generate link
      const linkPath = entryRelativePath.split(path.sep).join('/')
      const link = '/' + linkPath.replace(/\.md$/, '')
      
      items.push({ 
        text: metadata.title, 
        link,
        order: metadata.order 
      })
    }
  }

  // Sort items by order then text
  items.sort((a, b) => {
    if (a.order !== b.order) {
      return a.order - b.order
    }
    return a.text.localeCompare(b.text)
  })

  // Remove order property from final output
  return items.map(({ order, ...item }) => item)
}

export function getSidebar(rootDir: string, subDir: string, title: string) {
  if (title === 'Development') {
    return [
      {
        text: 'Development',
        items: [
          { text: 'Architecture', link: '/develop/architecture' },
          { text: 'Environment Setup', link: '/develop/environment' },
          { text: 'Code Standards', link: '/develop/standards/code-style' },
          { text: 'Plugin Development', link: '/develop/plugins' },
          { text: 'Core Modules', link: '/develop/modules/core' }
        ]
      }
    ]
  }

  const items = getSidebarItems(rootDir, subDir)

  return [
    {
      text: title,
      items: items,
      collapsed: false
    }
  ]
}
