# Etusivu

Tämä on esimerkki siitä, miten blogin voi muuttaa wikiksi AI:lla.

Wiki on MkDocs-pohjainen ja tekoälynä on käytetty OpenAI:n ChatGPT o3-mallia. Wikiksi muunto maksoi $29,8e (12.7.2025, o3-hinnanalennuksen jälkeen).
Lopputulos jättää paljon toivomisen varaan, mutta prompteja viilaamalla tulosta pystyy parantamaan.

Esimerkkinä on käytetty [Jounin lappujuoksuja](https://jouninlappujuoksut.blogspot.com/) (blogspot.com).

Lähdekoodit löytyy [GitHubista](https://github.com/emick/blog-to-wiki-demo).

## Opit

- Wikin generointi on mahdollista, koska wiki on mahdollista esittää markdown-tekstimuodossa ja jatkoprosessoida MkDocsilla. 
- AI on hyvä ehdottamaan sisällysluetteloita, mutta sitä joutuu iteroimaan
- Ihmisen tarkistus on välttämätöntä eri etapeissa:
  - Sisällysluettelo on hyvä tarkistaa manuaalisesti
  - Sisällysluetteloon on hyvä lisätä lisätietoa promptiin, jotta artikkelista tulee sellainen kuin haluaa
- Sisältöä joutuu iteroimaan. Yksittäisen artikkelin uudelleengenerointi on oltava mahdollista
