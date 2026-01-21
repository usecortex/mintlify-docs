import { useEffect, useState } from 'react'

export const TableOfContents = ({
  title = 'On this page',
  items,
  minHeadingLevel = 2,
  maxHeadingLevel = 3,
  className = '',
  activeClassName = 'text-primary dark:text-primary-light border-primary dark:border-primary-light hover:border-primary dark:hover:border-primary-light',
  inactiveClassName = 'hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-300',
}) => {
  const [toc, setToc] = useState(items ?? [])
  const [activeId, setActiveId] = useState('')

  // Build TOC from document headings if items are not provided
  useEffect(() => {
    if (items && items.length) return
    if (typeof document === 'undefined') return

    const selectors = []
    for (let lvl = minHeadingLevel; lvl <= maxHeadingLevel; lvl++) {
      selectors.push(`h${lvl}`)
    }

    const nodes = Array.from(document.querySelectorAll(selectors.join(',')))
      .filter((el) => el.id)

    const built = []
    let currentTop = null

    nodes.forEach((el) => {
      const level = Number(el.tagName.slice(1))
      const node = {
        id: el.id,
        label: el.textContent.trim(),
        href: `#${el.id}`,
        children: [],
      }

      if (level === minHeadingLevel) {
        built.push(node)
        currentTop = node
      } else if (level > minHeadingLevel && currentTop) {
        currentTop.children.push(node)
      } else {
        built.push(node)
      }
    })

    setToc(built)
  }, [items, minHeadingLevel, maxHeadingLevel])

  // Track active section using hash and intersection observer
  useEffect(() => {
    if (typeof document === 'undefined') return

    const applyHash = () => {
      const h = window.location.hash.replace('#', '')
      if (h) setActiveId(h)
    }
    applyHash()

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id)
          }
        })
      },
      { rootMargin: '0px 0px -70% 0px', threshold: 0.1 }
    )

    const ids = toc.flatMap((i) => [i, ...(i.children ?? [])]).map((i) => i.id)
    ids.forEach((id) => {
      const el = document.getElementById(id)
      if (el) observer.observe(el)
    })

    window.addEventListener('hashchange', applyHash)
    return () => {
      window.removeEventListener('hashchange', applyHash)
      observer.disconnect()
    }
  }, [toc])

  const Item = ({ node, depth = 0 }) => {
    const isActive = activeId === node.id
    return (
      <li className="toc-item relative ml-6" data-depth={depth}>
        <a
          href={node.href}
          className={`py-1 block font-medium ${isActive ? activeClassName : inactiveClassName}`}
          style={depth > 0 ? { marginLeft: `${depth}rem` } : {}}
          onClick={() => setActiveId(node.id)}
        >
          {node.label}
        </a>
        {node.children && node.children.length > 0 && (
          <>
            {node.children.map((child) => (
              <Item node={child} depth={depth + 1} key={child.href} />
            ))}
          </>
        )}
      </li>
    )
  }

  const data = toc && toc.length ? toc : items || []

  return (
    <div className={`text-gray-600 text-sm leading-6 w-[18rem] pb-4 -mt-10 pt-10 hidden xl:block ${className}`} id="table-of-contents-custom">
      <ul id="table-of-contents-custom-content" className="toc">
        <li className="toc-item relative">
          <div className="text-gray-700 dark:text-gray-300 font-medium flex items-center space-x-2 py-1">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" xmlns="http://www.w3.org/2000/svg" className="h-3 w-3">
              <path d="M2.44434 12.6665H13.5554" strokeLinecap="round" strokeLinejoin="round"></path>
              <path d="M2.44434 3.3335H13.5554" strokeLinecap="round" strokeLinejoin="round"></path>
              <path d="M2.44434 8H7.33323" strokeLinecap="round" strokeLinejoin="round"></path>
            </svg>
            <span>{title}</span>
          </div>
        </li>
        {data.map((node) => (
          <Item node={node} key={node.href} />
        ))}
      </ul>
    </div>
  )
}
