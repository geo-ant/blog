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

I've recently seen the famous _skateboard, scooter, bike, motorcycle, and car_
[image](https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp)
by Henrik Kniberg about agile product development one too many times and I snapped.
In the following, I'll explain what it is that irks me about that mental model
so much. That requires some digging, because the core idea is fantastic
when viewed from certain perspectives, and it's horrible when viewed through others.

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
and there's much truth to it. Continuos feedback informing us on how aligned
we are with the user needs is indeed invaluable. Additionally, I think as a
framework for _product discovery_ and actually committing on an
earliest testable/usable/lovable/... version of the product this mental model
absolutely shines.

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
_self contained_, it's presented clearly in opposition to a partial car.
You _could_ give a partial car to users to test it, and as a matter of fact that's
pretty much what I'll argue later, but still Kniberg chose to go with skateboard.
This notion of self contained-ness (is that a word?) is where I believe things start to unravel.

Let's dig into the examples in his text and see if we can understand what
Kniberg could mean with skateboard...

### The Spotify Example

> "developers basically sat down and hacked up a technical prototype, put in
> whatever ripped music they had on their laptops, and started experimenting
> wildly to find ways to make playback fast and stable"

He goes on to explain that they focussed on the single metric of latency to
make the product viable and used friends and family to test it. I can definitely
see that this is pretty far from what Spotify is today (or even at the time the
article was written), but why not just call this a prototype? Is a skateboard
a prototype for a car? Hardly.

### The Minecraft Example

Here, in one of the most baffling takes of the article, the skateboard of
Minecraft is described as:

> "You couldn’t do much in the first version – it was basically an ugly
> blocky 3d-landscape where you can dig up blocks and place them elsewhere
> to build crude structures."

Isn't that... just Minecraft?? I'm not making any friends here, I know, and of course
I'm being a bit facetious here. But can you honestly say that this first release
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
skateboard just means to get early feedback, and that the first versions of your
product are simpler than the later versions. None of this is objectionable,
but the fact that products start simple is also not very insightful[^big-bang].

#TODO: thin vertical slices!!


# TODO TODO TODO

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

Scrum guide 2013: https://scrumguides.org/docs/scrumguide/v1/Scrum-Guide-US.pdf : mentions "potentially releasable increment".
Scrum guide 2017: https://scrumguides.org/docs/scrumguide/v2017/2017-Scrum-Guide-US.pdf : softens that language to "must be in usable condition[...]"
Scrum guide 2020 (latest at the time of writing): https://scrumguides.org/docs/scrumguide/v2020/2020-Scrum-Guide-US.pdf#zoom=100 : "In order to provide value, the Increment must be usable"

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

![Anti-Agile Development](/blog/images/mvp/mvp-illustration.png)

## Endnotes

[^ai-assist-drawing]: Full disclosure, I used Claude Opus 4.6 to generate this drawing for me, by prompting it to create an SVG. The idea is, of course, mine but I'm still not proud of the resulting image. If you're an artist and would like your image featured here, please contact me!
[^henry-ford-quote]: While it _is true_ that the quote is often attributed to Ford, there's [no evidence](https://www.snopes.com/news/2025/02/23/horses-quote-henry-ford/) of him actually saying it. But _"never let the truth get in the way of a good story"_ --Mark Twain, or was it...?
[^lego-worlds]: I guess that the point of the Lego section is to say that the successful development did incorporate early user feedback, while the failed one did not. Sure, but what's that got to do with skateboards?
[^big-bang]: I'll extend an olive branch here and I'll say that there truly are people that try to design the perfect product in their ivory tower and yes, those people will likely never release _anything_.
