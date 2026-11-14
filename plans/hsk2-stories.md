# Plan: 10 texts for HSK 3.0 Level 2 (stories 32–41)

Short stories told mostly in the past, each with one small problem and its solution, plus a little
real cultural content. Characters talk, compare things, and change their minds.

## Targets
See `plans/writing-brief-hsk1-2-3-6.md`. In short:
- 800–1,200 hanzi, 3–4 `@h2` sections.
- **100 % of non-name words at or below HSK 2** (word list, or all characters in the level-1/2
  character list). Only names are footnoted, and there are no J or I tokens.
- Build: `make_book.py … --annotate-above 2 --annotate-kinds N`.

Some obvious words are **above** level 2, so write around them. For example: 邻居, 钢琴, 视频 (L5),
感冒, 支付, 结婚, 跑步, 跳舞, 希望, 世界 (L3), 高铁, 微信, 拍照, 发烧 (L4), 宠物, 皇帝 (L6),
太极 (L7). Rivers, cities and people are names (N) and are exempt. Check any word you are unsure of
with `hsk_level()`.

## Grammar map
Hooks are level-1/2 words or structures in the repo's word list. Check structures against GF 0025-2021.

| # | story | focus points | review |
|---|---|---|---|
| 32 | 奶奶的手机 | 得 (degree complement: 学得很快) · 越来越 · 一边……一边 | 了 · 会 |
| 33 | 坐火车去西安 | 过 (experience) · 比 / 没有……那么 · 只要……就 | 先……再 |
| 34 | 包饺子 | 先……然后 · 着 · result complements (好, 完, 到, 懂) | 一边……一边 |
| 35 | 我的中文名字 | 因为……所以 · 原来 · 叫 / 姓 | 是……的 (if level 2; else drop) |
| 36 | 公园里的早上 | 正在……呢 · 有的……有的…… · 着 | 一边……一边 |
| 37 | 长江和黄河 | 比 · 跟……一样 · 不但……而且 · 最 | 因为……所以 |
| 38 | 楼上的音乐 | 以为 · 原来 · 虽然……但是 | 得 |
| 39 | 我家的猫 | 要……了 / 快……了 · 就 / 才 · 还是 / 或者 | 比 · 过 |
| 40 | 颜色的意思 | 因为……所以 · 不但……而且 · 一样 / 不一样 | 比 |
| 41 | 我为什么学中文 | 以为 · 越来越 · 虽然……但是 · 已经 | 得 · 原来 |

## The texts

### 32 · 奶奶的手机 — *Grandma's Phone*
- **Content:** older people and smartphones: calling with the camera on, buying things with the phone,
  maps, photos. Avoid 视频 and 微信; say 打电话的时候能看到人, 用手机买东西.
- **Plot:** Grandma gets her first smartphone and thinks it is too hard. Her grandson Ding Dong
  (丁冬) teaches her every weekend. She learns faster and faster. At the end she teaches the old
  people in her building, and calls her grandson to ask why he hasn't called her.
- **Sections:** 一个新手机 · 星期六的课 · 奶奶的学生

### 33 · 坐火车去西安 — *The Fast Train to Xi'an*
- **Content:** China's fast trains, compared with the old slow trains. Xi'an as an old city.
  Do not use 高铁 (L4); describe it: 新的火车, 很快的火车.
- **Plot:** A student, Liu Yang (刘洋), goes to Xi'an with his grandfather. Grandpa went there forty
  years ago on a slow train: two days, no seats. Today it takes a few hours. Grandpa compares
  everything (then vs now), and in Xi'an they find that one old noodle shop is still there.
- **Sections:** 爷爷去过西安 · 新的火车 · 还在的面馆
- **Names:** 西安 (L2 word), 刘洋.

### 34 · 包饺子 — *Making Dumplings*
- **Content:** making dumplings step by step at home before the New Year (avoid 春节 if it doesn't fit;
  饺子, 过年 are level 2, so they are fine here). The custom of hiding a coin in one dumpling (硬币 is L7: say 一块钱).
- **Plot:** A foreign student, Tom (汤姆), visits his Chinese friend's family to make dumplings. His
  first ones break or look funny. Everyone laughs, then helps. He eats the dumpling with the coin.
