---
layout: post
tags: agile development systems-engineering
#categories: []
date: 2026-04-30
last_updated:
#excerpt: ''
#image:
#description:
#permalink:
title: 'The Skateboard To Car Metaphor Is A Poor Mental Model for Vertical Slices'
#
#
# Make sure this image is correct !!!
og_image: not-like-this.png
#
#
# make sure comments are enabled
comments_id: 
math: false
---

It's been one too many times that I've seen the famous _skateboard, scooter, bike,
motorcycle, and car_ [image](https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp)
by Henrik Kniberg about agile product development and I needed to know what irked
me about that so much. Follow me for a deep dive that goes beyond the obvious and
shallow "car manufacturer didn't use to build skateboards"
critique. That requires some digging, because the original article contains great
insights and examples, but I'll still argue that the mental image underlying the
metaphor doesn't work to guide _development_.

Let's remind ourselves of the (in)famous image quickly before we go further.

<figure>
 <img src="/blog/images/mvp/kniberg-mvp.png" alt="Kniberg's Illustration" style="width:100%">
   <figcaption> Kniberg's original illustration from <a href="https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp">this article</a>. He writes "The picture is a metaphor. It is not about actual car development, it is about product development in general, using a car as a metaphor."</figcaption>
</figure>

This illustrates the key metaphor presented in the article. Attacking a
metaphor always runs the risk of attacking a strawman by taking the metaphor
too literally. I'll try my best not to do that. But what I  _can_ do is critically
evaluate the mental model that underlies the metaphor. A mental model guides our 
thinking and consequently our decision making. That's why, if it is flawed, it can lead 
us to make bad decisions.

## The Good

At its core, the original article argues that rather than building 
incomplete pieces of a grand vision, start with a simple solution that already 
delivers real user value. Evolve testable, usable, lovable versions through 
feedback. This avoids wasted effort and leads to a better product than executing a 
fixed upfront plan.

Kniberg's argument is very strong when we see the iterative understanding
and subsequent addressing of the actual user needs as the guiding principle.
We all know the _"If I had asked people what they
wanted, they would have said faster horses"_ quote often attributed to Henry Ford[^henry-ford-quote]
and there's much wisdom in it. Continuous feedback informing us on how aligned
we are with the user needs is indeed invaluable. I think as a
framework for _product discovery_ this is great. It also shines when
used as a mental model for getting us to actually commit to an earliest
testable/usable/lovable/... version of a product. This prevents us from optimizing
something to death in an ivory tower.

## Digging Deeper

<figure>
 <img src="/blog/images/mvp/pepe-silvia.jpg" alt="Pepe Silvia Meme" style="width:50%">
   <figcaption> Me, obsessing over the skateboard metaphor.</figcaption>
</figure>

And yet, something just feels off to me about this skateboard to car
metaphor. Of course! No car manufacturer started with a
skateboard, right? Sure, but that's just taking the metaphor uncharitably
literally. So does the skateboard just mean _simpler car_? That also feels
wrong. In Kniberg's article the skateboard is described to the customer
by saying "don't worry [...] We’re still aiming to build a car, but in the meantime please
try this and give us feedback". So the metaphorical skateboard _is_ a stepping
stone on the way to a car.

In the article, the first thing that the customer would get delivered
in the _Not Like This_ section is a single wheel of a car, which is of no use
to them. In the _Like This_ section, a skateboard is shipped to them. They are potentially
not happy about it, but it's definitely something that they can use and
provide feedback on. So _usable_ is one important property of a metaphorical skateboard.
Obviously, it's also _simpler_ than a (metaphorical) car. And thirdly, it's
_self contained_. It's not a _partial_ car, in fact: it's not even _part of a car_!
You _could_ give a partial car to users to test it, and as a matter of fact that's
pretty much what I'll argue later, but still Kniberg chose to go with skateboard.
Those notions of self-containedness (is that a word?) and independence
are where, I believe, things start to unravel.

Let's dig into the examples in his text and see if we can understand what
Kniberg could mean by skateboard...

### The Examples

I'll try to keep this short, because this is shaping up to be a long article, but we do
need to talk about the examples in the original article briefly. For the Spotify
example Kniberg writes: 

> "developers basically sat down and hacked up a technical prototype, put in
> whatever ripped music they had on their laptops, and started experimenting
> wildly to find ways to make playback fast and stable"

