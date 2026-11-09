# Plan: 10 short stories for HSK 3.0 Level 5

Series 2 of the bilingual reader. Stories 01–11 aimed at HSK 4 and were mostly explanatory
articles. This series moves up one level and changes form: each text is a **narrative short story**
with real cultural or social content built into the plot. HSK 5 readers can follow characters,
dialogue, time jumps and opinions, not only facts.

## Targets for every story

| item | target |
|---|---|
| length | 2,800–3,500 hanzi (stories 01–11: 2,000–2,700) |
| vocabulary | ≥ 90 % of running words at HSK ≤ 5; most of the rest are names (N), terms (J) or idioms (I) |
| new words | about 40–60 HSK 5 words per story, each used at least twice |
| grammar | 4 **focus points** per story, each used 3–5 times, plus 3–4 **review points** from earlier stories |
| form | narrative with dialogue (“……”), 5–8 sections (`@h2`), one paragraph = one scene beat |
| tone | concrete and human. Every story has a person who changes their mind about something |

Build and check commands (same pipeline as before, one level higher):

```bash
python zhb2jsonl.py stories/hsk5/12-watch-repairer/12-watch-repairer.zhb
python validate.py stories/hsk5/12-watch-repairer/12-watch-repairer.jsonl --annotate-above 5
python hsk_report.py stories/hsk5/12-watch-repairer/12-watch-repairer.jsonl --target 5
python make_book.py stories/hsk5/12-watch-repairer/12-watch-repairer.jsonl -o stories/hsk5/12-watch-repairer --annotate-above 5
```

## Grammar map

**How the points were chosen.** Function words marked *(L5)* are HSK 5 in the repo's HSK 3.0 word
list (`data/hsk30-expanded.csv`). Structures without a mark are generally taught around level 5 in the
2021 standard (GF 0025-2021). Check those against the official level 5 grammar list before final
editing. Words the list puts at 7–9 (何况, 与其, 宁可, 之所以, 以免, 趁, 难怪, 幸亏…) are **avoided as
focus points**. If a story needs one, it gets a footnote.

| # | story | focus points (new) | review |
|---|---|---|---|
| 12 | 胡同里的修表师傅 | 毕竟 (L5) · 居然 (L5) / 竟然 · 随着 (L5) · 一向 (L5) | 越来越 · 是……的 · 把字句 |
| 13 | 郑和下西洋 | 凭 (L5) · 将 (L5, written “will / 把”) · 以便 (L5) · 从而 (L5) | 被字句 · 由于……因此 |
| 14 | 回村的女孩 | 即使……也 (L5) · 尽管……还是 (L5) · 一旦……就 (L5) · 除非……否则/才 (L5) | 随着 · 毕竟 · 不但……而且 |
| 15 | 塞翁失马 | 反而 · 未必 · 究竟 · 不是 A，而是 B · rhetorical questions (难道……吗？ 谁知道……？) | 居然 · 即使……也 |
| 16 | 变脸 | 非……不可 · 连……都/也 · 再……也 · double negation (不得不, 没有……不……) | 一旦 · 尽管 · 凭 |
| 17 | 高考那一年 | 总算 (L5) · 不免 (L5) · 哪怕……也 · question words used generally (谁都, 怎么……也不……) | 毕竟 · 除非 · 反而 |
| 18 | 大熊猫回家 | 被/叫/让 + 给 passive · 因而 (L5) · 难以 (L5) · 加以 (L5) | 以便 · 一旦 · 随着 |
| 19 | 沙漠里的驼铃 | 依照 (L5) · 不顾 (L5) · 以往 (L5) · V 得起 / V 不起, V 得了 / V 不了 | 凭 · 将 · 从而 |
| 20 | 外婆的药箱 | extended directional complements (V 起来 / V 下去 / V 出来 / V 上) · A 是 A，就是/可是…… · 无论……都 | 未必 · 不免 · 难道……吗 |
| 21 | 月亮上的脚印 | consolidation: “V 着 V 着” · 越……越…… (clause-level) · 一……就…… · 是……的 (emphasis) | 总算 · 即使 · 因而 · 非……不可 |

## The stories

### 12 · 胡同里的修表师傅 — *The Watch Repairer of the Hutong*
- **Content:** Beijing hutongs, urban renewal, craftsmanship (工匠精神), old and new ways of living.
- **Plot:** Old Zhou has repaired watches in a corner of a hutong for forty years. His granddaughter
  Xiaoyu is a product designer who thinks the shop is a relic. When the lane is set to be renovated,
  she films his work for a school project, and the video unexpectedly goes viral. Young people start
  bringing their parents' old watches. The story ends with the shop moving into the renovated
  courtyard, smaller but busier.
