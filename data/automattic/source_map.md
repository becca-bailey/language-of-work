# Source map: Automattic

Phase 1a wide-exploration census (capped). Counts/date-ranges per source by register.

> Caveat: HN Algolia `nbHits` overcounts (loose token / OR matching), and Open Library
> date ranges include off-topic hits. Trust the ranked **samples**, not raw totals, as the
> viability signal. Empty press/legal rows are tooling gaps (news.py/courts.py unbuilt),
> not data gaps.

| Source | Register | Query | Total hits | Date range | Samples |
|---|---|---|---|---|---|
| hn | worker | `"Automattic"` | 3379 | 2008-10-27..2025-02-27 | 8 |
| hn | worker | `WP Engine Automattic` | 566 | 2024-09-24..2026-05-28 | 8 |
| hn | worker | `WordPress trademark Mullenweg` | 60 | 2015-07-25..2025-09-13 | 8 |
| hn | worker | `Automattic alignment offer` | 18 | 2012-08-24..2024-12-27 | 8 |
| hn | worker | `Automattic Creed` | 2262 | 2011-02-10..2025-09-13 | 8 |
| books | firm | `Year Without Pants Berkun` | 2 | 2013..2014 | 2 — first_publish_year of top hits = codification-date candidates |
| books | firm | `WordPress Mullenweg` | 1 | 2007..2007 | 1 — first_publish_year of top hits = codification-date candidates |
| reddit | worker | `` | ? | — | 0 — ERROR: Expecting value: line 1 column 1 (char 0) |

## Register coverage (viability gate)

- **firm**: 2 source-queries, ~3 total hits
- **press**: 0 source-queries, ~0 total hits
- **worker**: 6 source-queries, ~6285 total hits
- **legal**: 0 source-queries, ~0 total hits

## Samples

