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

Before we get into my thoughts, let's remind ourselves of the original image.

<figure>
 <img src="/blog/images/mvp/kniberg-mvp.png" alt="Kniberg's Illustration" style="width:100%">
   <figcaption> Kniberg's original illustration from <a href="https://blog.crisp.se/2016/01/25/henrikkniberg/making-sense-of-mvp">this article</a>: "The picture is a metaphor. It is not about actual car development, it is about product development in general, using a car as a metaphor."</figcaption>
</figure>

I don't want to focus on the image too much because as Kniberg states, it's just
a metaphor, so let me also give a very brief summary of the article as I understand
it. The core message in the article is as follows: Rather than building incomplete
pieces of a larger vision, start with a simple solution that already delivers
real user value. Evolve testable, usable, lovable versions through feedback.
This avoids wasted effort and leads to a better product than executing a fixed
upfront plan.

I hope that's a fair (albeit brief) summary and I believe there's both great
value and great danger in the mental model underlying this thinking. Let's get
into it.

## The Good Parts

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

![Anti-Agile Development](/blog/images/mvp/mvp-illustration.png)

## Endnotes

[^ai-assist-drawing]: Full disclosure, I used Claude Opus 4.6 to generate this drawing for me, by prompting it to create an SVG. The idea is, of course, mine but I'm still not proud of the resulting image. If you're an artist and would like your image featured here, please contact me!

