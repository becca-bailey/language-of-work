# Deck echo clusters across the netflix-culture cohort (2026-07-23)

Pairs at cosine >= 0.5 between any deck sentence and any company sentence.
`covered` = sentence also clears the current 14-concept echo floor.


## Section x company echo matrix (pairs >= 0.5, netflix excluded)

| deck section | goog | amaz | meta | pala | coin | shop | stri | airb | snap | hubs | gitl | gith | sale | engi | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| values = what's rewarded (Enron) |  | 1 |  |  |  |  | 1 |  |  |  |  |  | 1 | 1 | 4 |
| the nine values (judgment..selflessness) | 1 | 7 | 2 |  |  | 4 | 5 | 2 | 5 | 1 | 2 |  | 2 | 8 | 39 |
| high performance (severance, keeper test, team-not-family, not-for-everyone) | 2 | 1 | 3 |  | 8 | 6 | 11 | 1 | 3 | 3 | 5 |  | 7 | 14 | 64 |
| freedom as we grow | 7 |  | 3 | 2 | 1 | 2 |  |  |  | 3 | 2 |  | 3 | 1 | 24 |
| talent density vs complexity | 2 |  | 1 |  | 6 | 6 | 3 | 1 |  |  |  | 1 | 4 | 7 | 31 |
| rules / rapid recovery |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| no policies (vacation, expenses) | 2 |  |  |  | 1 | 1 | 2 |  |  | 1 |  |  |  |  | 7 |
| context, not control |  |  |  |  |  |  | 1 |  |  | 1 |  |  |  |  | 2 |
| highly aligned, loosely coupled |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 0 |
| pay top of market | 1 | 2 |  |  |  |  |  |  |  |  |  |  | 1 |  | 4 |
| promotions & development |  | 2 |  |  | 2 | 2 | 5 | 1 |  | 2 |  |  | 3 | 1 | 18 |
| closing | 3 |  | 2 |  | 4 |  | 1 |  |  | 5 | 1 |  | 5 | 4 | 25 |

## Exemplars per section (top 6 by score)

### values = what's rewarded (Enron) — 4 pairs, 4 covered / 0 missed
- 0.552 [covered:values_not_wall] **stripe** 2019: "A great deal of your fulfillment at any company is determined by the extent to which the values of the people "  
  ↳ deck s7: "Actual company values are the behaviors and skills that are valued in fellow employees"
- 0.534 [covered:values_not_wall] **engine** 2025: "It’s who we hire, how we work, and what we reward."  
  ↳ deck s6: "The actual company values, as opposed to the nice-sounding values, are shown by who getsrewarded, promoted, or"
- 0.515 [covered:freedom_responsibility] **salesforce** 2026: "Our core values guide everything we do as a company and as people."  
  ↳ deck s7: "Actual company values are the behaviors and skills that are valued in fellow employees"
- 0.506 [covered:freedom_responsibility] **amazon** 2007: "We make decisions as a company, and as individuals, based on our core values."  
  ↳ deck s7: "Actual company values are the behaviors and skills that are valued in fellow employees"

### the nine values (judgment..selflessness) — 39 pairs, 4 covered / 35 missed
- 0.613 [MISSED] **stripe** 2020: "We seek fresh perspectives, challenge industry convention and assumptions, and develop innovative and automate"  
  ↳ deck s13: "You re-conceptualize issues to discover practical solutions to hard problems You challenge prevailingInnovatio"
- 0.613 [MISSED] **amazon** 2013: "People who are innovative; people who enjoy solving complex problems with ingenuity and simplicity."  
  ↳ deck s13: "You re-conceptualize issues to discover practical solutions to hard problems You challenge prevailingInnovatio"
- 0.605 [MISSED] **snap** 2022: "We solve problems through action, make high-quality decisions, and think with a strategic mindset."  
  ↳ deck s9: "You make wise decisions (people, technical, business, and creative) despite ambiguity You identify root causes"
- 0.592 [MISSED] **snap** 2022: "We Are Smart We solve problems through action, make high-quality decisions, and think with a strategic mindset"  
  ↳ deck s9: "You make wise decisions (people, technical, business, and creative) despite ambiguity You identify root causes"
- 0.584 [MISSED] **engine** 2021: "Think of new ways to approach obstacles and opportunities that inspire results."  
  ↳ deck s13: "You re-conceptualize issues to discover practical solutions to hard problems You challenge prevailingInnovatio"
