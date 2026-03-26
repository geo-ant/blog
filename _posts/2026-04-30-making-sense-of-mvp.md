---
layout: post
tags: agile development
#categories: []
date: 2026-04-30
last_updated:
#excerpt: ''
#image:
#description:
#permalink:
title: 'The Agile MVP: The Problem with Skateboards, Bikes, and Cars'
#
#
# Make sure this image is correct !!!
og_image: 
#
#
# make sure comments are enabled
comments_id: 
math: false
---

It's been one too many times that I've seen the famous _skateboard, scooter, bike,
motorcycle, and car_ [image](https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp)
by Henrik Kniberg about agile product development. Something happened and I
needed to know what irked me about that image so much. Follow me for a deep
dive that goes way beyond the obvious (and dumb) "skateboards don't become cars"
critique. That requires some digging, because the core idea is great
when viewed from certain perspectives, but I'll argue it's horrible when
taken as an actual _development_ metaphor.

Before we get into my thoughts, let's remind ourselves of the original image
and then jump into the parts of Kniberg's argument that I actually like.

<figure>
 <img src="/blog/images/mvp/kniberg-mvp.png" alt="Kniberg's Illustration" style="width:100%">
   <figcaption> Kniberg's original illustration from <a href="https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp">this article</a>: "The picture is a metaphor. It is not about actual car development, it is about product development in general, using a car as a metaphor."</figcaption>
</figure>

## The Good

I don't want to focus on the image alone too much because as Kniberg states, it's just
a metaphor, so let me also give a very brief summary of the article stripped
to its core message: Rather than building incomplete pieces of a larger vision,
start with a simple solution that already delivers real user value. Evolve
testable, usable, lovable versions through feedback. This avoids wasted effort
and leads to a better product than executing a fixed upfront plan.

Knibergs argument is very strong when viewed through the lens of satisfying
your users' underlying needs. We all know the _"If I had asked people what they
wanted, they would have said faster horses"_ quote often attributed to Henry Ford[^henry-ford-quote]
and there's much wisdom in it. Continuos feedback informing us on how aligned
we are with the user needs is indeed invaluable. I think as a
framework for _product discovery_ this is great. It also shines when
used as a mental model for getting us to actually commit on an earliest
testable/usable/lovable/... version of a product. This prevents us from optimizing
something to death in an ivory tower.

## Digging Deeper
<figure>
 <img src="/blog/images/mvp/pepe-silvia.jpg" alt="Pepe Silvia Meme" style="width:50%">
   <figcaption> Me, obsessing over the skateboard metaphor.</figcaption>
</figure>

And yet, something just feels off to me about this skateboard to car
metaphor. What could it be? Of course! No car manufacturer started with a
skateboard, right? Yes, but that's just taking the metaphor uncharitably
literally. So does the skateboard just mean _simpler car_? That also feels
wrong. If Kniberg had wanted to say simpler car, he probably would have found
a better metaphor.

In the article, the first thing that the customer would get delivered
in the _Not Like This_ section is a single wheel of a car, which is obviously useless
to them. In the _Like This_ section, a skateboard is shipped to them. They are potentially
not happy about it, but it's definitely something that they can use and
provide feeback on. So _usable_ is one important property of a metaphorical skateboard.
Obviously, it's also _simpler_ than a (metaphorical) car. And thirdly, it's
_self contained_, since it's presented clearly in opposition to a partial car.
You _could_ give a partial car to users to test it, and as a matter of fact that's
pretty much what I'll argue later, but still Kniberg chose to go with skateboard.
This notion of self contained-ness (is that a word?) is where I believe things start to unravel.

Let's dig into the examples in his text and see if we can understand what
Kniberg could mean with skateboard...

### The Spotify Example

Kniberg writes: 

> "developers basically sat down and hacked up a technical prototype, put in
> whatever ripped music they had on their laptops, and started experimenting
> wildly to find ways to make playback fast and stable"

He goes on to explain that they focussed on the single metric of latency to
make the product viable and used friends and family to test it. I can definitely
see that this is pretty far from what Spotify is today (or even at the time the
article was written), but why not just leave it at prototype? Is a skateboard
a prototype for a car? Hardly.

