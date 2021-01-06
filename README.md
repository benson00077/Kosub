# {{ Goblin Query }}

{{ Goblin Query }} is a browse-based searching engine in which one can search the subtitles from K-drama by some Korean word query.


## Website content
Following main contnets included:

- Regiser
- Log in
- Noun searching page
- Predicative searching page
- Histroy page
- Sentence book page

Following helper buttons included in searching page:

- Highlight: Highlight the query word in sentneces output.
- English: Hide or Show the translation.
- Chinese: Hide or Show the translation.
- Add-to-SentneceBook: Add the selected sentences as favorite.
- CheckBox : Select sentences
- Go-to-top: Scroll bak to top

## Usage

The site gets back the matched sentneces output when searching by Noun.
If search by Verb/Adjective, make sure to type in key word in Korean Basic Form. The engine helps to search the corresponding Conjugation Form of the word.

Basic form looks like: 하다.
Conjugation looks like: 해요 or 합니다 etc.

## Tools used in back-end

The website is built and developed using Flask and CS50 libaray(SQL included).
Pre-process of the Korean sentences (for SQL database) is implemented with the help of [KoNLPy](https://konlpy.org/en/v0.4.4/).


## Learn More: Conjugatoin Form in Korean

Predicate(Verb/Adjective) have 2 forms.
Basic Form looks like: 하다.
Conjugation Form looks like: 해요 or 합니다 etc.

Notice that 하 transform into 해 or 합 here.
It's hard to search a single word and get all it's variatio on the internet.


## Learn More: Morpheme segmentation

Pre-process of Korean sentences refered to as below functionalities:
- Analyze morphemes
- Segment by morphemes

Befor:
```bash
'공부를 합니다.'
```

After:
```bash
'공부', '를', '하', 'ㅂ니다', '.'
```

