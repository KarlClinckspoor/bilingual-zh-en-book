# Story catalogue

All texts, every level. Each folder holds the source (`.zhb`, the file to edit), the generated
`.jsonl` and the finished PDF (Chinese on the left page, English on the right).

Download a whole level at once from the repository's **Releases** page.

| # | level | 中文 | English | themes | hanzi |
|---|---|---|---|---|---|
| 01 | [HSK 4](hsk4/) | [中国茶](hsk4/01-tea/01-tea.pdf) | Tea in China | culture & daily life | 2,262 |
| 02 | [HSK 4](hsk4/) | [中国各地的饮食](hsk4/02-regional-food/02-regional-food.pdf) | Food Across China | culture & daily life | 2,065 |
| 03 | [HSK 4](hsk4/) | [汉字的故事](hsk4/03-chinese-characters/03-chinese-characters.pdf) | How Chinese Characters Work | language | 2,372 |
| 04 | [HSK 4](hsk4/) | [城市里的一天](hsk4/04-a-day-in-the-city/04-a-day-in-the-city.pdf) | A Day in a Chinese City | culture & daily life | 1,980 |
| 05 | [HSK 4](hsk4/) | [长城：传说与事实](hsk4/05-great-wall/05-great-wall.pdf) | The Great Wall: Myth and Fact | history | 2,291 |
| 06 | [HSK 4](hsk4/) | [中国人的名字和称呼](hsk4/06-names-and-family/06-names-and-family.pdf) | Chinese Names and Family Terms | language · culture & daily life | 2,342 |
| 07 | [HSK 4](hsk4/) | [二十四节气](hsk4/07-solar-terms/07-solar-terms.pdf) | The 24 Solar Terms | nature & environment · tradition & ideas | 2,228 |
| 08 | [HSK 4](hsk4/) | [3D打印是怎么工作的](hsk4/08-3d-printing/08-3d-printing.pdf) | How 3D Printing Works | science & technology | 2,208 |
| 09 | [HSK 4](hsk4/) | [四大发明](hsk4/09-four-great-inventions/09-four-great-inventions.pdf) | The Four Great Inventions | history · science & technology | 1,965 |
| 10 | [HSK 4](hsk4/) | [三国的故事](hsk4/10-three-kingdoms/10-three-kingdoms.pdf) | The Three Kingdoms | history | 2,676 |
| 11 | [HSK 4](hsk4/) | [秦始皇](hsk4/11-qin-shi-huang/11-qin-shi-huang.pdf) | Qin Shi Huang | history | 2,711 |

**HSK 5** (stories 12–21) are in preparation. See [hsk5/](hsk5/).

## Themes

`culture & daily life` · `history` · `language` · `nature & environment` · `science & technology` ·
`tradition & ideas` · `society`

## Adding a story

1. Create `hskN/NN-slug/NN-slug.zhb`. Numbers continue across levels (the next free one), so a number
   always means the same text.
2. Build it (`zhb2jsonl.py`, `validate.py`, `hsk_report.py`, `make_book.py`; see the main README).
3. Add a row here and in `hskN/README.md`.

All texts are CC BY 4.0. See [../LICENSE-TEXTS](../LICENSE-TEXTS).
