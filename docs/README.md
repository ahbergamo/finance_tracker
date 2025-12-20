# Documentation Development

This directory contains the FRacker documentation built with MkDocs Material.

## Quick Start

### Serve Locally

```bash
mkdocs serve
```

Or use the VSCode task: **Terminal → Run Task → MkDocs: Serve Locally**

Visit [http://localhost:8000](http://localhost:8000) to view the docs. Changes auto-reload!

### Deploy to GitHub Pages

```bash
mkdocs gh-deploy --clean
```

Or use the VSCode task: **Terminal → Run Task → MkDocs: Deploy to GitHub Pages**

This will:
1. Build the static site
2. Create/update the `gh-pages` branch
3. Push to GitHub
4. Docs will be live at: https://ahbergamo.github.io/finance_tracker/

## Quick Reference

### Common Commands

| Command | Description |
|---------|-------------|
| `mkdocs serve` | Start dev server (localhost:8000) |
| `mkdocs build` | Build static site to ./site/ |
| `mkdocs build --clean` | Clean build (removes old files) |
| `mkdocs gh-deploy --clean` | Deploy to GitHub Pages |
| `mkdocs --help` | Show all available commands |

### Common Development Tasks

| Task | VSCode Shortcut |
|------|-----------------|
| **Flask: Clean SQLite DB** | `Ctrl+Shift+P` → Run Task |
| **Flask: DB Init** | `Ctrl+Shift+P` → Run Task |
| **Flask: DB Migrate** | `Ctrl+Shift+P` → Run Task |
| **Flask: DB Upgrade** | `Ctrl+Shift+P` → Run Task |
| **Flask: Seed DB** | `Ctrl+Shift+P` → Run Task |
| **Flask Dev All** | `Ctrl+Shift+P` → Run Task (full reset) |
| **Lint Code** | `Ctrl+Shift+P` → Run Task |
| **Run Pytest with Coverage** | `Ctrl+Shift+P` → Run Task |
| **Clean Local** | `Ctrl+Shift+P` → Run Task (remove __pycache__) |

## VSCode Tasks

All available documentation tasks (MkDocs is pre-installed in the devcontainer):

| Task | Description | Shortcut |
|------|-------------|----------|
| **MkDocs: Serve Locally** | Start dev server at localhost:8000 | `Ctrl+Shift+P` → Run Task |
| **MkDocs: Build Site** | Build static site to `./site/` | `Ctrl+Shift+P` → Run Task |
| **MkDocs: Deploy to GitHub Pages** | Deploy to gh-pages branch | `Ctrl+Shift+P` → Run Task |
| **MkDocs: Open Local Docs** | Start server and open in browser | `Ctrl+Shift+P` → Run Task |

## Documentation Structure

```
docs/
├── index.md                    # Homepage
├── getting-started/            # Installation & setup guides
│   ├── quick-start.md
│   ├── raspberry-pi.md
│   ├── development.md
│   └── configuration.md
├── user-guide/                 # User documentation
│   ├── dashboard.md
│   ├── importing-transactions.md
│   ├── categories-budgets.md
│   ├── reports.md
│   ├── account-types.md
│   └── import-rules.md
├── admin-guide/                # Admin/deployment docs
│   └── (to be added)
├── development/                # Developer documentation
│   └── (to be added)
├── design/                     # Design documents
│   ├── index.md
│   ├── retirement-accounts.md
│   └── asset-tracking.md
├── assets/
│   └── screenshots/           # Images for documentation
├── changelog.md               # Symlink to ../CHANGELOG.md
└── contributing.md            # Symlink to ../CONTRIBUTING.md
```

## Writing Documentation

### Markdown Features

MkDocs Material supports:

- **Admonitions** (notes, tips, warnings)
- **Code blocks** with syntax highlighting
- **Tabbed content**
- **Tables**
- **Images** with captions
- **Internal links**
- **Mermaid diagrams** (if enabled)

### Admonition Examples

```markdown
!!! note "Optional Title"
    This is a note

!!! tip
    This is a tip

!!! warning
    This is a warning

!!! danger
    This is a danger notice
```

### Code Blocks

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### Images

```markdown
![Alt Text](assets/screenshots/image.png)

Or with caption:
<figure markdown>
  ![Alt Text](assets/screenshots/image.png){ width="600" }
  <figcaption>Image caption here</figcaption>
</figure>
```

### Internal Links

```markdown
[Link to another page](../getting-started/quick-start.md)
[Link to section](../getting-started/quick-start.md#step-1-download)
```

## Testing Changes

1. Run `mkdocs serve`
2. Make changes to `.md` files
3. Browser auto-refreshes with changes
4. Check for broken links or formatting issues
5. Build with `mkdocs build` to check for errors

## Deployment Workflow

1. **Develop locally** - Make changes and test with `mkdocs serve`
2. **Commit changes** - Commit documentation updates to your branch
3. **Merge to develop** - PR and merge to develop branch
4. **Deploy** - Run `mkdocs gh-deploy` from develop or main branch
5. **Verify** - Check https://ahbergamo.github.io/finance_tracker/

## Configuration

Documentation configuration is in `mkdocs.yml` at the project root.

Key settings:
- **theme**: Material theme configuration
- **nav**: Navigation structure
- **plugins**: Search, lightbox, etc.
- **markdown_extensions**: Enhanced markdown features

## Adding Pages

1. Create new `.md` file in appropriate directory
2. Add to navigation in `mkdocs.yml`:

```yaml
nav:
  - User Guide:
      - Dashboard: user-guide/dashboard.md
      - New Page: user-guide/new-page.md  # Add here
```

3. Test with `mkdocs serve`
4. Commit and deploy

## Troubleshooting

### "mkdocs: command not found"

Install dependencies:
```bash
pip install -r requirements-docs.txt
```

### Changes not appearing

- Hard refresh browser (Ctrl+F5)
- Check file is saved
- Check for syntax errors in terminal

### Build errors

Common issues:
- Broken internal links
- Missing images
- YAML syntax errors in mkdocs.yml
- Markdown formatting issues

Check the terminal output for specific errors.

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