He goes on to explain that they focused on the singular metric of latency to
make the product viable and used friends and family to test it. I can definitely
see that this is pretty far from what Spotify is today (or even at the time the
article was written), but why not just leave it at prototype? Is a skateboard
a prototype for a car? Hardly. I'd argue the same is true for the minecraft
example presented in the article [^minecraft].

The Big Government example in the original article is a great case study of 
how they released a very narrowly scoped initial version (with respect to both 
capabilities and distribution) and built on the gathered feedback. However, again I 
don't see how that first version is a skateboard except for it being a much 
simpler, stripped-down version compared to the releases that came after. But again, 
a skateboard is not a simpler car, it's not a partial car, it's not part of a car.

All this is to say that the examples in the text are excellent examples of good
development practices that led to great products, but none of this has anything
to do with the skateboard-to-car mental model and all to do with vertical integrations.

## A Skateboard Isn't a Simpler Car...

it's a simpler _mode of transportation!_ I hear you shout at your screen, shaking your copy of
the Agile Manifesto at it. But let's think about it. The Spotify "skateboard" was 
built around specific commitments in the realm of low-latency music streaming.
Later increments were built on top of those commitments, not independently from
them. Same for the other examples. A skateboard doesn't share the foundational
principles with a car, whereas a vertical slice does.

One principle that I strongly believe is that successful development needs clear
constraints. Just think of practical reasons like hiring decisions, funding rounds,
technology choices and the like[^mode-of-transport]. A concrete vision helps by
constraining the solution spaces you'll explore. And exploration doesn't come for free.
And yes, do get user feedback early and often, because it will help you align
your vision with user needs. 

So sure, in the most charitable interpretation, the skateboard just means to start
simple and get early user feedback. None of this is objectionable, but I'd argue
it's also not very helpful for planning actual development[^big-bang]. Kniberg
writes "Think big, but deliver in small functionally viable increments". I agree
whole-heartedly, but the skateboard metaphor is a very bad way of illustrating
_how_ to do that. One big problem with that article is it does present the idea
of functionally viable increments without addressing how to 
go from one step to the next systematically, other than getting user feedback. 

Say you've identified your (metaphorical) skateboard, which
although less complex than a (metaphorical) car, will likely be a product of decent
complexity. It'll take requirements analysis, architecture decisions, actual engineering
work, and much more. This is where a lot of the complexity lies. More than that,
the skateboard to car metaphor implies a harmful level of independence of earlier
and later versions. In reality, architectural decisions will compound and components
will be shared across iterations. In that sense, the metaphor doesn't just fail
as a guide for development, it actively points in the wrong direction[^potentially-shippable].

## A Better Development Model: Vertical Slices

One last time, let's revisit Kniberg's examples again. What do they
actually represent? They are _thin vertical
slices_, which are a "narrow but complete sliver of the final product vision"[^vertical].
They are all highly incomplete and/or narrowly scoped when compared
against their later versions, but all examples show a high level of
_vertical integration_, meaning a lot of system components from top to bottom
have to work together. Let's check how a vertical slice compares to the
key properties of the (metaphorical) skateboard we identified above.

Are vertical slices usable? Yes they are, though I much prefer _testable_,
as Kniberg does, too. That's actually one of their major benefits. A vertical
slice through a complex system means that many modules will have to work
together successfully. Thus, you really get to pressure test those interfaces,
which is where a lot of the breaking points of a system are. Sure, it's easy
for a team to deliver a brilliantly polished module, but that's worthless
without seeing if their assumptions and the formal interface specifications
(you _do_ have those, right?) hold up in reality. Fail early here and iterate,
to save yourself a lot of costly reworks later.

Are vertical slices _simpler_ than what comes after? Of course! Are they
_self contained_? In a way, yes. But to me, that's more a consequence of them
being vertical slices. They definitely aren't what a skateboard is to a car
and we should all free ourselves from the idea that incremental versions have a high
degree of independence. Your versions _of course_
won't be independent from each other, _that's the whole point_! You're building
something incrementally. Thinking of vertical slices helps us remember that 
we are iterating towards a (possibly evolving) vision incrementally rather
than building solutions of increasing complexity independently from each other.
Vertical slices make it clear that the decisions you make in
the early stages will have an impact on the later stages. Vertical slices
aren't a new idea and spelled out like this, all of this may sound banal and yet
the skateboard-to-car metaphor exists. This article isn't about inventing a
new development practice. It's pointing out what Kniberg's examples already show,
and arguing that the popular skateboard to car metaphor obscures a better mental model.

