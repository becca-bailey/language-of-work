# Source map: Menlo Innovations

Phase 1a wide-exploration census (capped). Counts/date-ranges per source by register.

> Caveat: HN Algolia `nbHits` overcounts (loose token / OR matching), and Open Library
> date ranges include off-topic hits. Trust the ranked **samples**, not raw totals, as the
> viability signal. Empty press/legal rows are tooling gaps (news.py/courts.py unbuilt),
> not data gaps.

| Source | Register | Query                        | Total hits | Date range             | Samples                                                                                                                                                                |
| ------ | -------- | ---------------------------- | ---------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| hn     | worker   | `Menlo Innovations`          | 39         | 2009-04-14..2026-05-03 | 8                                                                                                                                                                      |
| hn     | worker   | `"the Menlo Way"`            | 2          | 2012-10-17..2013-11-26 | 2                                                                                                                                                                      |
| books  | firm     | `Joy Inc Sheridan`           | 5          | 1600..2022             | 5 — first_publish_year of top hits = codification-date candidates                                                                                                      |
| books  | firm     | `Chief Joy Officer Sheridan` | 2          | 2018..2022             | 2 — first_publish_year of top hits = codification-date candidates                                                                                                      |
| reddit | worker   | ``                           | ?          | —                      | 0 — ERROR: keyless Reddit is blocked; set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET (register a script app at https://www.reddit.com/prefs/apps) to enable this source |

## Register coverage (viability gate)

- **firm**: 2 source-queries, ~7 total hits
- **press**: 0 source-queries, ~0 total hits
- **worker**: 3 source-queries, ~41 total hits
- **legal**: 0 source-queries, ~0 total hits

## Samples

### hn — `Menlo Innovations` (worker)

- **2013-11-21** [Who pairs? Looking for companies that pair program.](https://news.ycombinator.com/item?id=6778138)
  > Who pairs? Looking for companies that pair program. I am a Junior Web Developer researching companies that practice pair programming (and hopefully agile, tdd). I feel this would be the best environme
- **2012-10-17** [How I Hired Someone On Craigslist And Quadrupled My Productivity](https://news.ycombinator.com/item?id=4663174)
  > This reminds of of pair programming, or pair <i>everything</i> like they do at Menlo Innovations [1]. I took a tour there recently and it was pretty eye opening. People are now even paying to learn th
- **2024-01-06** [Focus and Flow: trade-offs in programmer productivity (2021)](https://news.ycombinator.com/item?id=38890892)
  > I agree, students and industry workers are not directly comparable. But one of the issues that I would wager is somewhat comparable is the human factors which, in the study above showed large ineffici
- **2022-03-06** [Pair Programming Antipatterns](https://news.ycombinator.com/item?id=30579993)
  > &gt; I find this hard to believe. Which country’s laws are you thinking of? In the US, at least, companies such as Pivotal and Menlo Innovations, as well as others I’m not at liberty to name, require
- **2022-03-06** [Pair Programming Antipatterns](https://news.ycombinator.com/item?id=30579804)
  > &gt; one little conflict away from a lawsuit<p>I find this hard to believe. Which country’s laws are you thinking of? In the US, at least, companies such as Pivotal and Menlo Innovations, as well as o
- **2021-10-27** [My Foreword to “The Art of Agile Development”](https://news.ycombinator.com/item?id=29017553)
  > I wish I knew! There <i>are</i> companies that get it, but they&#x27;re hard to filter out from the noise. Two I&#x27;m aware of are Pivotal and Menlo Innovations. I&#x27;m sure there are more.
- **2021-05-10** [The mortifying ordeal of pairing all day](https://news.ycombinator.com/item?id=27106294)
  > I can&#x27;t imagine pairing full time, but I did it for brief stints as a customer of Menlo Innovations. All customer code must be written by pairs, but one option to reduce costs is to have the cust
- **2019-07-30** [The art of interrupting software engineers](https://news.ycombinator.com/item?id=20563058)
  > Menlo innovations do pair everything and find most their employees are introverted and like it.<p>The theory is that introverts don&#x27;t dislike social interaction but unsafe social interaction. It&

### hn — `"the Menlo Way"` (worker)

- **2013-11-26** [The "Menlo way" of software development](https://news.ycombinator.com/item?id=6801938)
  > The "Menlo way" of software development
- **2012-10-17** [How I Hired Someone On Craigslist And Quadrupled My Productivity](https://news.ycombinator.com/item?id=4663174)
  > This reminds of of pair programming, or pair <i>everything</i> like they do at Menlo Innovations [1]. I took a tour there recently and it was pretty eye opening. People are now even paying to learn th

### books — `Joy Inc Sheridan` (firm)

- **2013** [Joy, Inc.](https://openlibrary.org/works/OL17105053W)
- **2015** [Joy, Inc.](https://openlibrary.org/works/OL21089118W)
- **2022** [Summary of Richard Sheridan's Joy, Inc](https://openlibrary.org/works/OL28114004W)
- **2002** [Kitchen afloat](https://openlibrary.org/works/OL5954463W)

### books — `Chief Joy Officer Sheridan` (firm)

- **2022** [Summary of Richard Sheridan's Chief Joy Officer](https://openlibrary.org/works/OL28134189W)
- **2018** [Chief Joy Officer](https://openlibrary.org/works/OL21184739W)