- 0.584 [MISSED] **amazon** 2016: "Leaders expect and require innovation and invention from their teams and always find ways to simplify."  
  ↳ deck s13: "You re-conceptualize issues to discover practical solutions to hard problems You challenge prevailingInnovatio"

### high performance (severance, keeper test, team-not-family, not-for-everyone) — 64 pairs, 26 covered / 38 missed
- 0.681 [covered:adequate_severance] **coinbase** 2021: "Unremarkable performance gets a generous severance package."  
  ↳ deck s22: "Unlike many companies, we practice:adequate performance gets agenerous severance package"
- 0.649 [covered:team_not_family] **coinbase** 2021: "We are a winning team, not a family, and have high expectations for performance and delivering results."  
  ↳ deck s23: "We’re a team, not a family We’re like a pro sports team, not a kid’s recreational team Netflix leaders hire, d"
- 0.644 [MISSED] **coinbase** 2017: "We take care of each other, and help each other grow."  
  ↳ deck s31: "We Help Each Other To Be Great"
- 0.597 [covered:raise_the_bar] **engine** 2025: "We inspire and push each other to achieve more."  
  ↳ deck s31: "We Help Each Other To Be Great"
- 0.578 [covered:judged_by_outcomes] **gitlab** 2018: "A culture of results, not hours spent: Flexible hours let us schedule our days so that we do our best work wit"  
  ↳ deck s34: "Hard Work – Not Relevant• We don’t measure people by how many hours they work or how much they are in the offi"
- 0.573 [covered:only_the_best] **coinbase** 2021: "We cast a wide net, to attract candidates from every background, focusing on both skill and culture alignment."  
  ↳ deck s21: "Like every company, we try to hire well"

### freedom as we grow — 24 pairs, 4 covered / 20 missed
- 0.580 [covered:freedom_responsibility] **meta** 2011: "Hear from our leadership team about why we emphasize freedom and autonomy inside the company and how we build "  
  ↳ deck s42: "Our model is to increase employee freedom as we grow, rather than limit it,to continue to attract and nourish "
- 0.559 [covered:freedom_responsibility] **google** 2014: "Our company culture encourages experimentation and the free flow of ideas."  
  ↳ deck s42: "Our model is to increase employee freedom as we grow, rather than limit it,to continue to attract and nourish "
- 0.543 [MISSED] **google** 2007: "From our flexible, project-based approach to corporate structure to our innovative perks and benefits, we do e"  
  ↳ deck s42: "Our model is to increase employee freedom as we grow, rather than limit it,to continue to attract and nourish "
- 0.542 [MISSED] **coinbase** 2025: "We believe flexibility boosts productivity, while in-person collaboration drives innovation."  
  ↳ deck s42: "Our model is to increase employee freedom as we grow, rather than limit it,to continue to attract and nourish "
- 0.539 [covered:freedom_responsibility] **gitlab** 2026: "We run our business on our own product, stay transparent in how we work, and create space for team members acr"  
  ↳ deck s42: "Our model is to increase employee freedom as we grow, rather than limit it,to continue to attract and nourish "
- 0.536 [MISSED] **engine** 2024: "This openness supports our people in doing their best work, developing their career, and maximizing the impact"  
  ↳ deck s42: "Our model is to increase employee freedom as we grow, rather than limit it,to continue to attract and nourish "

### talent density vs complexity — 31 pairs, 9 covered / 22 missed
- 0.670 [MISSED] **coinbase** 2014: "Be ruthless about cutting out complexity, otherwise it will creep in slowly until it takes over."  
  ↳ deck s57: "Minimize Complexity Growth• Few big products vs many small ones• Eliminate distracting complexity (barnacles)•"
- 0.634 [MISSED] **coinbase** 2016: "We're ruthless about cutting out complexity, otherwise it can creep in and slowly take over."  
  ↳ deck s57: "Minimize Complexity Growth• Few big products vs many small ones• Eliminate distracting complexity (barnacles)•"
- 0.603 [covered:only_the_best] **salesforce** 2006: "What attracts top talent globally is our "change the world" mentality, coupled by the opportunity to excel in "  
  ↳ deck s56: "Increase Talent Density • Top of market compensation • Attract high-value people through freedom to make big i"
- 0.599 [covered:freedom_responsibility] **github** 2011: "We operate in a culture based on personal responsibility, rather than management, by hiring great people and t"  
  ↳ deck s58: "With the Right People, Instead of aCulture of Process Adherence, We have a Culture ofCreativity and Self-Disci"