### hn — `"Automattic"` (worker)
- **2019-08-12** [Verizon to Sell Tumblr to Automattic](https://news.ycombinator.com/item?id=20679387)
  > Verizon to Sell Tumblr to Automattic
- **2024-10-03** [Filed: WP Engine Inc. v Automattic Inc. and Matthew Charles Mullenweg [pdf]](https://news.ycombinator.com/item?id=41726197)
  > Filed: WP Engine Inc. v Automattic Inc. and Matthew Charles Mullenweg [pdf]
- **2024-04-09** [Beeper acquired by Automattic](https://news.ycombinator.com/item?id=39980268)
  > Beeper acquired by Automattic
- **2017-06-12** [Automattic is closing its San Francisco office as most employees work remotely](https://news.ycombinator.com/item?id=14536410)
  > Automattic is closing its San Francisco office as most employees work remotely
- **2024-12-10** [WPEngine, Inc. vs. Automattic– Order on Motion for Preliminary Injunction](https://news.ycombinator.com/item?id=42382829)
  > WPEngine, Inc. vs. Automattic– Order on Motion for Preliminary Injunction
- **2024-09-24** [WP Engine sent “cease and desist” letter to Automattic](https://news.ycombinator.com/item?id=41631912)
  > WP Engine sent “cease and desist” letter to Automattic Direct link to letter: <a href="https:&#x2F;&#x2F;wpengine.com&#x2F;wp-content&#x2F;uploads&#x2F;2024&#x2F;09&#x2F;Cease-and-Desist-Letter-to-Aut
- **2024-10-04** [Some Automattic employees accept severance package offer](https://news.ycombinator.com/item?id=41738914)
  > Some Automattic employees accept severance package offer
- **2019-09-19** [Automattic raises $300M at $3B valuation from Salesforce Ventures](https://news.ycombinator.com/item?id=21015895)
  > Automattic raises $300M at $3B valuation from Salesforce Ventures

### hn — `WP Engine Automattic` (worker)
- **2024-11-15** [WP Engine revs Automattic lawsuit with antitrust claim](https://news.ycombinator.com/item?id=42143586)
  > WP Engine revs Automattic lawsuit with antitrust claim
- **2024-10-03** [WP Engine Sues Automattic and WordPress Co-Founder Matt Mullenweg](https://news.ycombinator.com/item?id=41727245)
  > WP Engine Sues Automattic and WordPress Co-Founder Matt Mullenweg
- **2026-05-27** [WP Engine and Automattic Trade Accusations](https://news.ycombinator.com/item?id=48300294)
  > WP Engine and Automattic Trade Accusations
- **2024-11-14** [WPEngine Accuses Automattic of WordPress Monopoly Abuse in New Lawsuit [pdf]](https://news.ycombinator.com/item?id=42137412)
  > WPEngine Accuses Automattic of WordPress Monopoly Abuse in New Lawsuit [pdf]
- **2024-10-03** [WP Engine Sues Automattic and Matt Mullenweg over WordPress Dispute](https://news.ycombinator.com/item?id=41726267)
  > WP Engine Sues Automattic and Matt Mullenweg over WordPress Dispute
- **2026-05-28** [WP23](https://news.ycombinator.com/item?id=48307602)
  > &gt; I believe Matt is right about the core issue in this fight. WordPress cannot become a place where large companies extract massive value from the ecosystem while ignoring the responsibilities that
- **2025-01-14** [WordPress Is in Trouble](https://news.ycombinator.com/item?id=42691528)
  > Don&#x27;t forget the time Matt <i>allegedly</i> attempted to extort the WPEngine CEO <i>into coming to work for him</i> [1]<p>1: <a href="https:&#x2F;&#x2F;www.therepository.email&#x2F;wp-engine-sues
- **2024-12-11** [WordPress CEO quits community Slack after court injunction](https://news.ycombinator.com/item?id=42391220)
  > I found it frustrating that the article highlights Mullenweg’s actions while failing to even briefly describe what WP Engine is, and what actions they took. The story felt very incomplete, perhaps int

### hn — `WordPress trademark Mullenweg` (worker)
- **2024-10-02** [Mullenweg threatens corporate takeover of WP Engine](https://news.ycombinator.com/item?id=41716586)
  > &gt; Again you&#x27;re claiming it was &quot;sudden&quot;, but it does not appear to have been sudden.<p>It was definitely sudden, just last week the term &quot;WP&quot; was explicitly allowed in Word
- **2024-09-25** [WP Engine sent “cease and desist” letter to Automattic](https://news.ycombinator.com/item?id=41648891)
  > Some important nuance is lost here. Matt Mullenweg transferred the trademark to the WordPress Foundation (which he is head of) and the foundation (again... Matt himself) in turn granted Automattic the
- **2015-07-25** [Thesis, Automattic, and WordPress: A Conflict of Ideology](https://news.ycombinator.com/item?id=9946243)
  > I just thought of another set of implications:<p>WordPress Foundation is the non-profit that owns the WordPress trademarks and source code. Automattic is a commercial entity working to &quot;defend&qu
- **2024-10-20** [Regarding our Cease and Desist letter to Automattic](https://news.ycombinator.com/item?id=41892618)
  > &gt; The trademark dispute ...<p>Is something Matt started, when he suddenly went after WPEngine for trademark use after decades of their use - during which time Matt praised and even invested in thei
- **2024-10-15** [Ask HN: Where After WordPress?](https://news.ycombinator.com/item?id=41853378)
  > I’ve tried to document the most relevant happenings and writings: <a href="https:&#x2F;&#x2F;duerrenberger.dev&#x2F;blog&#x2F;2024&#x2F;10&#x2F;08&#x2F;timeline-of-the-wordpress-drama&#x2F;" rel="nofo
- **2024-10-13** [The ACF plugin on the WordPress directory has been taken over by WordPress.org](https://news.ycombinator.com/item?id=41825884)
  > And Automattic&#x27;s control over WordPress is part of <i>their</i> &quot;marketing&quot; budget. Let&#x27;s not forget how valuable the exclusive commercial license for the WordPress trademark is to
- **2024-10-12** [My WordPress Slack Ban](https://news.ycombinator.com/item?id=41816005)
  > is this not true?<p>Main Points of Contention
Trademark and Branding Issues
Mullenweg accuses WP Engine of misusing the WordPress trademark and causing confusion among users1.
WP Engine has since chan
- **2024-10-10** [Mullenweg has gone 'nuclear' against tech investing giant Silver Lake](https://news.ycombinator.com/item?id=41804716)
  > As I understand it, Mullenweg has explicitly said in his video interview [0] that no other company is currently paying an 8% license fee. The WordPress Foundation trademark policy page [1] states (sin

### hn — `Automattic alignment offer` (worker)
- **2024-10-17** [Details of new alignment offer (Automattic)](https://news.ycombinator.com/item?id=41870882)
  > Details of new alignment offer (Automattic)
- **2024-10-17** [WordPress retaliation impacts community](https://news.ycombinator.com/item?id=41866568)
  > &gt; Mullenweg had also asked Automattic employees to pick a side, shortly after banning WP Engine from WordPress.org. He wrote on October 3 that Automattic had extended an &quot;&quot;Alignment Offer
- **2024-10-17** [WordPress retaliation impacts community](https://news.ycombinator.com/item?id=41866545)
  > I have been thinking about the alignment offer that Automattic has offered its employees. It’s hard for me to imagine any scenario at any company where I would not take the money and go. Six months of
- **2024-10-17** [Employees Describe an Environment of Paranoia and Fear Inside Automattic](https://news.ycombinator.com/item?id=41873015)
  > Quoting:<p>&gt; In the “Alignment Offer,” Mullenweg offered Automattic employees six months of pay or $30,000, whichever was higher, with the stipulation that they would lose access to their work logi
- **2024-10-17** [Employees Describe an Environment of Paranoia and Fear Inside Automattic](https://news.ycombinator.com/item?id=41872756)
  > &gt; “New alignment offer: I guess some people were sad they missed the last window. Some have been leaking to the press and ex-employees. That&#x27;s water under the bridge. Maybe the last offer need
- **2024-10-04** [Some Automattic employees accept severance package offer](https://news.ycombinator.com/item?id=41739442)
  > &gt;<i>So we decided to design the most generous buy-out package possible, we called it an Alignment Offer: if you resigned before 20:00 UTC on Thursday, October 3, 2024, you would receive $30,000 or 
- **2012-08-24** [Evernote Smart Notebook by Moleskine](https://news.ycombinator.com/item?id=4429474)
  > &#62; Yes, but how far is this from just using standard/college/quad ruled paper in the first place?<p>Not far.  Most of the features, it seems, do not really require the notebook.  But it also seems 
- **2015-01-14** [Cirqoid – printed circuit board prototyping machine](https://news.ycombinator.com/item?id=8889762)
  > Very cool.  Add a camera to do pick-and-place alignment automatically, and I&#x27;ll take one.  P&amp;P is pointless with that much manual intervention.<p>Another obvious improvement: offer a hot air 

### hn — `Automattic Creed` (worker)
- **2011-09-20** [Automattic Creed - Matt on sharing values with new people joining the company](https://news.ycombinator.com/item?id=3016686)
  > Automattic Creed - Matt on sharing values with new people joining the company
- **2022-11-02** [Ask HN: Who is hiring? (November 2022)](https://news.ycombinator.com/item?id=33432150)
  > AUTOMATTIC | SYSTEMS ENGINEER | REMOTE | FULL TIME | Proficiency with some or all of: NGINX, Docker, PHP, Golang, LUA, MySQL, ELK.<p>We’d love to chat with you if you have:
* Experience with implement
- **2022-10-04** [Ask HN: Who is hiring? (October 2022)](https://news.ycombinator.com/item?id=33078292)
  > AUTOMATTIC | SYSTEMS ENGINEER | REMOTE | FULL TIME | Proficiency with some or all of: NGINX, Docker, PHP, Golang, LUA, MySQL, ELK.<p>We’d love to chat with you if you have:<p>* Experience with impleme
- **2022-06-08** [Automattic Is Creepy](https://news.ycombinator.com/item?id=31662185)
  > Automattic Is Creepy
- **2020-05-21** [Coinbase will be a remote-first company](https://news.ycombinator.com/item?id=23255698)
  > I always feel that Automattic don&#x27;t get enough credit in these articles. Over 1000 employees in 70 countries and no central office...
- **2012-12-13** [WordPress.com Enterprise is Live](https://news.ycombinator.com/item?id=4918652)
  > When I first saw this, I thought, "Oh good, finally Automattic has something to compete with Page.ly, WP Engine, and Synthesis (i.e. managed WordPress hosting)."<p>But then I read their prices. The ot
- **2024-10-31** [WordPress forces user conf organizers to share social media credentials](https://news.ycombinator.com/item?id=42002195)
  > Organisers of WordCamps, community-organized events for WordPress users, have been ordered to take down some social media posts and share their login credentials for social networks.<p>The order to sh
- **2011-10-31** [Staying hungry post-ramen](https://news.ycombinator.com/item?id=3178467)
  > Staying hungry post-ramen In his Startup School talk, Matt Mullenweg mentioned a point where Automattic was doing well and he said to himself "I can just watch TV all day and make a thousand dollars!"

### books — `Year Without Pants Berkun` (firm)
- **2013** [The Year Without Pants](https://openlibrary.org/works/OL17579381W)
- **2014** [Shanah beli mikhnasayim](https://openlibrary.org/works/OL31448392W)

### books — `WordPress Mullenweg` (firm)
- **2007** [WordPress For Dummies](https://openlibrary.org/works/OL8206689W)

