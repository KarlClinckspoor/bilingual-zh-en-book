# HSK 1, 2, 3 and 6 stories (22–61): review notes before release

All 40 stories pass `validate.py --annotate-above <level>` with 0 errors. Two deliberate pinyin WARNs
remain (see below).
- **HSK 1–2:** every story is at **100 %** in `hsk_report.py --target <level>` (names excluded), and
  only N kinds are used. The PDFs are built with `--annotate-above <level> --annotate-kinds N`, so
  names are the only footnotes. The title page says "Footnotes mark names and words above HSK n".
- **HSK 3:** 93.7–98.6 %.
- **HSK 6:** 95.8–99.5 %.

The items below are for a human reviewer: a native speaker and a fact-checker.

## Facts to verify
| story | claim | how the text hedges it |
|---|---|---|
| 30 | Xi'an–Beijing train 8:00–13:00 | loose, no train type named |
| 33 | 1980s Beijing–Xi'an train "a day and a night"; today 4½ hours | — |
| 37 | Yangtze 六千三百多公里, Yellow River 五千四百多公里, both rise in Qinghai | 大约 is L3, so "多" is used |
| 44 | old Leifeng Pagoda fell 1924, rebuilt 2002 | "曾经倒过"; several endings of the legend mentioned |
| 46 | 两千多万辆 shared bikes nationwide around 2017 | 据说 |
| 47 | Yangtze fishing ban from 1 Jan 2020 in "many parts" (full main stream 2021); porpoise ~1,000+ | 听说 / 大约 |
| 48 | Weifang kite festival every April since 1984; 世界风筝都 | — |
| 52 | dates of arrest, Huangzhou years, 定风波 (1082), the Red Cliff odes; 东坡肉 legend; Red Cliff probably not the battle site | legends marked 据说 / 传说 |
| 53 | ~490 decorated caves, earliest ~366 AD, "25 km of murals", Digital Dunhuang online ~2016 | 据说 / 大约 / 有人算过 |
| 54 | survival under 5 % (1962) / 8 % (1963); 马蹄坑 1964 "over 500 mu, over 90 %" (not hedged); 1977 freezing rain; cover ~11 % → 80 %+; UN award 2017 | mostly 大约 / 据说 |
| 54 | fire-tower report every 15 minutes (fictional son's routine) | not hedged |
| 55 | AlphaGo–Lee 2016 (4–1, move 37 in game 2, Lee's move 78 in game 4); Ke Jie 2017 (3–0); Lee retired 2019; Go "4,000 years" | 据说 for age and for Ke Jie's tears |
| 56 | 2020 article on riders "困在系统里"; 2021 guidance against the "strictest" algorithm | 据说 / 有人说; no platforms named |
| 57 | ~80 % speak Putonghua (2020); 语保工程 from 2015; 箸 kept in Wenzhou dialect | 据统计 / 据说 |
| 58 | Project 523 from 1967, Tu Youyou's team from 1969, sample 191 in Oct 1971, Nobel 2015, Nobel lecture title, "first Chinese woman to win a Nobel science prize", WHO malaria-free June 2021 | 据说 / 据报道 for details |
| 59 | Zhuangzi quotations (梦蝶, 濠梁, 无用之用, 庖丁) and their chapter attributions | tortoise, borrowing grain, Huizi's tomb marked 据说 |
| 60 | Sui canal from 605; Huai'an as grain-transport centre from mid-Ming; Tianjin–Pukou railway ~1912; Huai'an's first station early 21st c.; UNESCO 22 June 2014 | 大约 / 据说 |

## Language and labelling choices to confirm
- **WARN, 52 pork-3:** 少著水 *shǎo zhuó shuǐ*. Here 著 is the classical form of 着 *zhuó*, "to put
  in"; CC-CEDICT only has *zhù*.
- **WARN, 58 191-1:** 鼻血 *bíxiě*, the colloquial reading. CC-CEDICT has *xuè*.
- **N for language and region names at HSK 1–2:** 法语 (23), 黄土高原 (37). These are proper names
  and are footnoted.
- **27:** "我不要去医院" is tokenised 不 + 要 ("don't want"), because the word 不要 is L2.
- **35:** 马路 and 马上 are left unmarked (level-1 words), as the joke needs them read as words.
- **41:** 四声, 第三声 and 第四声 are kept as single tokens, which count as level 2 by their
  characters. Splitting them would leave 声, which is L5.
- **HSK 3:** the kinds were assigned by different writers, so they are not quite uniform. For example,
  49 tags 叔叔 and 阿姨 as J, and 48 tags 北京 as N.
- **Experiential 过:** some writers use *guo*, some *guò*. The HSK 4/5 stories are mixed too. Pick
  one and make it consistent across the series.
- **Directional complements:** neutral tone (*qǐlai, chūlai, xiàqu*), as in the HSK 4/5 house style.
  These show as INFO only.

## Process note
The stories were drafted in parallel by separate writers. Each final `.jsonl` was regenerated from its
`.zhb` and validated centrally before the PDFs were built. During drafting, two HSK 6 writers wrote to
the same scratch file name. Afterwards stories 53 and 60 were checked: neither contains the other's
text, and both have all their planned sections.