- 0.599 [covered:only_the_best] **salesforce** 2007: "What attracts top talent globally is our "change-the-world" mentality, coupled with the opportunity to excel i"  
  ↳ deck s56: "Increase Talent Density • Top of market compensation • Attract high-value people through freedom to make big i"
- 0.595 [MISSED] **coinbase** 2014: "Always ask what can be removed, consolidated, and redone to eliminate complexity."  
  ↳ deck s57: "Minimize Complexity Growth• Few big products vs many small ones• Eliminate distracting complexity (barnacles)•"

### no policies (vacation, expenses) — 7 pairs, 2 covered / 5 missed
- 0.585 [covered:no_vacation_policy] **hubspot** 2020: "We work remotely, keep non-traditional hours, and use unlimited vacation to create work-life "fit" for us and "  
  ↳ deck s66: "Meanwhile…We’re all working online some nights and weekends, responding to emails at odd hours, spending some "
- 0.577 [MISSED] **stripe** 2019: "But working here will mean some late nights, some weekends, and (especially if you end up in a position of sig"  
  ↳ deck s66: "Meanwhile…We’re all working online some nights and weekends, responding to emails at odd hours, spending some "
- 0.575 [MISSED] **shopify** 2012: "We don’t believe in silly rules like working 9 to 5 every day."  
  ↳ deck s68: "We should focus on what people get done, not on how many days workedJust as we don’t have an 9am-5pm workday p"
- 0.528 [MISSED] **google** 2020: "Operating at this scale brings an elevated level of responsibility to everything we do—including a workforce t"  
  ↳ deck s76: "Freedom and Responsibility• Many people say one can’t do it at scale• But since going public in 2002, which is"
- 0.520 [covered:no_vacation_policy] **coinbase** 2014: "There is no set time you need to be in the office, and the vacation policy is quite flexible."  
  ↳ deck s68: "We should focus on what people get done, not on how many days workedJust as we don’t have an 9am-5pm workday p"
- 0.516 [MISSED] **google** 2008: "Google offers the freedom of a startup with the stability of a large, profitable and growing company."  
  ↳ deck s76: "Freedom and Responsibility• Many people say one can’t do it at scale• But since going public in 2002, which is"

### context, not control — 2 pairs, 0 covered / 2 missed
- 0.515 [MISSED] **hubspot** 2020: "That’s why I make sure to read the announcements, check our company’s corporate meeting notes, talk to my fell"  
  ↳ deck s86: "Investing in Context This is why we do new employee college, frequent department meetings, and why we are so o"
- 0.514 [MISSED] **stripe** 2020: "We over-index on transparency because we believe access to information is imperative to creating the very best"  
  ↳ deck s86: "Investing in Context This is why we do new employee college, frequent department meetings, and why we are so o"

### pay top of market — 4 pairs, 1 covered / 3 missed
- 0.565 [MISSED] **google** 2008: "We provide individually-tailored compensation packages that can be comprised of competitive salary, bonus, and"  
  ↳ deck s110: "Optional Options• Employees get top of market salary, and then can request to trade salary for stock options• "
- 0.515 [MISSED] **salesforce** 2016: "Continuously assess and aim for pay equity across the entire organization"  
  ↳ deck s98: "Takes Great Judgment• Goal is to keep each employee at top of market for that person – Pay them more than anyo"
- 0.504 [MISSED] **amazon** 1999: "Also, since this is very possibly the worst five-year period in history not to have equity ownership, you shou"  
  ↳ deck s110: "Optional Options• Employees get top of market salary, and then can request to trade salary for stock options• "
- 0.503 [covered:raise_the_bar] **amazon** 2016: "Leaders raise the performance bar with every hire and promotion."  
  ↳ deck s96: "Pay Top of Market is Core to High Performance Culture One outstanding employee gets more doneand costs less th"

### promotions & development — 18 pairs, 5 covered / 13 missed
- 0.568 [covered:freedom_responsibility] **stripe** 2019: "We believe in performance management and feedback, but we’re not rigid in terms of a career paths and box chec"  
  ↳ deck s121: "Career “Planning” Not for Us• Formalized development is rarely effective, and we don’t try to do it – e.g., Me"
- 0.556 [MISSED] **shopify** 2015: "We care about growing great people Your personal growth is important to us, and we’ll give you everything you "  
  ↳ deck s120: "Development• We develop people by giving them the opportunity to develop themselves, by surrounding them with "
