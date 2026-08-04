# Dark Places

_Draft v4 — 2026-08-03, Becca's rewrite. Links restored and instrument
numbers synced to the prompt-v3 extraction run (2026-08-03, PRE-VALIDATION —
they will move again with the final prompt and the hand-label gate).
Fact-check list at the bottom._

_Content note: this post quotes anti-migrant, anti-Roma, and anti-trans
rhetoric verbatim, including dehumanizing language and a slur for Roma
people. The quotes are the evidence, so I've kept them exact rather than
paraphrasing._

In my last post, I attempted to measure "masculine energy". I scored my
whole corpus of company careers page text on a gender axis and ranked which
companies lean the hardest on masculine-coded language. But here's the
question I couldn't stop thinking about: why does this matter? Sure, the
performative toughness rubs me the wrong way sometimes, but even I, the
woman with a whole shelf full of feminist writers, have to admit that
masculinity in and of itself isn't a bad thing. Building, moving decisively,
and communicating clearly are usually good things to do at work regardless
of your gender identity.

In that post, I made a note of a company that seemed to be a bit of an
outlier, and it has been bugging me ever since. So I did some more research.

37signals is small, but influential in the tech industry. (The company went
by Basecamp from 2014 to 2022, after its flagship product, which is why all
the contemporaneous coverage of what follows says Basecamp.) Co-founder and
CTO David Heinemeier Hansson (often referred to just as DHH) was the creator
of Ruby on Rails, a widely used framework for building web applications.
Both Hansson and co-founder Jason Fried have published books on their
workplace culture, and clearly consider themselves to be a model for the
entire industry.

