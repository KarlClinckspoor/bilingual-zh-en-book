# Plan: 10 texts for HSK 3.0 Level 1 (stories 22–31)

The first steps of the series. Each text is a short, warm slice of everyday life, told in very simple
sentences with a lot of natural repetition and a little dialogue. Every text has a small point or
surprise at the end, so it reads as a story and not as a drill.

## Targets
See `plans/writing-brief-hsk1-2-3-6.md`. In short:
- 400–700 hanzi, 2–3 `@h2` sections.
- **100 % of non-name words at or below HSK 1** (word list, or all characters in the level-1 character
  list). Only names are footnoted, and there are no J or I tokens.
- Build: `make_book.py … --annotate-above 1 --annotate-kinds N`.

The level-1 list has about 500 words and 300 characters. Some obvious words are **not** level 1, so
write around them. For example: 猫, 狗 (L2), 饺子, 春节, 过年 (L2), 快乐 (L2), 地铁 (L2), 饭馆 (L2),
碗 (L2), 蛋糕 (L5), 苹果 (L3). Check any word you are unsure of with `hsk_level()`.

## Grammar map
Hooks are level-1 words or structures in the repo's word list. Check structures against GF 0025-2021.

| # | story | focus points |
|---|---|---|
| 22 | 我的家 | 是 · 有 / 没有 · 几 + measure word (口, 个) · 的 (possession) |
| 23 | 我的中国朋友 | 吗 / 呢 questions · 会 / 能 · 也 / 都 |
| 24 | 今天早上吃什么？ | 想 / 要 · 多少钱 · 块 · measure words (个, 杯) |
| 25 | 一二三 | numbers 1–100 · 几 / 多少 · 是 / 不是 · 这 / 那 |
| 26 | 下雨了 | 了 (change of state) · 太……了 · days of the week, 今天 / 明天 |
| 27 | 我生病了 | 了 · 不 / 没 · 要 / 不要 · 一点儿 (有点儿 is L2) |
| 28 | 今天是我的生日 | dates (月, 号, 星期) · 给 · 了 · 岁 |
| 29 | 在学校 | 在 (place / progressive) · 有 · 什么时候 · 点 / 分 times |
| 30 | 坐火车去北京 | 怎么 · 哪儿 · 先……再…… · 坐 / 去 / 到 |
| 31 | 新年好 | 一起 · 和 · 都 · 过 (to spend: 过新年) · 一边……一边…… |

## The texts

### 22 · 我的家 — *My Family*
- **Content:** a child introduces their family: who lives at home, ages, jobs, what each one likes.
- **Plot:** Xiao Wen (王小文) shows a family photo to a new classmate and names everyone. The last
  person in the photo is a "big brother" who turns out to be the family's grandfather when he was
  young. Simple, warm surprise.
- **Sections:** 我的家人 · 这是谁？
- **Names:** 王小文 and maybe one classmate.

### 23 · 我的中国朋友 — *My Chinese Friend*
- **Content:** language exchange: a foreign student and a Chinese student teach each other words.
- **Plot:** Anna (安娜), a student from abroad in Beijing, meets Li Ming (李明). She teaches him a
  little of her language, he teaches her Chinese. Questions back and forth (你会说……吗？ 这个
  怎么说？). At the end both can say a full sentence in the other's language.
- **Sections:** 一个新朋友 · 你会说吗？ · 我们都是老师
- **Names:** 安娜, 李明, 北京 (北京 is a level-1 word, so no N needed).

### 24 · 今天早上吃什么？ — *What's for Breakfast?*
- **Content:** Chinese breakfast: 包子, 面条, 米饭, 鸡蛋, 牛奶, 面包, 茶. Buying food, numbers and money.
- **Plot:** A father and his daughter go out on a Sunday morning. She wants bread and milk, he wants
  baozi and tea. They go to a small shop (饭店 or 商店) and count their money. In the end they buy both
  and share.
- **Sections:** 星期天早上 · 多少钱？ · 一人一半

### 25 · 一二三 — *One, Two, Three*
- **Content:** numbers, how Chinese people show 6–10 with one hand, why 八 is a number people like
  (it sounds a little like getting rich: keep it simple and say only "很多人喜欢八").
- **Plot:** A grandfather teaches his grandson to count on one hand. The boy shows his age with his
  fingers, then the grandfather's age (two hands are not enough!). A small joke at the end.
- **Sections:** 我的手 · 爷爷多大？ (只 is L2)

### 26 · 下雨了 — *It's Raining*
- **Content:** weather and the days of the week, what people do when it rains.
- **Plot:** One week from Monday to Sunday. It rains every day, and each family member does something
  different at home. On Sunday the sun comes out, and everyone goes out, except the cat... no cat at
  level 1, so make it the little sister, who is asleep.
- **Sections:** 星期一到星期五 · 星期六 · 星期天

### 27 · 我生病了 — *I'm Sick*
- **Content:** being ill, seeing the doctor (看病, 医院, 医生), rest, drinking water. No medical advice.
- **Plot:** Zhang Lin (张林) wakes up feeling ill and does not want to go to school. His mother takes
  him to the hospital. The doctor asks simple questions. At home he rests, drinks water and sleeps.
  In the evening his friends call, and he feels better at once. Light and positive.
- **Sections:** 早上 · 在医院 · 晚上

### 28 · 今天是我的生日 — *It's My Birthday*
- **Content:** a birthday in China: dates, ages, a bowl of noodles (面条) for a long life, presents.
  Avoid 蛋糕 and 快乐; say 生日好 or describe the wishes in simple words.
- **Plot:** Xiao Yu (小雨) thinks everyone has forgotten her birthday. Her day at school is quiet.
  At home, her grandmother has made noodles and her friends are waiting.
- **Sections:** 九月十号 · 大家都不知道？ · 一大家人 (or similar)

### 29 · 在学校 — *At School*
- **Content:** the school day: classes, the teacher, the timetable, lunch, friends.
- **Plot:** The first day at a new school, told hour by hour (八点…, 十二点…). Ma Xiaoshan (马小山) is
  scared in the morning. By the afternoon he has a friend. At home he says he wants to go to school
  tomorrow too.
- **Sections:** 第一天 · 上课 · 下课以后

### 30 · 坐火车去北京 — *By Train to Beijing*
- **Content:** travel: buying a ticket, the station, asking the way, taking a taxi, a map on the phone.
- **Plot:** Grandma (奶奶) travels alone by train for the first time to visit her son in Beijing. She
  asks people for help at the station, on the train and in Beijing. Her phone helps too. Her son
  thought she would get lost, but she finds his home before he gets back from work.
- **Sections:** 买票 · 在火车上 · 到北京了
- **Names:** maybe a station or a city name (北京 is level 1).

### 31 · 新年好 — *Happy New Year*
- **Content:** New Year at the grandparents' home: the family eats together, watches TV, says
  "新年好", the children get money and presents. Avoid 春节, 过年, 饺子 and 红包 (above level 1).
- **Plot:** Everyone comes home from different cities. The house is full and noisy. At midnight the
  family says 新年好 together, and the youngest child, who could not stay awake, says it the next
  morning to everyone.
- **Sections:** 回家 · 一起吃饭 · 新年的第一天