- 0.555 [MISSED] **stripe** 2019: "Are you comfortable with owning your own career outcomes, rather than having a clear progression of goals and "  
  ↳ deck s123: "We want people to manage their own career growth,and not rely on a corporation for “planning” their careers"
- 0.553 [MISSED] **airbnb** 2019: "We’re driven by curiosity, optimism, and the belief that every person can grow."  
  ↳ deck s122: "We Support Self-Improvement• High performance people are generally self- improving through experience, observa"
- 0.553 [covered:team_not_family] **coinbase** 2024: "We have high expectations for performance and delivering results, and thrive as a team of individual star perf"  
  ↳ deck s122: "We Support Self-Improvement• High performance people are generally self- improving through experience, observa"
- 0.547 [MISSED] **hubspot** 2020: "From weekly tech talks to 1:1 mentoring, we're constantly helping each other become the best product people (a"  
  ↳ deck s122: "We Support Self-Improvement• High performance people are generally self- improving through experience, observa"

### closing — 25 pairs, 8 covered / 17 missed
- 0.591 [MISSED] **coinbase** 2021: "We seek to improve all aspects of our company even in ways that are not explicitly part of our job."  
  ↳ deck s126: "We keep improvingour culture as we grow We try to get betterat seeking excellence"
- 0.587 [MISSED] **hubspot** 2018: "We have to not just build culture, but iterate on it over time."  
  ↳ deck s126: "We keep improvingour culture as we grow We try to get betterat seeking excellence"
- 0.580 [covered:freedom_responsibility] **hubspot** 2024: "Our culture is not tied to locations, it’s rooted in our values, our amazing people, and our mission of helpin"  
  ↳ deck s125: "Seven Aspects of our Culture• Values are what we Value• High Performance• Freedom & Responsibility• Context, n"
- 0.579 [covered:raise_the_bar] **engine** 2019: "We’re always pushing forward to better our operations, products, and services."  
  ↳ deck s126: "We keep improvingour culture as we grow We try to get betterat seeking excellence"
- 0.574 [MISSED] **hubspot** 2018: "And, as we keep finding bugs in our Culture Code, we’ll keep fixing them."  
  ↳ deck s126: "We keep improvingour culture as we grow We try to get betterat seeking excellence"
- 0.574 [MISSED] **hubspot** 2020: "We're building a culture where personal and professional growth are just as important as business growth."  
  ↳ deck s126: "We keep improvingour culture as we grow We try to get betterat seeking excellence"


## Coinbase canon essays vs deck

- 0.640 [culturedoc] "We seek out ways to improve our products, culture, and the company overall, even in ways that are not explicit"  
  ↳ deck s126 (closing): "We keep improvingour culture as we grow We try to get betterat seeking excellence"
- 0.580 [culturedoc] "We over invest in finding top talent, knowing that recruiting and developing top talent is the root cause of a"  
  ↳ deck s56 (talent density vs complexity): "Increase Talent Density • Top of market compensation • Attract high-value people through freedom to "
- 0.576 [culturedoc] "There are six tenets of our culture, with a set of actions under each one."  
  ↳ deck s3 (intro): "Seven Aspects of our Culture• Values are what we Value• High Performance• Freedom & Responsibility• "
- 0.564 [culturedoc] "We discourage internal competition, instead asking everyone to put their company hat on."  
  ↳ deck s30 (high performance (severance, keeper test, team-not-family, not-for-everyone)): "Corporate Team The more talent we have, the more we can accomplish,so our people assist each other a"
- 0.554 [culturedoc] "We have a goal to put top talent in every seat, and we work hard to fight the bias that might lead us to miss "  
  ↳ deck s21 (high performance (severance, keeper test, team-not-family, not-for-everyone)): "Like every company, we try to hire well"
- 0.554 [mission2020] "We have a pay for performance culture, which means that your rewards and promotions are linked to your overall"  
  ↳ deck s114 (divider): "Seven Aspects of our Culture• High Performance• Values are what we Value• Freedom & Responsibility• "
- 0.551 [culturedoc] "What we won’t do Only celebrate the individual above the whole Foster internal competition Ask one product to "  
  ↳ deck s113 (pay top of market): "No Ranking Against Other Employees• We avoid “top 30%” and “bottom 10%” rankings amongst employees• "
- 0.546 [culturedoc] "We prefer to occasionally miss out on a good hire rather than make a bad hire (in other words we intentionally"  
  ↳ deck s21 (high performance (severance, keeper test, team-not-family, not-for-everyone)): "Like every company, we try to hire well"
