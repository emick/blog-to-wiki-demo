import os
import re
import glob
from openai import OpenAI

BLOG_DIR = "blog"
TOC_FILE = 'table-of-contents.txt'

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

def create_toc_from_blog_posts(blog_content: str):
    system_prompt = f"""
You are a professional content organizer.

You are given a series of blog posts. Based on the blog posts, write a table of contents for a mkdocs based wiki as a file tree layout.

Create subfolders for categories. You build a folder tree of the documents for mkdocs. Write the file and folder names in finnish. Do not use any characters unsupported for file names. UTF-8 characters and spaces are allowed. Use ∕ instead of /.

For example:

Paikat/
  Suomi/
    Hetta.md
    Pallas.md
    Ylläs.md
  Treenipaikat/
Varustus/
  sauvat.md
Muu/
  ekologia.md
  mentaalipuoli.md (flow, mustat hetket, keskeytyksen rajalla, motivaatio)
  sää ja olosuhteet.md (helle, kylmät tunturituulet, loska- ja mutapaini)
  mentaalipuoli.md
  eläimet.md
Lajit/
  yö- vs päiväjuoksu.md
  kylmä- tai kuumahelvetti.md

Extend the above table of contents (including the above). Do not make yearly folders. Output only the table of contents in above form. Do not output anything else.
"""

    user_prompt = blog_content.strip()

    toc = generate_response(system_prompt, user_prompt, model='o3')
    return toc

def save_table_of_contents(toc: str):
    with open(TOC_FILE, 'w', encoding='utf-8') as f:
        f.write(toc)

def main():
    blog_content = read_blog_posts()
    toc = create_toc_from_blog_posts(blog_content)
    save_table_of_contents(toc)

if __name__ == "__main__":
    main()