### The Minecraft Example

Here, in one of the most baffling takes of the article, Kniberg describes the
skateboard of Minecraft as:

> "You couldn’t do much in the first version – it was basically an ugly
> blocky 3d-landscape where you can dig up blocks and place them elsewhere
> to build crude structures."

Isn't that... just Minecraft?? I'm not making any friends here, I know. And yes,
I'm being a bit facetious here, but can you honestly say that this first release
(as described) has the same relation to Minecraft as a skateboard has to a car?
I don't think so.

### Big Government Example

I'll keep it short, because this plays out as the examples above. I actually
like this example a lot because it shows how they released a very reduced
version (both in scope as well as distribution) and built on the gathered
feedback. But I don't see how that first version is a
skateboard other than it was a much simpler, stripped down version of
the releases that came after. Again, a skateboard is not a simpler car.

There's another example (Lego) in Kniberg's article, where he explicitly
admits that he doesn't even know where the skateboard is, but merely emphasizes
the importance of early user feedback. For good measure he throws in
another Lego example that didn't have a skateboard and subsequently failed...[^lego-worlds]


## A Skateboard Isn't a Simpler Car...

it's a simpler _mode of transportation!_ I hear you shout at your screen, shaking your copy of
the Agile Manifesto at it. And yes, in the most charitable interpretation, the
skateboard just means to get early feedback. And it tells us that the first versions of our
product are simpler than the later versions. None of this is objectionable,
but the fact that products start simple is also not very insightful[^big-bang].

I promise I'll be finished with the damn skateboard soon, but I need to make one
final point, which is that the whole metaphor is a horrible mental model for
development. Why? First of all, the process that brings us from nothing to a skateboard,
from a skateboard to a scooter and so on: that's _development_. And second of
all, now that we've established that, how does that mental model help to inform development?
It absolutely doesn't. Say you've somehow identified your (metaphorical) skateboard, which
although less complex than your (metaphorical) car, will likely be a product
of some complexity[^bus-ticket]. So how do you get from nothing to a skateboard? You don't.
This mental model will have you thinking about your skateboard's skateboard and that's
where it all breaks down. The whole mental model doesn't help to
inform your development at all. And if it can't inform development, it can't help
you get to a product of value. So there. That's my problem with that
mental model. I had a whole rant about how this ties into the whole _potientally
shippable product_ that's still echoing in the agile world, but I'll leave it
at that and try and present a better mental model that _can_ inform our development
and still help us gather feedback[^potentially-shippable]. Because, mind you,
that whole getting-feedback-thingy is still great.

## A Better Development Model: Verticals

So now that we've abandoned the skateboard-to-car mental model, let's revisit
Kniberg's examples again. So what are they actually? They are _thin vertical
slices_, which are a "narrow but complete sliver of the final product vision"
[^vertical]. They are all highly incomplete and/or narrowly scoped when compared
against their later versions, but all examples show a high level of
_vertical integration_, meaning a lot of system components from top to bottom
have to work together. Yes, it's kind of important that the thing is 

# TODO TODO TODO

!!! vertical integrations actually help you go somewhere incrementally.

!!!!!!!!!! I think part of the problem stems from the "potentially shippable product" idea.
While I don't think Kniberg argues that one can build a car in 4 sprints by first
building a skateboard, I believe the mental model is informed by this.

!!! why else would the products be so neat and finished in themselves.
!!! The graphic never shows an unfinished step
!!! Of course: in the most steelman version of readin the argument it's just
about building simpler things first. Of course! Nobody disagrees with that!
!!! There is practically no benefit in building a skateboard if what you want
to build is a car.