- **Sections:** 一个角落 · 停了的表 · 拆还是不拆 · 镜头里的手 · 意想不到 · 新的院子
- **Vocab field:** 零件, 维修, 手艺, 耐心, 拆迁, 改造, 传统, 时代, 记忆, 精确

### 13 · 郑和下西洋 — *Zheng He Sails the Western Seas*
- **Content:** Ming dynasty (1405–1433), seven voyages, shipbuilding, the compass, trade and diplomacy,
  and why the voyages stopped.
- **Plot:** Told through Ali, a fictional young interpreter from Quanzhou who joins the fourth voyage.
  We see the treasure ships, the navigation stars, the arrival at Calicut and Hormuz, and a giraffe
  brought back to the court. In the last scene an old Ali hears the fleet will never sail again and
  wonders what it means.
- **Sections:** 泉州的少年 · 宝船 · 星星和罗盘 · 远方的港口 · 一只长颈鹿 · 船队不再出发
- **Vocab field:** 航海, 船队, 港口, 贸易, 使者, 礼物, 方向, 风暴, 朝廷, 交流
- **Fact-check:** dates, ports, number of ships. Mark the uncertain figures as uncertain in the text.

### 14 · 回村的女孩 — *The Girl Who Went Back to the Village*
- **Content:** rural revitalisation (乡村振兴), live-stream selling (直播带货), migration and the
  generation gap.
- **Plot:** Lin Xia quits an office job in Shenzhen and returns to her family's tea village in Fujian.
  Her father thinks she has failed. Her first live streams fail (bad signal, no viewers). Then a storm
  ruins half the harvest, and she streams the truth instead of an advertisement, and orders come in.
  Her father ends up appearing in the streams, explaining how tea is roasted.
- **Sections:** 辞职 · 爸爸的沉默 · 没人看的直播 · 一场大雨 · 说真话 · 镜头前的爸爸
- **Vocab field:** 农产品, 网络, 观众, 订单, 失败, 坚持, 收入, 信任, 质量, 宣传
- **Link:** builds on story 01 (tea) with new vocabulary.

### 15 · 塞翁失马 — *Old Sai Loses His Horse*
- **Content:** the classical fable (*Huainanzi*) and the Daoist idea that good and bad fortune turn into
  each other. Idioms in context.
- **Plot (frame story):** Haoran loses a job offer he was sure of and comes home angry. His grandfather
  tells him the fable in full: the horse runs off, returns with another, the son breaks his leg, and
  the leg saves him from war. Over the following months Haoran's "bad luck" leads somewhere unexpected.
  The ending stays open: it is not fully good, only different.
- **Sections:** 没有得到的工作 · 爷爷的故事 · 马跑了 · 马回来了 · 后来呢 · 祸福
- **Idioms (I):** 塞翁失马，焉知非福 · 祸不单行 · 因祸得福 · 自言自语 (each footnoted once)
- **Vocab field:** 运气, 失望, 安慰, 结果, 打仗, 邻居, 祝贺, 恐怕, 道理, 意外

### 16 · 变脸 — *The Face-Changer's Apprentice*
- **Content:** Sichuan opera, face-changing (变脸) as intangible cultural heritage (非物质文化遗产),
  master–apprentice transmission and the tradition of secrecy.
- **Plot:** Thirteen-year-old Ming Hao in Chengdu pesters an old performer, Master Tang, to teach him.
  The master refuses and then sets impossible tasks: practise for a year before touching a mask. A
  stage accident during a tea-house show forces Ming Hao to go on early. The master's decision at the
  end is about trust, not skill.
- **Sections:** 茶馆里的表演 · 不收徒弟 · 一年的基本功 · 秘密 · 意外 · 第一张脸
- **Vocab field:** 表演, 舞台, 观众, 练习, 动作, 面具, 秘密, 师傅, 徒弟, 传承

### 17 · 高考那一年 — *The Year of the Gaokao*
- **Content:** China's national college entrance exam, family expectations, choosing a path versus
  choosing "the safe thing".
- **Plot:** One school year in the life of Chen Jing, a quiet student in a small city in Henan who
  secretly wants to study archaeology, against her mother's plan (medicine or finance). A mock exam
  goes badly, a friendship breaks and is mended, and the June exam days are told hour by hour. When the
  results come, the real decision is about the application form, not the score.
- **Sections:** 九月 · 墙上的倒计时 · 模拟考试 · 妈妈的计划 · 六月七日 · 填志愿
- **Vocab field:** 考试, 成绩, 压力, 志愿, 专业, 复习, 期待, 选择, 紧张, 梦想

