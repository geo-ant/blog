---
layout: post
tags: bayesian-probability-theory math games
#categories: []
date: 2020-02-08 00:00:00
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Bayesian Analysis of a Game for Children - Part 1: Fundamentals'
comments_id: 5
math: true
---

While playing a boardgame for three-year-olds with my daughter, my mind started to wander. Boardgames for young children give the player very little agency to influence the game, if any. Yet I wondered what the best playing strategy for this particular game was. The game is simple enough that I can start writing a simulation but now I am faced with the problem of how to interpret the data. How confident can I be that one strategy really is better than the other? Deriving these answers from scratch is the topic of this series.

# A Note on Bayesian Probability Theory
The book that changed my whole perception of probability theory is [Data Analysis - A Bayesian Tutorial](https://global.oup.com/academic/product/data-analysis-9780198568322?cc=de&lang=en&) by D.S. Sivia and J. Skilling. In this book, the authors build a logical fundament of probablity theory and motivate the reader by constantly giving practical applications. I will follow their reasoning and their notation. Thus $$P(X \vert I)$$ is the probability of a proposition $$X$$ given some background knowledge $$I$$. All probabilities are conditional on $$I$$ because the authors state:
> ...there is no such thing as an absolute probability

The $$I$$ takes the role of all background knowlegde we have on a certain situation. The probability of an event depends on the state of knowlegde  we have (or *assumptions* if that is easier to swallow). Your background knowledge may be different than mine and thus lead to different probabilities. That is fine, because as long as we are clear about our assumptions we can always compare results.

This leads us to the next point. Probability values reflect our confidence in something. The probability of a proposition being true is a value between zero and one. Zero meaning the proposition is false and one meaning it is true (given our prior knowlegde $$I$$). Every value between those reflects our confidence in the truth value of the proposition. However, this only has a meaning if compared to the probability value of a different proposition. Say we have $$A$$="I look fantastic in my black shirt" and we arrived somehow at $$P(A \vert I) = 0.2$$. That does not mean much by itself. Let us also say we have $$B$$="A killer virus will break out today" and $$P(B \vert I)=10^{-6}$$. Now we know that we believe in $$A$$ more than $$B$$. So when we stand before our wardrobe, black shirt in one hand and biohazard suit in the other, we can let our fashion choice be guided by our relative confidence in these propositions.

Interpreting the probability as a level of confidence (or *belief*) in the proposition is the heart of the Bayesian approach. This is opposed to the frequentist approach, which interprets the probabilty of an event as the frequency of an event occurring given multiple repetitions of the same experiment.

# Anatomy of a Simple Game
Let us now dive into the analysis of a game. Assume the simplest case for a game: a cooperative game where either all players win or lose collectively. This means the game has two outcomes $$W$$="players win the game" and $$L$$="players lose the game". Further assume that we have some agency in the game, e.g. a choice of strategy $$S$$ that might influence the outcome of the game. What we are interested in is the probability of winning the game $$P(W \vert S,I)$$ given our strategy $$S$$ and our background knowledge $$I$$. By the way, of course we have $$P(W \vert S,I)=1-P(L \vert S,I)$$.

For ease of notation let us write the probability of winning as $$p := P(W \vert S,I) \in [0,1]$$. We omit $$S$$ and $$I$$ in our symbol $$p$$ just to make the following calculations easier to read. What we are interested in is gaining knowledge about $$p$$ from some data we have collected about the game. How do we do that? Well, let us answer a different (but related) question first.

We ask: If we play the game $$N$$ times total, what is the probability of winning $$N_W$$ times? Again, given the probability $$p$$ of winning a single game. This is answered by the [Binomial Distribution](https://en.m.wikipedia.org/wiki/Binomial_distribution) if we assume the results of individual games are statistically independent:

$$P(N_W \vert p,N,S,I) = \binom{N}{N_W} \cdot p^{N_W}\cdot(1-p)^{N-N_W} \tag{1}$$

It is the first step in estimating our chances of winning from data we have collected about the game.

# Gaining Knowledge from Data
To get to $$p=P(W \vert S,I)$$ we need data. This data can, for example, be generated by repeated executions of the game or a simulation. The data is the vector $$(N_W,N,S)$$, i.e. the number $$N_W$$ of wins in $$N$$ games using a strategy $$S$$. What we are interested in specifically is $$P(p \vert N_W,N,S,I)$$: it is the probability of $$P(W \vert S,I)$$ having the value $$p$$ given a certain strategy and the observed data. Do not be weirded out that  $$p$$ is itself a probability (of winning a single game). Call it  "chance of winning" and the thing gets less complicated when written as an English sentence: we are interested in the probability of our chance of winning being $$p$$. Not too bad, right?

If this is all getting confusing and by now you are thinking: "*stop making things so complicated, the chance of winning is $$p=N_W/N$$ and that's it*". Well... you're not *wrong*, but this is just part of the riddle. The point of this exercise is not only to get to the value of $$p$$. The point of this exercise is to gain insight into how confident we are in this value given the data. So bear with me.

## Applying Bayes Theorem

Looking at formula $$(1)$$ above we can see that we almost, but not quite, have the expression that we want. What we *have* is an expression for the probability of observing the data $$N_W$$ given $$p$$. What we *want* is an expression for the probability of $$p$$ given the observed data. This is where [Bayes Theorem](https://en.m.wikipedia.org/wiki/Bayes%27_theorem) comes into play. Here it enables us to write:

$$P(p \vert N_W,N,S,I) = \frac{P(N_W \vert p,N,S,I) \cdot P(p \vert N,S,I)}{P(N_W \vert ,N,S,I)}.$$

Let us talk about each term briefly: the term on the left hand side is called the *posterior probability*. It reflects our state of knowledge in light of new data. The first term on the right hand side $$P(N_W \vert p,N,S,I)$$ is called the *likelihood* of observing the data given $$p$$. We already have an expression from formula $$(1)$$. The denominator $$P(N_W \vert ,N,S,I)$$ is called the *evidence*. Since term does not depend on $$p$$, it is merely a constant of integration in our particular use case. It ensures that the posterior probability is normalized to one.

The last term on the right hand side is called the *prior* probability. That is the probability we assign to the possible values of $$p$$ based on our prior state of knowledge. One thing we can be sure of is that the term does not depend on the number of games (per our initial assumtions that games are independent). So  $$P(p \vert ,N,S,I)=P(p \vert S,I)$$. The prior probability is informed by everything we assume or know beforehand, for example

* we could have reason to assume that the game is balanced. So we might assign a probability distribution with maximum at $$p=0.5$$ and a width that reflects how sure we are of the game being perfectly balanced,
* we could already have collected data and our prior is the posterior propability which we calculated last time,
* we are completely ignorant,

or anything else we can think of. Expressing ignorance is generally an art in itself and I will consider it the next time I write about this topic. Before I finish this post, let us state the posterior probability explicitly:

$$P(p \vert N_W,N,S,I) = \frac{\binom{N}{N_W} \cdot p^{N_W}\cdot(1-p)^{N-N_W} \cdot P(p \vert S,I)}{P(N_W \vert N,S,I)}.$$

So much for the very basics. With this we can calculate the probability distribution of the chance of winning with a given strategy, after collecting data.

## The Most Likely Chance of Winning
Since we have gotten into a lot of abstract theory, we want to leave with one practical thing. What is the value at which the posterior probability is at its maximum? This should be easy because it is just going to be $$p=N_W/N$$, right? Using good old calculus we just have to find $$p$$ for which

$$\frac{\partial }{\partial p}P(p \vert N_W,N,S,I) = 0.$$

This is identical to

$$\frac{\partial }{\partial p} \left(p^{N_W}\cdot(1-p)^{N-N_W} \cdot P(p \vert S,I)\right) = 0,$$

because all other terms in the equation are constant with respect to $$p$$. Now we can see a tiny problem. The *prior* probability is a function of $$p$$. Thus the maximum of the *posterior* distribution depends on our prior distribution, which only makes sense. If we set the prior distribution to a constant on the whole range of $$p$$, *only then* do we arrive at the familiar

$$p=\frac{N_W}{N} \text{ , if } P(p \vert S,I)=const.$$

Here have effectively only maximized the likelihood term. This is why our $$p=N_W/N$$ is called the maximum likelihood estimator for the Binomial Distribution.

# To Be Continued
In [part 2 of this series](/blog/2020/bayesian-game-analysis-part2/) I will turn to the actual game I am playing with my kid. I will present the results based on the calculations in today's post (and also [this one over here](/blog/2020/probability-x-greater-y/)).