- 0.544 [culturedoc] "Finding top talent requires us to cast the widest net possible and understand unique strengths and capabilitie"  
  ↳ deck s56 (talent density vs complexity): "Increase Talent Density • Top of market compensation • Attract high-value people through freedom to "
- 0.542 [culturedoc] "We prioritize team goals over individual goals, because we all benefit most from the success of the parent com"  
  ↳ deck s30 (high performance (severance, keeper test, team-not-family, not-for-everyone)): "Corporate Team The more talent we have, the more we can accomplish,so our people assist each other a"
- 0.541 [culturedoc] "A lot is asked of us: excellence in our work, solving hard challenges, 100% accountability for our actions, an"  
  ↳ deck s2 (intro): "We Seek ExcellenceOur culture focuses on helping us achieve excellence"
- 0.540 [culturedoc] "Our goal as a team is to continually get closer to this ideal (we will likely never be 100% perfect on it)."  
  ↳ deck s126 (closing): "We keep improvingour culture as we grow We try to get betterat seeking excellence"
- 0.537 [culturedoc] "Instead, we choose to foster a culture of repeatable innovation and celebrate being a multi-product company."  
  ↳ deck s42 (freedom as we grow): "Our model is to increase employee freedom as we grow, rather than limit it,to continue to attract an"
- 0.533 [culturedoc] "We are rigorous about hiring based on skills and values, but outside of this, we welcome people from every bac"  
  ↳ deck s21 (high performance (severance, keeper test, team-not-family, not-for-everyone)): "Like every company, we try to hire well"
- 0.533 [culturedoc] "We do reference checks on every hire."  
  ↳ deck s21 (high performance (severance, keeper test, team-not-family, not-for-everyone)): "Like every company, we try to hire well"

## Engine corpus vs Coinbase canon (direct-descent test)

Engine sentences echoing (>=0.5) the Netflix deck: 46; echoing Coinbase canon: 103.

- 0.704 engine 2026: "If we haven't failed, we haven't tried hard enough."  
  ↳ coinbase culturedoc: "If some of our projects aren’t failing, we aren’t thinking big enough."
- 0.666 engine 2019: "We act in unity to support our team, collaborate with respect, and work together toward a shared vision."  
  ↳ coinbase mission2020: "Act in service of the greater mission: We have united as a team to try and accomplish something that none of u"
- 0.641 engine 2026: "We'd rather be a place where people of every background and belief can focus on the same goal."  
  ↳ coinbase culturedoc: "At work, we focus on what unites us, our mission, and not what divides us."
- 0.637 engine 2024: "We look for candidates with diverse talents and backgrounds who are energized by our culture."  
  ↳ coinbase culturedoc: "We are rigorous about hiring based on skills and values, but outside of this, we welcome people from every bac"
- 0.636 engine 2021: "Great people are our number one investment, critical to our success today and our growth in the future."  
  ↳ coinbase culturedoc: "We over invest in finding top talent, knowing that recruiting and developing top talent is the root cause of a"
- 0.633 engine 2026: "We choose to focus that energy entirely on our customers, our product, and our mission."  
  ↳ coinbase mission2020: "We focus on the things that help us achieve our mission: Build great products: The vast majority of the impact"
- 0.632 engine 2019: "Every individual is empowered to take initiative and tackle challenges."  
  ↳ coinbase culturedoc: "Each one of us is empowered to make this company a success."
- 0.630 engine 2022: "We’re focused on finding the right people who are energized by our culture, with diverse experiences and backg"  
  ↳ coinbase culturedoc: "Finding top talent requires us to cast the widest net possible and understand unique strengths and capabilitie"
- 0.623 engine 2019: "We’re always pushing forward to better our operations, products, and services."  
  ↳ coinbase culturedoc: "We seek out ways to improve our products, culture, and the company overall, even in ways that are not explicit"
- 0.618 engine 2021: "That starts and ends with finding and nurturing the best and brightest talent."  
  ↳ coinbase culturedoc: "We over invest in finding top talent, knowing that recruiting and developing top talent is the root cause of a"
- 0.617 engine 2024: "Withholding important feedback hurts both our team members and our business."  
  ↳ coinbase culturedoc: "When we withhold these thoughts, we rob the team of our wisdom and fail to make them better."
- 0.613 engine 2026: "Bringing corporate positions on social or political issues into the workplace, however well-intentioned, creat"  
  ↳ coinbase culturedoc: "We refrain from debating issues or advocating for causes unrelated to our mission or business objectives at wo"