### 18 · 大熊猫回家 — *Bringing the Pandas Home*
- **Content:** giant panda conservation, reintroduction into the wild, habitat corridors, bamboo die-off
  cycles, the work of field researchers.
- **Plot:** Field researcher Yang Fan at a breeding centre in Sichuan prepares a young female panda,
  "Caocao" (草草), for release. Keepers wear panda costumes so she does not get used to humans.
  Caocao is released, her GPS collar goes silent in winter, and the team searches for her in the snow.
  In spring they find her, alive and not alone.
- **Sections:** 穿熊猫衣服的人 · 学会害怕 · 放归 · 没有信号 · 雪地里的脚印 · 春天
- **Vocab field:** 保护, 环境, 野生, 适应, 研究, 数据, 森林, 生存, 危险, 恢复

### 19 · 沙漠里的驼铃 — *Camel Bells in the Desert*
- **Content:** the Silk Road in the Tang dynasty, Chang'an and Dunhuang, Sogdian merchants, goods and
  ideas (silk, paper, music, Buddhism) moving in both directions.
- **Plot:** A Sogdian merchant's son, Kang Ning, makes his first caravan crossing from Chang'an to
  Samarkand. Sandstorms, a dispute over prices at Dunhuang, and an injured camel teach him that the
  road runs on trust and rules, not only profit. He brings home something unexpected that cannot be
  sold.
- **Sections:** 长安的西市 · 出发 · 敦煌 · 沙尘暴 · 一头受伤的骆驼 · 带回来的东西
- **Vocab field:** 商人, 骆驼, 丝绸, 价格, 规矩, 沙漠, 交换, 文化, 损失, 经验
- **Link:** builds on stories 09 (four inventions: paper) and 05 (Great Wall, frontier).

### 20 · 外婆的药箱 — *Grandma's Medicine Chest*
- **Content:** traditional Chinese medicine in daily life (herbal soups, 上火, seasonal eating),
  modern medicine, and how families combine the two. Not promotional: the story is balanced and does
  not make health claims.
- **Plot:** Medical student Xu Le spends the summer with her grandmother in Guangzhou, whose wooden
  medicine chest and "cooling" soups she finds unscientific. When the grandmother falls ill, Xu Le
  insists on the hospital, and she is right. While caring for her, though, she learns what the soups
  and rituals really did: they kept a family paying attention to each other.
- **Sections:** 木头药箱 · 凉茶 · 争论 · 半夜的电话 · 医院 · 一碗汤
- **Vocab field:** 健康, 医生, 治疗, 症状, 科学, 习惯, 照顾, 传统, 相信, 关心
- **Care point:** no medical advice. Characters' opinions stay characters' opinions.

### 21 · 月亮上的脚印 — *Footprints on the Moon*
- **Content:** China's lunar programme (Chang'e missions, the far-side landing, sample return), the
  Chang'e legend, and how a myth gives a name to a machine.
- **Plot:** A father and daughter in a small town watch the Chang'e-4 landing on TV in 2019. The
  daughter, Xingxing, starts asking questions her father cannot answer. Told in jumps across fifteen
  years, she becomes an engineer on a later mission team. The last scene mirrors the first, on another
  TV, with her father watching her.
- **Sections:** 电视里的月亮 · 嫦娥和玉兔 · 月亮的背面 · 十年 · 控制中心 · 爸爸的电视
- **Vocab field:** 探索, 卫星, 发射, 工程师, 宇宙, 科学, 理想, 成功, 信号, 着陆
- **Fact-check:** mission names and dates (Chang'e-4 Jan 2019, Chang'e-5 Dec 2020, Chang'e-6 June 2024).
  Keep any future missions clearly fictional or vague.

## Order and balance

| strand | stories |
|---|---|
| modern life | 12 hutong · 14 village · 17 gaokao · 20 medicine chest |
| history | 13 Zheng He · 19 Silk Road |
| tradition and ideas | 15 Sai Weng · 16 face-changing |
| science and nature | 18 pandas · 21 Moon |

Suggested writing order: 12 → 15 → 14 → 13 → 16 → 18 → 17 → 19 → 20 → 21. The table order works
too. This order puts an easier, dialogue-heavy story first and spaces out the review points.

## Quality checklist per story

1. `validate.py` passes with no ERROR. Every pinyin WARN is resolved by hand.
2. `hsk_report.py --target 5` gives ≥ 90 % at L ≤ 5. List the words above L5 and replace any that are
   not N/J/I.
3. Each focus grammar point appears 3–5 times, ideally once in narration and once in dialogue.
4. A native speaker reads it before publishing. Natural rhythm matters more at HSK 5 than at HSK 4.
5. Fact-check the history and science stories (13, 18, 19, 21).
