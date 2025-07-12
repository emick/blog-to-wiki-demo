import os
import re
import glob
import click
from openai import OpenAI


BLOG_DIR = "blog"
TOC_FILE = 'table-of-contents.txt'

def summary_prompt(texts: str):
    return f"""<writings>
{texts}
</writings>

You are a summarizer. You summarize everything from above writings related to given topic. You summarize all events, all that has happened related to the person, place or whatever given as a topic. Write events in chronological order. Follow extra instructions when given.

Present the events in a purely objective manner, without subjective commentary or evaluative language. Please avoid phrases such as 'Her role is significant, because she ...' Instead, just describe the actions and events as they occur, leaving any interpretation of significance up to the reader.

Write the summary in finnish.
"""

def markdown_prompt(table_of_contents: str):
    return f"""You are a text converter. You convert given text to mkdocs compatible markdown.

Rules:
  - Do not add comments or anything extra, just produce the markdown.
  - Do not makeup any information. Just use what you are given in <summary> and verify that
  - Do not include <summary> or </summary> in the response
  - Avoid h2-6 headings (## / ### / ...) with short text
  - Don't surround the answer with code tags ```. The output must be a standalone mkdocs markdown page
  - Do not write that a place or person is only mentioned once in texts
  - Do not mention when person or place was first or last time mentioned
  - Present the events in a purely objective manner, without subjective commentary or evaluative language
  - Link to other pages generously, but just once per other page (just like wikipedia)
  - Do not link to the current page
  - Write in finnish
  - Use the below file tree to determine relative paths

<toc>
{table_of_contents}
</toc>

E.g. If you are writing Paikat/Suomi/Espoo.md then a link to Suolatabletit would be [Suolatabletit](../../Huolto ja ravinto/Suolatabletit.md).
"""

def sources_prompt(texts: str):
    return f"""<blog-content>
{texts}
</blog-content>

Your job is to evaluate given text and find all texts from <blog-content> that are sources for it.

The link to the text is in the text's h1 header and the text is below the header.

List the references like this:

```
## Lähteet

- [title](link)
- [title](link)
```

for example:

```
## Lähteet

- [NUTS Karhunkierros 80 (26.5.2018)](https://jouninlappujuoksut.blogspot.com/2018/07/nuts-karhunkierros-80-2652018.html)
- [Tenerife bluetrail 110](https://jouninlappujuoksut.blogspot.com/2025/03/tenerife-bluetrail-110.html)
- [Transgrancanaria Classic (126 km, noin 6500 D+) Never again, yeah right](https://jouninlappujuoksut.blogspot.com/2024/02/transgrancanaria-126-km-2024-neveragain.html)
```

Do not include the surrounding ```

Do not write anything else. No explanations.

Only include links to those writings that are actually referred."""

CLEANUP_PROMPT = f"""Your job is to cleanup unwanted texts from given text.

Rules:

  - Do not add or invent any new links
  - Present the events in a purely objective manner, without subjective commentary or evaluative language
  - Include taivutus inside the visible text. Do `[Espoossa](../Paikat/Suomi/Espoo.md)` instead of `[Espoo](../Paikat/Suomi/Espoo.md):ssa`
  - Do not duplicate link name in parenthesis. Do `[Espoossa](../Paikat/Suomi/Espoo.md)` instead of `Espoossa ([Espoo](../Paikat/Suomi/Espoo.md))`
  - Do not write that a place or person is only mentioned once in texts
  - Do not mention when person or a place was first or last time mentioned, or that it was not mentioned afterwards

Avoid (remove) text like this:

- "Vaikka häntä ei tässä retkellä mainittu, hänen roolinsa on ollut ratkaiseva matkalla"
- "Muuta Teneriffasta ei kerrottu"
- "Vaikka tarkat tiedot Jounin aiemmista retkistä eivät ole laajalti dokumentoitu"
"""

