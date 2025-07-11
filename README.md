# Blog to Wiki Demo

A demonstration of converting a blog to a wiki using AI.

LLM models are used for AI and MkDocs for the wiki.

The example blog used is https://jouninlappujuoksut.blogspot.com/ (blogspot.com) and the result is rendered to https://emick.github.io/blog-to-wiki-demo/

## Setup

1. Clone this repository
2. Install pipx: `pip install pipx` 
3. Install uv: `pipx install uv` 

## Local development

To run the site locally:

```bash
uv run mkdocs serve
```

This will start a local server.

## Convert blog to wiki

```bash
# Download blog
uv run 1-download-blog.py

# Create Table of Contents
uv run --env-file .env 2-create-table-of-contents.py

# Manually validate and edit table-of-contents.txt

# Convert to wiki
uv run 3-convert-to-wiki.py

# Publish to github pages
git commit -am 'Publish changes'
```

The resulting wiki can be found in https://emick.github.io/blog-to-wiki-demo/

## GitHub Pages notes

- Repository must be public
- Pages must be activated in classic mode and `gh-pages` branch selected with root folder as source.

## License

See the [LICENSE](LICENSE) file for details.