- **Sections:** 去朋友家 · 先……然后…… · 有钱的饺子 (or similar)

### 35 · 我的中文名字 — *My Chinese Name*
- **Content:** how Chinese names work (family name first, the meaning of characters) and how a learner
  gets a Chinese name.
- **Plot:** Mark (马克) has a Chinese name that a website gave him, and people smile when they hear
  it. His teacher explains why: the characters mean something funny together. With his classmates he
  chooses a new name, character by character, thinking about sound and meaning. Keep the "funny"
  name gentle and level-2 (for example, a name that sounds like a food).
- **Sections:** 大家都笑了 · 名字的意思 · 新名字

### 36 · 公园里的早上 — *Morning in the Park*
- **Content:** Chinese parks in the early morning: old people singing, writing big characters on the
  ground with water, playing ball, walking with birds, exercise. Avoid 太极, 跳舞, 跑步.
- **Plot:** Wang Xiaomei (王小美) has to get up at six to walk her grandfather to the park, and she
  hates it. She watches, and is surprised at how busy and happy the park is. A man writing characters
  with water asks her to write one. The next morning she wakes up her grandfather.
- **Sections:** 六点 · 公园里的人 · 地上的字

### 37 · 长江和黄河 — *Two Rivers*
- **Content:** the Yangtze and the Yellow River: length, colour, where they flow, big cities on them,
  why the Yellow River is like a mother to China (母亲 is L3, so say 像妈妈一样).
  Keep numbers simple and correct (长江 about 6,300 km, 黄河 about 5,400 km).
- **Plot (framed):** Two cousins, one from Chongqing (on the Yangtze) and one from Lanzhou (on the
  Yellow River), argue about whose river is better. Their grandfather settles it: both rivers end in
  the sea, and their family has lived by both.
- **Sections:** 谁的河好？ · 长江 · 黄河 · 都到大海 (or similar)
- **Names:** 长江, 黄河, 重庆, 兰州 (N), the cousins.

### 38 · 楼上的音乐 — *Music from Upstairs*
- **Content:** life in an apartment building, noise, getting to know the people who live near you.
  Avoid 邻居 and 钢琴: say 楼上的人, 住在楼上的老人, 音乐.
- **Plot:** Every evening, loud music comes from the flat upstairs, and Chen Jing (陈静) can't study.
  She thinks it's a young man having parties. She goes up to complain and finds an old man who teaches
  singing to children for free. In the end she joins them on Sunday afternoons.
- **Sections:** 每天晚上 · 我要上楼 · 原来是他

### 39 · 我家的猫 — *Our Cat*
- **Content:** a family and its cat; how a cat lives; responsibility.
- **Plot:** A small white cat (the children name it 小白, N; 灰 "grey" is L7) comes to the family's door in the rain.
  Mum doesn't want a cat. The children promise to look after it. Small problems (it breaks a cup, it
  goes missing). When it comes back, Mum is the one who was most worried.
- **Sections:** 下雨的晚上 · 妈妈不要猫 · 猫去哪儿了？ · 回来了 (不见 is L6)

### 40 · 颜色的意思 — *What Colours Mean*
- **Content:** colours in Chinese culture: red for happy days and the New Year, white in the past for
  sad days, yellow for the emperor long ago (皇帝 is L6, 古时候 is L3: say 以前, 很久以前, or leave
  the emperor out), green, and how colour meanings change today (white wedding dresses).
- **Plot:** A foreign student, Sophie (苏菲), wants to give a white present to a Chinese friend's
  family for the New Year. Her friend explains the colours. Sophie learns, and her friend learns that
  in Sophie's country it would be fine.
- **Sections:** 白色的礼物 · 红色 · 别的颜色 · 一样和不一样

### 41 · 我为什么学中文 — *Why I Learn Chinese*
- **Content:** learning Chinese: tones, characters, mistakes, reasons for learning.
- **Plot:** First-person story by a learner, Ben (本), with funny mistakes from tones: 买 / 卖, and
  水饺 / 睡觉 (he says he wants to "sleep" when he orders dumplings). He thought Chinese was too hard
  and wanted to stop. A Chinese friend tells him about his own mistakes in English. Now he gets better
  and better and isn't afraid of mistakes.
- **Sections:** 我想买，不想卖 · 睡觉还是水饺？ · 为什么学