Particularly in Chicago (where I'm from), 37signals was always considered
one of the best places to work, which is why the company's trajectory in
2021 surprised me. For those of you who are not chronically online tech
workers, let me summarize.

## The rupture

In early 2021, 37signals employees launched a DEI initiative. Employees were
particularly concerned about a list of "funny" customer names that had
circulated internally for over a decade, and about a third of the company's
57 employees volunteered to join the initiative and discuss issues like this
one. Two employees did a write-up on the list of names that referenced the
Anti-Defamation League's
["Pyramid of Hate"](https://www.adl.org/resources/tools-and-strategies/pyramid-hate)
concept, which argues that poking fun at people from different cultures and
ethnicities may not be immediately harmful, but it can lay the groundwork
for hate speech, discrimination, or worse.

Hansson's response, as reported in detail by
[The Verge](https://www.theverge.com/2021/4/27/22406673/basecamp-political-speech-policy-controversy),
acknowledged that management had failed to act on the list for years, but
also objected to the Pyramid of Hate as catastrophizing. He dug up old chat
logs to show that one of the complaining employees had once participated in
the list themselves.

Rather than listening to employees' concerns and continuing to work to
resolve this tension internally, Fried and Hansson decided to roll out a
public-facing policy change that became a primary topic of conversation in
the tech world for weeks. In April 2021, Jason Fried published a blog post
entitled
["Changes at Basecamp"](https://world.hey.com/jason/changes-at-basecamp-7f32afc5)
that said:

> "No more societal and political discussions on our company Basecamp
> account. [...] It's become too much. It's a major distraction. It saps our
> energy, and redirects our dialog towards dark places."

They also disbanded the DEI committee, cut "paternalistic" benefits, and
offered a buyout for anyone who disagreed. Around 20 of the company's 57
employees took it
([New York Times](https://www.nytimes.com/2021/04/30/technology/basecamp-politics-ban-resignations.html)) —
including the head of design, the head of marketing, the head of customer
support, and most of the iOS team. At the
[final all-hands](https://www.theverge.com/2021/5/3/22418208/basecamp-all-hands-meeting-employee-resignations-buyouts-implosion),
Ryan Singer, the head of strategy and an eighteen-year veteran, was
suspended after disputing whether "white supremacy" belonged in a
conversation about the company's culture, and then resigned. Casey Newton at
Platformer has
[the fullest account](https://www.platformer.news/-how-basecamp-blew-up/).

So in other words, employees brought up concerns about racial stereotypes
inside 37signals, and rather than listen, engage, and revise internal
practices, the founders shut down the conversation by publicly airing their
issues and banning political conversations at work.

## The outlier

37signals has shown up as an outlier in my research a couple of times now.
Despite the size of the company, the founders have—to put it lightly—a lot
of opinions. So they have given me one of the largest corpora in my dataset,
the fifth-largest of over twenty companies. Despite the sheer amount of
writing they have done about their company culture, their technical
practices, and how they set themselves apart from the rest of the tech
industry, they have been largely silent on the topic of diversity and
inclusion. Only four percent of 37signals' chunks mention it, as opposed to
26-52% for the other four companies of comparable corpus size. Only Coinbase
and Palantir scored lower, and that was true even before 37signals disbanded
the DEI committee in 2021.

[CHART: corpus size vs. share of DEI-register language, all 20 companies,
37signals/Coinbase/Palantir highlighted — data in
`astro/src/data/stories/dei.json`]

They also rank second, next to Anduril (a literal weapons manufacturer) as
the most masculine-coded company in my corpus, ahead of SpaceX and Palantir.
Most likely this is because so much of the cultural canon was written by the
founders themselves and not by recruiters or HR teams.

## The "non-political workplace"

Jason Fried's 2021 memo stated that they were concerned about their dialog
going to "dark places", but I don't think they were aware yet of the irony
of this statement. As a part of my research for this story, I scraped all
512 posts from Hansson's 37signals-hosted blog. Just in the last 8 weeks,
Hansson has brought us some gems such as: "The Rape of Britain." "Three
sacred cows that must die so Europe can live." "European Delusions & Danish
Drones." "Wolves, sheep, and gypsies." That last one, captured on July 21,
builds an extended analogy between Denmark's wolf population and Roma people
in Copenhagen, and ends:

> "When wolves get out of control, you shoot them. When gypsies take over
> public spaces, you deport them. This isn't hard, it isn't cruel. It's the
> basic logic of self-preservation."

So much for the "non-political workplace". Using his company's platform to
say that Roma people should be deported from the places they have lived for
centuries is a discussion about cultural groups and government affairs —
which is the definition of political speech.

I should note at this point that the rules about political speech at
37signals have never explicitly included the founders' blog posts. But in
this two-tiered system, they have created a dynamic where the company
leaders are allowed to disparage marginalized groups in public, and their
employees aren't allowed to say anything about it in the group chat.

## The shift

In order to better understand what happened after 2021, I ran an instrument
over every post to extract references to marginalized groups. This surfaced
references to Roma, Muslims, trans people, and other groups. It also codes
the tone of the reference—is it a neutral call-out, general hostility, or
does it frame these groups as a threat? (Every extracted quote is
machine-checked as a verbatim substring of the post, and I'm hand-labeling a
blind sample before I trust these counts; the numbers below are the current
pre-validation run.)

In 2021, exactly one post mentions any marginalized group — a neutral aside
about the Black Panthers — and nothing is hostile. In 2022 and 2023, a
handful of posts do, but none frame a group as a threat. In 2024, he starts
citing statistics (with an unclear source) about migrants and crime rates in
Denmark and Sweden.

> They went with an open-door policy on immigration for far longer, ended up
> taking many more (about 3x Denmark), and are now in a world of hurt with
> the highest gun-murder rate in all of Europe, along with an overall crime
> rate 50% greater than Denmark.

2024 is also when the blog starts in on trans people — first as punchlines,
then as a threat to what one post title calls "The endangered state of
normality." By February 2025 he's writing about "the trans mania" and "men
who said they were women"; by June, a post about his children's school in
Copenhagen describes a gender-ideology "obsession" that has "ravaged many
schools in America" and calls a student gender-and-sexuality club "overt
indoctrination." That post is one of the two that the Plan Vert open letter
(more on that below) would later cite.

In 2025, seventeen posts reference marginalized groups—nine of them are
about migrants or refugees, and eleven of the seventeen reference crime or
call for their removal. And in 2026 so far, all four referencing posts are
threat-framed, and Roma appear for the first time. A July post endorses
"remigration" by name: "millions who are already in Europe must go." That
word has a specific home in European identitarian politics, and it's a
favorite topic of the online far-right.

His references to migrants have increased even as his blogging cadence has
slowed, so the share of his posts about marginalized people has risen from
both directions at once. His writing went from slightly self-righteous tech
founder to overtly hostile to marginalized groups in about thirty
months—this is radicalization happening in real-time.

## The network

The no-politics memo didn't appear independently at two companies seven
months apart. The people who wrote these documents know each other, and have
for a long time.

Two of the names in this timeline may need an introduction. Tobi Lütke is
the co-founder and CEO of Shopify, the Canadian e-commerce company whose
software runs millions of online stores. Before he was a CEO he was a Rails
programmer: in 2004 he built Snowdevil, the online snowboard shop that
became Shopify, on a pre-release version of Rails, and he served on the
framework's early core team. He and Hansson have been in each other's
professional orbit for as long as Rails has existed. Brian Armstrong is the
co-founder and CEO of Coinbase, the largest cryptocurrency exchange in the
US.

**February 2017.** Tobi Lütke publishes an open letter refusing demands that
Shopify drop Breitbart's online store, framing the refusal as a free-speech
principle
([Globe and Mail](https://www.theglobeandmail.com/report-on-business/shopify-faces-increased-pressure-over-refusal-to-drop-breitbart-webstore/article33973253/),
[BetaKit](https://betakit.com/ceo-tobi-lutke-responds-to-petition-asking-shopify-to-stop-powering-breitbart-store/)).
This is the earliest "we don't do politics, we do commerce" document in my
whole dataset — three and a half years before anyone else in the cohort.

**September 2020.** Brian Armstrong publishes "Coinbase is a mission focused
company," barring societal and political debate at work. Days later he
offers severance to employees who disagree
([CNBC](https://www.cnbc.com/2020/09/30/coinbase-ceo-offers-severance-to-employees-leaving-over-politics.html));
about 60 people, 5% of the company, take it
([Fortune](https://fortune.com/2020/10/09/coinbase-says-60-employees-are-leaving-over-its-apolitical-stance)).

**April 2021.** Fried and Hansson follow with "Changes at Basecamp," seven
months later, with the same structure: no politics where the work happens,
exit packages for dissenters.

**January 31, 2022.** Lütke joins Coinbase's board
([Coinbase's announcement](https://www.coinbase.com/blog/tobias-lutke-ceo-of-shopify-to-join-coinbase-board-of-directors)).
The stated rationale is crypto and commerce: Lütke calls it a "like-minded
vision" of Web3 and entrepreneurship.

**November 19, 2024.** Hansson joins Shopify's board
([Shopify's announcement](https://www.shopify.com/news/david-heinemeier-hansson-board)).
Twenty years after Snowdevil, Hansson titled his own announcement
["20 years in the making."](https://world.hey.com/dhh/joining-the-shopify-board-of-directors-3c351fbb)

**September 2025.** An open letter
([Plan Vert](https://github.com/Plan-Vert/open-letter)) asks Ruby and Rails
institutions to cut ties with Hansson over what it calls his "racist and
transphobic views." Lütke publicly dismisses it
([contemporaneous account](https://po-ru.com/2026/07/29/it-doesnt-matter-whether-matz-is-nice)).
David Celis, a longtime Rails contributor, documents the escalation and
[calls for new Rails governance](https://davidcel.is/articles/rails-needs-new-governance).

**July 2026.** The same month Hansson publishes the wolves post, Lütke
replies "Good system" to a proposal giving five votes to people paying
$500k+ in taxes and zero votes to people paying none, then adds that
pensioners are dependents and "that means no voting"
([CBC](https://www.cbc.ca/news/canada/shopify-ceo-appears-to-endorse-giving-more-votes-to-wealthy-canadians-9.7286688),
[Fortune](https://fortune.com/2026/07/27/shopify-ceo-voting-rights-stripping-americans-19th-century/)).

## The syllabus

As for where Hansson got these ideas, we don't have to wonder. He told the
story himself last week on David Senra's _Founders_ podcast (episode posted
July 26, 2026), summarized in
[this X post](https://x.com/davidsenra/status/2081956616963006913) of the
key clip. In his telling: after the 2021 exodus, with tens of thousands of
people criticizing him on Twitter, it was Tobi Lütke who put him in contact
with Marc Andreessen — Andreessen had seen the same "phenomenon" at his
portfolio companies. Andreessen offered reassurance, contacts, and
operational help, and urged him not to apologize or revert.

And then, in Hansson's words, Andreessen "gave me a syllabus for
understanding the history of wokeness" — the Frankfurt School, Herbert
Marcuse, a decades-long plot against Western institutions. By the end of the
clip, Hansson is describing his employees' DEI concerns as part of a
civilizational battle against "the white walkers beyond the wall."

## The fascism of it all

It's clear that 37signals, like a large portion of the tech industry, has a
bit of a fascism problem right now. Hansson isn't the first tech founder to
face pushback and then court white supremacy and far-right extremism; it's a
known pattern. But why does it feel so important to me specifically?

Well, I think it means that my pattern-matching is working. Masculine-coded
language on your careers page could be neutral, or it could be a signal of a
lack of consideration for different groups who could be reading it.
Political neutrality could be a genuine call for workplace professionalism,
or it could be a way of silencing employees who are raising concerns. When I
see these two signals together, it often means there is more extremism
lurking beneath the surface.

Ironically, the framework that describes this the best is the one that
triggered Hansson's far-right swing: The Pyramid of Hate. Subtle biases that
are allowed to propagate lay the groundwork for more extreme speech,
discrimination, and violence. Hansson was given an opportunity to grapple
with this. But rather than acknowledging the pyramid, he decided to ascend
it.

---

_Fact-check status (updated 2026-08-03):_

1. _Group-reference numbers in "The shift" are from the PROMPT V3 run
   (data/dhh_blog/group_references.json, generated 2026-08-03T05:46Z,
   41 refposts/108 refs) and are PRE-VALIDATION. The prompt is being
   iterated (v1→v3 in two days; counts moved each time) — re-derive every
   number from the final run after the hand-label gate before publishing.
   v3 year table: 2021 1 refpost (neutral)/0 hostile; 2022 7/0; 2023 2/0;
   2024 10 refposts, 1 threat + 2 hostile; 2025 17 refposts, 9 migrants,
   11 threat; 2026 4/4 threat._
2. _"20 of 57 volunteered" changed to "about a third" — Platformer supports
   only "a third," and notes the volunteers and the ~20 who left are NOT the
   same people. Departures "around 20 of 57" confirmed (NYT, Platformer).
   Benefits-cut detail verified against our capture of the memo._
3. _Coinbase timeline entry: severance was NOT in the Sept 2020 post
   (verified against our canon capture) — it came days later by email
   (CNBC), ~60 people/5% took it (Fortune). Entry restored to the two-step
   sequence with cites._
4. _2024 stats sentence: the quoted crime statistics are about SWEDEN
   (compared to Denmark) — wording adjusted to "Denmark and Sweden." STILL
   OPEN: the "(with an unclear source)" aside — confirm the fairytale post
   really cites no source before publishing that parenthetical._
5. _Anti-trans thread (added 2026-08-03, v3 data): first hostile codings
   2024-04-25 ("The gift of ambition," a Babylon Bee joke — weakest coding,
   deliberately not quoted) and 2024-05-14 ("The endangered state of
   normality," quoted by title only). Quotes verified verbatim in v3
   extractions: "the trans mania" / "men who said they were women"
   (2025-02-15), "ravaged many schools in America" / "overt indoctrination"
   (2025-06-03 CIS post). CIS post = one of the two cited by Plan Vert
   (per heise coverage of the letter)._
6. _Roma tenure: changed "thousands of years" to "centuries" — Roma
   presence in Europe dates to roughly the 14th century._
7. _Plan Vert: primary source is github.com/Plan-Vert/open-letter (Sept
   2025, ~300 signatories); exact wording verified: "holds racist and
   transphobic views." STILL OPEN: Lütke's dismissal is sourced to a
   secondary account (po-ru.com) — pull his actual post before publishing._
8. _Senra podcast: X-post text captured to
   data/dhh_blog/external/senra_founders_x_clip_2026-07-28.md. STILL OPEN:
   transcription is Senra's — check quotes against episode audio, and
   screenshot the X post._
9. _DEI-share numbers in "The outlier" (4% vs 26–52%, fifth-largest corpus;
   Coinbase/Palantir lower): computed 2026-08-02 from
   astro/src/data/stories/dei.json. Re-run after any corpus refresh; build
   the chart from the same file._
10. _Lütke bio: co-founder/CEO (NOT board chair); Snowdevil 2004 on
   pre-release Rails; early Rails core team confirmed across multiple
   independent bios. "Millions of online stores" is Shopify's own merchant
   count._