Henry ford quote (didn't actually say that): https://checkyourfact.com/2019/10/10/fact-check-henry-ford-quote-faster-horses/


!!! visual paradigm still references the term: https://www.visual-paradigm.com/scrum/sprint-increment-potential-shippable-mvp-mmp/
this agile site from 2024 still uses it: https://staragile.com/blog/potentially-shippable-product

!!! johner institute development process: https://blog.johner-institute.com/systems-engineering/development-process/

!!! Vertical integration vs potentially shippable: I think potentially shippable
product gets close to this idea but subtly misses the point. One way to get to a
PSP is via vertical integrations, but that's not the only one. I know the definition
of "delivers value"/"shippable" etc is fuzzy, but it's just as well to flesh
out the frontend of a web application and call that shippable without any vertical
integration to the backend. This might already feel super shippable but to my
mind misses the point, because I'd argue that the real value is in the vertical
integration. This will show you how your modules work together which is much
more valuable in the development process than constantly getting user feedback
on the frontend, which might lead you to optimize a frontend without ever getting
to the backend and actual functionality.

!!! "delivering a front tire sucks". HOWEVER: real development is MODULAR.
The idea that we can always ship something simple and from there go to something
more complex is highly problematic. Sometimes there are intermediate steps that
don't actually bring much user facing value. That's okay. The important thing
is to make sure that those modules play nicely during the development process
and the likely breaking points are the interfaces between modules, so we need
to INTEGRATE to expose those weaknesses.

!!! one button on a UI that actually leads to a backend call that leads to a
chain triggering a call into an almost empty backend database to retrieve some data, which
then passes through completely unfinished business processing logo to display
a dummy image on the UI is worth more than...

!!! thin vertical integrations > finished products

!!! "The skateboard to car metaphor is not a development metaphor": Whatever happens
between the release, that _is_ development. Those steps don't just magically appear
because there are just literally things that are too complex to be a simple addition
to one thing. This also kinda goes back to this "potentially releasable product"
stuff. Not everything fits in nice _n_-week sprints.

![Anti-Agile Development](/blog/images/mvp/mvp-illustration.png)

## Endnotes

[^ai-assist-drawing]: Full disclosure, I used Claude Opus 4.6 to generate this drawing for me, by prompting it to create an SVG. The idea is, of course, mine but I'm still not proud of the resulting image. If you're an artist and would like your image featured here, please contact me!
[^henry-ford-quote]: While it _is true_ that the quote is often attributed to Ford, there's [no evidence](https://www.snopes.com/news/2025/02/23/horses-quote-henry-ford/) of him actually saying it. But _"never let the truth get in the way of a good story"_ --Mark Twain, or was it...?
[^lego-worlds]: I guess that the point of the Lego section is to say that the successful development did incorporate early user feedback, while the failed one did not. Sure, but what's that got to do with skateboards?
[^big-bang]: I'll extend an olive branch here and I'll say that there truly are people that try to design the perfect product in their ivory tower and yes, those people will likely never release _anything_.
[^vertical]: Quote from Richin Jose: "How not to build an MVP: The Flawed 'Skateboard to Car' Analogy", [here](https://richinjose.medium.com/how-not-to-build-an-mvp-the-flawed-skateboard-to-car-analogy-4920a845f151). The article goes on to compare the MVP to thin slice of layered cake, rather than delivering the whole top layer of frosting. Very tasty mental image, but doesn't work one bit as a development metaphor, since we'd have to bake the whole cake to deliver a slice...
[^bus-ticket]: Say _bus ticket_. I dare you, I double dare you. Do we _really_ have to argue about the fact that there is no such thing as the (metaphorical) _bus ticket_?? The idea that there are always absolutely _trivial_ steps to go from one release to the next and the only thing that's missing is user feedback is just mind boggling to me and I don't actually think anyone would take it seriously. This is for sure not what Kniberg is arguing, but this _is_ the internet and there's probably one agile apologist out there getting ready to lecture me.
[^potentially-shippable]: I went down a rabbit hole trying to find the origins of the _potentially releasable product_ phrasing. I looked in various editions of the Scrum guide. The [2013 guide](https://scrumguides.org/docs/scrumguide/v1/Scrum-Guide-US.pdf) speaks of the "potentially releasable increment", which is basically the that. The [2020 guide](https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf) has notably softened the language to: "In order to provide value, the Increment must be usable". While that language sure is mellower, the _potentially releasable product_ is still echoing in agile circles today and I don't think that it's doing anyone any good.
