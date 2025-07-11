# Blog to Wiki Demo

A demonstration of converting a blog to a wiki using AI.

LLM models are used for AI and MkDocs for the wiki.

## Setup

1. Clone this repository

## Local Development

To run the site locally:

```bash
uv run mkdocs serve
```

This will start a local server.

## Test run

```bash
# Download blog
uv run download-blog.py

# Convert to wiki
uv run convert-to-wiki.py
```

## License

See the [LICENSE](LICENSE) file for details.