def read_table_of_contents() -> str:
    with open(TOC_FILE, 'r', encoding='utf-8') as file:
        return file.read().strip()

def read_blog_posts() -> str:
    md_files = glob.glob(os.path.join(BLOG_DIR, "*.md"))

    file_contents = []
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]
            content = "\n".join(lines)
            content = re.sub(r'\n{3,}', '\n\n', content)
            file_contents.append(content)

    blog_content = "\n".join(file_contents)
    return blog_content

def generate_response(system_prompt: str, user_prompt: str, model: str) -> str:
    client = OpenAI()
    if model == "o4-mini":
        completion = client.chat.completions.create(
            model="o4-mini",
            reasoning_effort="high",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
    elif model == 'o3':
        completion = client.chat.completions.create(
            model="o3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
    else:
        completion = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
    return completion.choices[0].message.content

def parse_file_paths(content):
        lines = content.splitlines()
        stack = []
        paths = []
        for line in lines:
            if not line.strip():
                continue

            split_line = line.strip().split('.md', maxsplit=1)
            title = split_line[0].strip()
            comments = split_line[1].strip().lstrip('(').rstrip(')') if len(split_line) > 1 else ""

            leading = len(line) - len(line.lstrip(' '))
            depth = leading // 2
            name = line.strip()
            if name.endswith('/'):
                # directory
                dir_name = name.rstrip('/')
                # Adjust stack to depth
                stack = stack[:depth]
                stack.append(dir_name)
            elif '.md' in name:
                file_name = title + '.md'
                # Adjust stack to depth
                stack_current = stack[:depth]
                full_parts = stack_current + [file_name]
                paths.append(('wiki/' + '/'.join(full_parts), title, comments))
            else:
                raise Exception(f"Non ToC line: {line}")

        return paths

def handle_file(output_path, title, comments, blog_content, table_of_contents):
    extra_instructions = f"Extra instructions: {comments}." if comments else ''
    summary = generate_response(summary_prompt(blog_content), f"Given topic is: {title}. {extra_instructions}", model='o3')
    click.echo("SUMMARY:")
    click.echo(summary)

    cleaned_up = generate_response(CLEANUP_PROMPT, summary, model='o3')
    click.echo("CLEANED UP:")
    click.echo(cleaned_up)

    response = generate_response(f"""{markdown_prompt(table_of_contents)}\n\nStart the document with the following markdown front matter and h1 header:
        
        ```
        ---
        title: {title}
        ---
        
        # {title}
        ```
        
        Write the rest of the document based on information inside <summary> tag.
        
        Current path is {output_path.lstrip('wiki/')}. Use it for relative paths""", f"""<summary>\n{cleaned_up}\n</summary>)""", model='o4-mini')
    click.echo("RESPONSE:")
    click.echo(response)

    sources = generate_response(sources_prompt(blog_content), summary, model='o4-mini')
    click.echo("SOURCES:")
    click.echo(sources)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        if sources != '':
            file.write(response + "\n\n" + sources)
        else:
            file.write(response)

    click.echo(f"Response saved to {output_path}")

@click.command()
@click.option("--file", "file_path", default=None, help="Process only the given file (must end with .md)")
@click.option("--only-toc", is_flag=True, help="Print only table of contents")
def main(file_path: str, only_toc: bool):
    table_of_contents = read_table_of_contents()
    files_and_comments = parse_file_paths(table_of_contents)

    if only_toc:
        for entry in files_and_comments:
            print(entry)
        exit(0)

    blog_content = read_blog_posts()

    if file_path:
        files_and_comments = [
            item for item in files_and_comments if item[0] == file_path
        ]
        if not files_and_comments:
            click.echo(f"File {file_path} not found in table of contents.")
            exit(1)

    for output_path, title, comments in files_and_comments:
        handle_file(output_path, title, comments, blog_content, table_of_contents)


if __name__ == "__main__":
    main()