And now for the final question: does this mental model help us plan development?
Absolutely. If we prioritize verticals, then this helps us slice our work
into manageable chunks. Prioritize narrow goals which require high vertical
integration and work towards them, but don't stress about sprints or
potentially shippable products. Vertical slices force end-to-end integration and
thus requirements have to be concrete enough to implement, interfaces have
to be specified _and actually used_, and foundational architectural decisions
can't be deferred. This allows you to test internally, both manually and
automatically (ideally through all levels of integration), catch wrong assumptions fast
and when it's still cheap to correct them, and ultimately deliver a product early.

## Conclusion

The examples in Kniberg's original article are all excellent illustrations
of good development practices. What made them work wasn't the skateboard,
it was the fact that the early releases were all thin, integrated vertical
slices. Gathering early user feedback was used to inform future iterations,
which incrementally built on the engineering decisions in their predecessors.
The skateboard metaphor obscures that last part. If you think "skateboard",
it's easy to forget that earlier versions lay the groundwork for their
successive increments.

Think "vertical slices" instead. They are simpler, testable, and most importantly
you'll be forced to make decisions that lay the groundwork for subsequent
increments. To my mind, that's a better mental model of a good incremental
development process, and one that's both well-known and worth repeating.

## Endnotes

[^henry-ford-quote]: While it _is true_ that the quote is often attributed to Ford, there's [no evidence](https://www.snopes.com/news/2025/02/23/horses-quote-henry-ford/) of him actually saying it. But _"never let the truth get in the way of a good story"_ --Mark Twain, or was it...?
[^big-bang]: I'll extend an olive branch here and say that there truly are people who try to design the perfect product in their ivory tower, and yes, those people will most likely never release _anything_, let alone anything that anyone actually wants.
[^vertical]: Quote from Richin Jose: "How not to build an MVP: The Flawed 'Skateboard to Car' Analogy" [here](https://richinjose.medium.com/how-not-to-build-an-mvp-the-flawed-skateboard-to-car-analogy-4920a845f151). The article goes on to compare the MVP to a thin slice of layered cake, rather than delivering the whole top layer of frosting. Very tasty mental image, but doesn't work one bit as a development metaphor, since we'd have to bake the whole cake to deliver a slice...
[^potentially-shippable]: I had a whole rant about how this ties into the whole _potentially shippable product_ that's still echoing in the agile world. But I'll leave it at that and present what I think is a better mental model to inform our development and one that still helps us gather feedback. Because, mind you, that whole getting-feedback-thingy is still great. I went down a rabbit hole trying to find the origins of the potentially releasable product phrasing. I looked in various editions of the Scrum guide. The [2013 guide](https://scrumguides.org/docs/scrumguide/v1/Scrum-Guide-US.pdf) speaks of the "potentially releasable increment", which is pretty close. The [2020 guide](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf) has notably softened the language to: "In order to provide value, the Increment must be usable". While that language sure is mellower, the whole idea is still echoing in agile circles today and I don't think that it's doing anyone any good. See [here](https://www.visual-paradigm.com/scrum/sprint-increment-potential-shippable-mvp-mmp/) or [here](https://staragile.com/blog/potentially-shippable-product) for pretty recent references to the terminology.
[^mode-of-transport]: Cut to all AI and DeFi companies with hundreds of millions in funding and absolutely no concrete vision other than to "revolutionize" finance, intelligence—you name it...
[^better]: Where _better_ is measured by the degree to which the user needs and requirements are satisfied.
[^minecraft]: The skateboard of Minecraft is described as:  "You couldn't do much in the first version – it was basically an ugly blocky 3d-landscape where you can dig up blocks and place them elsewhere to build crude structures.". Surely a simpler version, but does this version of Minecraft (as described) have the same relation to modern Minecraft as a skateboard has to a car? Why not leave it at prototype here as well? If the core point is that this version was playable and testable, I still think that the skateboard isn't a good metaphor.
[^lego]: Except for the lego example, where he explicitly admits that he doesn't even know where the skateboard is, but he does emphasize the importance of early user feedback. For good measure, he throws in another Lego example that didn't have a skateboard and subsequently failed...I guess that the point of that section is to say that the successful development did incorporate early user feedback, while the failed one did not. Sure, but what's that got to do with skateboards?
