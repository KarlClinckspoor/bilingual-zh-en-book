# HSK 5 stories: review notes before release

All ten stories pass `validate.py --annotate-above 5`: 0 errors, and one deliberate warning (story 18,
see below). They also all score ≥ 95 % at HSK ≤ 5 in `hsk_report.py --target 5`. The items below are
for a human reviewer, a native speaker and a fact-checker, before the `hsk5-v1.0` release.

## Facts to verify
| story | paragraph | claim | how the text hedges it |
|---|---|---|---|
| 12 | watch section | 1970s: a watch cost 100+ yuan, a monthly wage was 30–40 yuan | 据说 |
| 13 | ships, fleet | fleet of 60+ large ships (maybe 100+), about 27,000 people, treasure ships 44 × 18 zhang | 据说 / 大约, plus modern doubts stated |
| 13 | departure | fourth voyage given as 1413 (it may have left late 1413 or early 1414) | year only |
| 13 | giraffe | the 1415 Malindi giraffe returned with the fourth voyage | 据说 |
| 15 | intro | Liu An, 179–122 BC (gloss) | — |
| 16 | — | 川剧 called 国家级非物质文化遗产 (first national list, 2006) | no date in the text |
| 17 | exam days | old Henan schedule (7–8 June). Henan has used the new gaokao since 2025 | no year in the text |
| 18 | intro, snow | 祥祥, the first captive-bred panda released (2006), died within a year | "about twenty years ago", "researchers believe" |
| 18 | training | model leopard and recorded calls used in wild-training at Hetaoping | — |
| 19 | departure | the "西去安西九千九百里" stone outside the Kaiyuan Gate | 据说 |
| 20 | — | 凉茶 on the first national intangible heritage list (2006) | — |
| 21 | legend-1 | photo of Yutu-2's tracks on the news on 4 Jan 2019 | "the next evening" |

## Language choices to confirm
- **18, snow-2:** 血 is read *xiě* in the line “没有血……” (colloquial). CC-CEDICT has only *xuè*, so
  the validator warns. Kept on purpose.
- **14:** the pet name 夏夏 is written *Xiàxia* (neutral second syllable).
- **20:** 外婆 (about 70 uses) is glossed as an ordinary word, not marked N.
- **All stories:** directional complements use neutral tone (*qǐlai, chūlai, xiàqu*), following the
  HSK 4 house style. The validator reports these as INFO only.

## Process note
The ten stories were drafted in parallel. Every final `.jsonl` was regenerated from its `.zhb` and
re-validated centrally before the PDFs were built, so temporary drafting files have no effect on the
results.
