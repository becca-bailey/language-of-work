# The Death of Changing the World

As a job seeker, I have become a student of tech company careers pages. You know, those pages that always feature photos of smiling employees in matching t-shirts and use enthusiastic language to tell you why you should work there. Most companies use a lot of the real estate on this page to talk about their culture, which can be loosely defined as the things that make them special. Every tech company claims to have the best culture, at least for a specific kind of person.

For example, if you’re a smart, enthusiastic generalist who wants to change the world, you would probably feel at home at Google. If you care deeply about technical excellence, you probably belong at Stripe. If you want to move fast and break things, you probably already know that Meta is the place for you.

But in 2026, we have seen a lot of changes in the industry. Some companies rolled out DEI programs that they talked about extensively in their careers copy, only to roll them back a couple of years later when the political tides changed. Some companies that claimed to want to change the world have changed their tune now that it’s clear that most workers didn’t buy the over-the-top enthusiasm from billionaires who extract their fortunes through ad revenue. Companies like Palantir have recently dug in their heels on white supremacist-adjacent language like “We built Palantir to ensure the future of the West”. (For the uninitiated, “The West” is a common euphemism for white people and white culture.)

What does it all even mean anymore?

## An archaeological exploration of text

In order to better understand how companies talk about themselves, when it changes, and why it matters, I needed to gather some data. I decided to pull in a bunch of careers page copy from the Wayback Machine and analyze it. While manual text matching and encoding methods have existed for a long time, this kind of analysis work became accessible to me with the help of AI tools.

Some AI companies like OpenAI expose APIs for embeddings. At a high level, embeddings are vectors. You give the API a chunk of text, and it returns a long list of numeric values that can be used to determine the relationship between that text and another piece of text. For example, if you use cosine similarity to match the text “We want to change the world through technology” with the similarly altruistic statement “We think software can make the world a better place”, it would get a high score like 0.86 on a scale of 0 to 1 that indicates that it’s a close match. If I compared that same sentence to an opposing idea like “We exist to make as much money as possible despite the human cost”, the score would be much closer to zero.

In my case, however, I wanted to measure a semantic shift between ideas, not just surface similarity. I put opposing ideas like altruism vs. commercial pragmatism onto axes so I could track where language falls on a spectrum year over year, and therefore see how language evolved.

For example, Google’s idealism seemed to peak around 2014, shortly after the Owen Wilson/Vince Vaughn buddy comedy “The Internship” introduced the wider world to the term “Googlyness”.

## A deeper dive into the world of DEI

I also wanted to study diversity and inclusion language. How often do companies mention diversity, equity, or inclusion, and what kind of signal is it? Is it vague and aspirational, or does it mention specific goals for specific groups? (Spoiler alert: when it existed, most of the language was vague and aspirational).

> “Google should be a place where people from different backgrounds and experiences come to do their best work–a place where every Googler feels they belong. The truth is that we’re not there yet. We know diversity and inclusion are values critical to our success and future innovation. We also know challenging bias–inside and outside our walls–is the right thing to do.” - Google, 2017

This was a place where I didn’t just need to measure whether it was DEI language, but I needed to encode what kind of language it was. I used the Claude API to help me classify blocks of text. Of course, textual classification is a highly subjective process, so I included a process for manually checking and fine-tuning the classification prompts. For example, originally I found that Claude wasn’t differentiating between “we want to build a diverse workforce” and “we want to build the best product for a diverse customer base”. While both signal a general concern for diversity, the difference mattered to me.

For example, while Amazon has a large and diverse workforce that includes everyone from delivery drivers to warehouse workers to software engineers, Amazon’s diversity mentions were almost always about their customers, not their workers. One of the first mentions of worforce diversity in my dataset showed up for Amazon in 2026.

> “We track the representation of our workforce because we know that diversity helps us build the best possible customer experiences and products for our globally diverse customer base.” - Amazon, 2026

Once you factor out mentions of customer diversity, DEI language at Amazon is virtually non-existent, and Google’s clearly peaks early on.
Of course, I should note at this point that DEI language is not the same as real policies that support inclusion. It’s a signal, not a clear indication of good or bad working conditions for marginalized groups. But as a job seeker, it’s the kind of signal that matters to me, and determines whether or not I will apply to work at a company.

In this DEI study, I also wanted to include the “negative” DEI indicators, roughly defined as the language that makes me, as a woman in tech, less likely to apply. This includes both anti-DEI meritocracy language and “civilizational mission” language, best exemplified by Palantir’s many mentions of “The West”.

Once those counterforces are included, you can clearly see the general mood at Palantir, as well as the post-2020 ideological reversals that happened at both Coinbase and Shopify.

> “Our mission is ambitious and important. We don’t engage in social or political activism that is unrelated to our mission while at work. We seek to make the workplace a refuge from division, so we can stay focused on making progress toward the mission.” - Coinbase, 2025

## What does this say about worker power?

In order to measure this, I took the data from all the companies I studied and measured it on four axes that can be roughly defined as idealism, DEI language, well-being, and performance. I then overlaid that data with the JOLTS quit rate from the U.S. Bureau of Labor Statistics to get a rough measure of when workers had the most opportunity, and therefore, were more likely to quit. It’s not an exact science, but you can see definite patterns.

For example, Netflix has always maintained a high performance bar, but we can see definite drops in their idealism and well-being language that started right before the quit rate decreased.

If I zoom out and look at the average of all the companies I have studied so far, the pattern is less distinctive, but still present.

These patterns raise a deeper question: if career page language is just a reflection of labor market conditions, what does that tell us about how tech companies think about worker power—and how workers should think about their own? In 2026, you can’t trust what companies say about themselves. But you can trust the pattern of when they stop saying it. Cultural signaling doesn’t give workers power, but it merely reflects the level of power they already have.