- 0.610 engine 2019: "We experiment, get creative, and view every step as an opportunity to learn."  
  ↳ coinbase culturedoc: "We strive to become excellent at failure — and work to extract the lesson from every misstep."
- 0.608 engine 2026: "We do not soften messages to protect feelings at the expense of clarity."  
  ↳ coinbase culturedoc: "We would rather share information that makes people a tad uncomfortable than withhold it to protect feelings, "
- 0.604 engine 2019: "We act on opportunity as a calculated risk outweighs never acting at all."  
  ↳ coinbase culturedoc: "We make calculated bets and always look to the horizon to see what we can build next."

## dream_team removal analysis

Sentences currently attributed to dream_team (>=0.5), with their next-best concept:

- 0.597 salesforce 2017: "We have the privilege of collaborating every day with talented, passionate teammates, and we genuine" → DROPS below floor
- 0.595 shopify 2010: "You'll be working in an amazing team with tons of benefits and perks." → DROPS below floor
- 0.593 salesforce 2016: "We work with talented, passionate people." → only_the_best 0.56
- 0.583 snap 2025: "We believe in hiring the most talented team members and creating an environment where everyone belon" → only_the_best 0.55
- 0.579 shopify 2017: "The strength of our teams is built on an incredible diversity of perspectives, backgrounds, and tale" → only_the_best 0.54
- 0.568 stripe 2017: "We want to work in a company of warm, inclusive people who treat their colleagues exceptionally well" → DROPS below floor
- 0.567 stripe 2019: "We want to work in a company of deeply good people who treat their colleagues exceptionally well." → DROPS below floor
- 0.558 google 2012: "We put great stock in our employees–energetic, passionate people from diverse backgrounds with creat" → only_the_best 0.54
- 0.554 coinbase 2018: "To achieve this, we are building a team of smart, creative, passionate optimists, the kind of people" → DROPS below floor
- 0.548 hubspot 2020: "We're building a culture at HubSpot where amazing people (like you) can do their best work." → DROPS below floor
- 0.546 airbnb 2015: "We build the best experience for our community - as a team." → DROPS below floor
- 0.545 google 2000: "Intelligent, fun, talented, hard working, high energy teammates." → only_the_best 0.51
- 0.540 salesforce 2025: "Here, you’ll work with teammates who challenge you, support you, and genuinely want to see you succe" → DROPS below floor
- 0.538 snap 2024: "We are a diverse team of designers, engineers, marketers, brand strategists, and so much more—all wo" → DROPS below floor
- 0.532 coinbase 2021: "We’re a team of smart, creative, optimists — the kind of people who see opportunity where others see" → DROPS below floor
- 0.529 shopify 2023: "Joining our team means working with the most driven crafters who pursue mastery." → DROPS below floor
- 0.526 coinbase 2022: "We’re a team of smart, creative optimists — the kind of people who see opportunity where others see " → DROPS below floor
- 0.522 shopify 2015: "You'll get a chance to work on challenging problems with some of the industry’s best and brightest." → DROPS below floor
- 0.521 stripe 2020: "We want to work in a company of warm, inclusive people who treat their colleagues well." → DROPS below floor
- 0.521 salesforce 2025: "You’ll find a team that values collaboration, celebrates wins, and balances precision with purpose." → DROPS below floor
- 0.519 airbnb 2024: "Work alongside industry-leading talent and be part of our vibrant network, encompassing people from " → DROPS below floor
- 0.517 salesforce 2020: "And we’re on a mission to build the most innovative teams in the world that reflect the communities " → DROPS below floor
- 0.513 github 2022: "We are dedicated to building a community and team that reflects the world we live in and pushes the " → DROPS below floor
- 0.511 shopify 2014: "You’ll get a chance to work on challenging problems with some of the industry’s best and brightest." → DROPS below floor
- 0.506 salesforce 2013: "Our team sport culture drives our rapid growth and creates a #dreamjob experience for nearly 10,000 " → DROPS below floor
- 0.504 salesforce 2006: "Everyone from the founders to our most recent hires, work as a team to create, market, and sell a su" → DROPS below floor
- 0.503 hubspot 2015: "We're building a once and a lifetime company and we want you to be apart of it." → DROPS below floor
- 0.501 airbnb 2019: "It’s an audacious, incredibly rewarding mission that our increasingly diverse team is dedicated to a" → DROPS below floor
- 0.501 google 1999: "Intelligent, fun, talented, hard-working, high-energy teammates In the center of the Silicon Valley " → DROPS below floor
