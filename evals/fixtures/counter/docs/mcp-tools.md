# Quillstack MCP tools

| Tool | Arguments | Behavior |
| --- | --- | --- |
| `list_pages` | `{ folder?, cursor?, limit? }` | Lists page paths and titles in a folder. Default 20 per page. |
| `read_page` | `{ path }` | Returns the page's Markdown. |
| `write_page` | `{ path, content }` | Creates or replaces one page. |
| `edit_page` | `{ path, old_string, new_string }` | Replaces one unique exact string in one page. |
| `delete_pages` | `{ paths[] }` | Moves the listed pages to Trash. The list must be nonempty. |
