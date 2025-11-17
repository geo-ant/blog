---
layout: post
tags: statistics math
#categories: []
date: 2025-11-16
last_updated: 2025-03-20
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Sample Size Calculations for Binomial Distributions'
#
#
# Make sure this image is correct !!!
og_image: 
#
#
# make sure comments are enabled
comments_id: 
math: true
---

Greetings, traveler[^garth]. Say we have a sequence of independent Bernoulli
experiments and we want to make claims about the true probability of success,
given our observations. How many trials do we need to make claims about the true
probability with a certain confidence? If you're interested in joining me
gaining an understanding of this from first principles, you're invited to
read along.

## 0. Overview and Caveats

Please note that this is a well-known subject and I'll focus on a
particular _frequentist_ approach here that made sense to me. Specifically,
it's based on the [Clopper-Pearson interval](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval#Clopper%E2%80%93Pearson_interval),
which we'll derive from scratch. Wikipedia provides a
[nice overview](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval)
of different confidence intervals for the Binomial distribution and I also
recommend [Brown _et al._](https://projecteuclid.org/journals/statistical-science/volume-16/issue-2/Interval-Estimation-for-a-Binomial-Proportion/10.1214/ss/1009213286.full)
and [Thulin _et al._](https://projecteuclid.org/journals/electronic-journal-of-statistics/volume-8/issue-1/The-cost-of-using-exact-confidence-intervals-for-a-binomial/10.1214/14-EJS909.pdf)
hereafter (Bro01) and (Thu14), respectively. Please also note that Brown _et al._
describe the Clopper-Pearson interval as "wastefully conservative" and recommend
other intervals. I will still use it for the following reasons:

1. Due to its conservative nature, it will lead us to overestimate the number
   of samples rather than underestimate them[^sample-overest].
2. Frequentist statistics usually don't come naturally for me, this one at
   least made sense _to me_. I admit this is a me problem. 
3. The math involved in this derivation is a great jumping-off point for
   a Bayesian perspective, which I might share in a later post.

## 1. Deriving The Clopper Pearson Lower and Upper Bounds

A Bernoulli process is a series of independent Bernoulli experiments with
outcome _success_ with probability $$p$$ and _failure_ with probability
$$1-p$$. Let $$x$$ denote the number of successes,
then the probability of observing exactly $$k \in \mathbb{N}$$ successes, given
the total number $$n$$ of experiments and the probability of success $$p$$ is

$$
P(x = k \mid n,p) = \binom{n}{k}p^k (1-p)^{n-k}, \label{binomial-pdf} \tag{1}
$$

where obviously $$k \leq n$$. This is the [Binomial distribution](https://en.wikipedia.org/wiki/Binomial_distribution).
The probability of observing _at least_ $$k$$ successes is obviously

$$
P(x \geq k \mid n,p) = \sum_{k'=k}^n P(x = k' \mid n,p). \label{binomial-cdf} \tag{2}
$$

Now, given an observation of $$x \geq k$$ in $$n$$ samples, the Clopper-Pearson
bound for confidence level $$\gamma = 1-\alpha \in (0,1)$$ is given as $$(p_L,p_U)$$,
where 

$$P(x \geq k \mid n,p_L) = \frac{\alpha}{2}, \tag{3} \label{clopper-pl}$$

where $$p_L$$ can be understood as the smallest probability of success $$p = p_L$$,
for which observing $$x\geq k$$ successes can happen "by pure chance"
with probability $$\geq \alpha/2$$.

$$
P(x \leq k \mid n,p_U) = \frac{\alpha}{2}, \tag{4} \label{clopper-pu}
$$

where $$p_U$$ can be understood as the largest probability of success $$p = p_U$$,
for which observing $$x \leq k$$ successes can happen with probability $$\leq \alpha /2$$.
This offers a reasonably intuitive way of bounding the true probability,
given $$k$$ or more observed successes[^conservative]. However, when stated
like this, eqns. $$(\ref{clopper-pl})$$ and $$(\ref{clopper-pu})$$ aren't very helpful in
finding those bounds. Let's derive useful expressions for the lower and upper
bounds. But first, we'll have to take a detour into beta functions and the beta
distribution. 

### 1.1 Prerequisites: The Beta Distribution and Beta Functions

Trust me, this detour will make sense in a moment. Say we have a variable $$y \in [0,1]$$
that follows a [beta distribution](https://en.wikipedia.org/wiki/Beta_distribution),
then it's probability density (PDF) is given as follows:

$$\begin{eqnarray}
Y &\sim& Beta(a,b) \\
\Rightarrow P(y \mid a,b) &=& \beta^{pdf}_{a,b}(y) = \frac{y^a (1-y)^{b-1}}{B(a,b)}, \tag{5}\label{beta-pdf}
\end{eqnarray}$$

where $$a,b \in \mathbb{R}$$ with $$a,b> 0$$. $$B(a,b)$$ denotes
the [beta function](https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function).
Note that we have to differentiate between the beta _function_ and the beta _distribution_.
I've denoted the probability density function with $$\beta^{pdf}_{a,b}(y)$$, which
is nonstandard notation. This is just to convey that this is a function of
$$y$$ parametrized by $$a,b$$. It's cumulative distribution function (CDF) is given
as function of $$y$$ that is parametrized by $$a,b$$.

$$P(y \geq y_0 \mid a,b) = \beta^{cdf}_{a,b}(y_0) = I_{y_0}(a,b), \tag{6} \label{beta-cdf}$$

where $$I_y(a,b)$$ is the [_regularized_ incomplete beta function](https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function),
defined as

$$
I_y(a,b) = \frac{B(y;a,b)}{B(a,b)}, \tag{7} \label{ribeta}
$$

and $$B(x;a,b)$$ is the [incomplete beta function](https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function).
Note again, that I've introduced a nonstandard symbol $$\beta^{cdf}_{a,b}$$ for the
cumulative distribution function (note the "cdf" superscript rather than "pdf") now.
Again, this is just a way to express the CDF as a function of $$y$$ with parameters
$$a,b$$. Finally, we also introduce the [_quantile function_](https://en.wikipedia.org/wiki/Quantile_function) (QF),
also called _percent-point function_ (PPF), of the Beta-distribution. It's (as always) defined
as the inverse of the cumulative distribution function:

$$\beta^{qf}_{a,b}(p) = \beta^{cdf,-1}_{a,b}(p). \tag{8} \label{beta-qf}$$

First note that $$\beta^{qf}_{a,b}$$ is the _inverse function_ not the multiplicative
inverse of $$\beta^{cdf}_{a,b}$$, such that $$\beta^{cdf}_{a,b}(\beta^{qf}_{a,b}(p))=p$$.
On Wikipedia, (Bro01), and (Thu14) the symbol $$B(y;a,b)$$ is also used for the
quantile function of the beta distribution, which will get confusing very
quickly. I will only ever use $$B(y;a,b)$$ to denote the _incomplete_ beta
function in the following calculations. The quantile function of the beta
distribution does not have a closed form expression (that I know of), but it
can be calculated numerically. For example, in Python it can by calculated via
[`scipy.stats.beta.ppf`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html#scipy.stats.beta).

### 1.2 The Upper Clopper Pearson Bound

Let's first rewrite eq. $$(\ref{clopper-pu})$$, because the
left hand side is the cumulative distribution, which [we know](https://en.wikipedia.org/wiki/Binomial_distribution#Cumulative_distribution_function)
can be written like this:

$$\begin{eqnarray}
P(x \leq k \mid n,p) &=& I_{1-p}(n-k,k+1) \\
&=& 1-I_{p}(k+1,n-k) \\
&=& 1-\beta_{k+1,n-k}^{cdf}(p), \tag{9} \label{bi-cum}
\end{eqnarray}$$

where the second line is a [well-known property](https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function)
of the regularized incomplete beta function. Plugging this into $$(\ref{clopper-pu})$$
leads us to a closed form solution $$p_U$$ using the quantile function of the beta-distribution
with $$a = k+1$$, $$b = n-k$$:

$$\boxed{p_U = \beta^{qf}_{k+1,n-k}\left(1-\frac{\alpha}{2}\right)} \tag{10} \label{pu}$$

### 1.3 The Lower Clopper-Pearson Bound

It turns out, that the left hand side of eq. $$(\ref{clopper-pl})$$ can also
be written in terms of the CDF of the beta distribution with $$a = k$$
and $$b = n-k+1$$ (Bro01, Thu14):

$$
P(x \geq k \mid | p,n) = \beta^{cdf}_{k,n-k+1}(p) \label{johnson-equality} \tag{11}
$$

I'll give a proof for this identity in the next section. Using it
with eq. $$(\ref{clopper-pl})$$ allows us to write the lower bound as

$$\boxed{p_L =  \beta^{qf}_{k,n-k+1}\left(\frac{\alpha}{2}\right)} \tag{12} \label{pl}$$

### 1.3.1 Interlude: A Proof

We'll quickly walk through a proof of eq. $$(\ref{johnson-equality})$$ here, feel
free to skip this section. Plugging $$(\ref{beta-cdf})$$ into $$(\ref{johnson-equality})$$,
the claim we want to prove is:

$$P(x \geq k \mid p,n) \overset{?}{=} I_p(k,n-k+1)$$

We can rewrite the left hand side and use eqns. $$(\ref{bi-cum})$$ and
$$(\ref{beta-cdf})$$ so that:

$$\begin{eqnarray}
P(x \geq k \mid p,n) &=& 1-P(x < k \mid p,n) \\
&=& 1- (P(x \leq k \mid p,n) - P(x = k \mid p,n)) \\
&=& I_p(k+1,n-k) + P(x = k \mid p,n).
\end{eqnarray}$$

This implies that we have to prove

$$
I_p(k+1,n-k) + P(x = k \mid p,n) \overset{?}{=} I_p(k,n-k+1).
$$

We now use [the following recurrence relations](https://en.wikipedia.org/wiki/Beta_function#Properties_2)
for the regularized incomplete beta function:

$$\begin{eqnarray}
I_y(a+1,b) &=& I_y(a,b) - \frac{y^a (1-y)^b}{a B(a,b)}\\
I_y(a,b+1) &=& I_y(a,b) + \frac{y^a (1-y)^b}{b B(a,b)}.
\end{eqnarray}$$

Plugging this into the equation to prove above and rearranging a bit
gives us:

$$
P(x = k \mid p,n) \overset{?}{=} \frac{1}{B(k,n-k)}\frac{n}{k(n-k)} p^k (1-p)^{n-k}
$$

Now we have to use the fact that the beta-function can be [written in terms
of the $$\Gamma$$-function](https://en.wikipedia.org/wiki/Beta_function#Relationship_to_the_gamma_function)
as well as the fact that $$\Gamma(m) = (m-1)!$$ for nonzero integers $$m$$.
Using this, gives us:

$$\begin{eqnarray}
P(x = k \mid p,n) &\overset{?}{=}& \frac{(n-1)!}{(k-1)!\cdot (n-k-1)!}\frac{n}{k(n-k)} p^k (1-p)^{n-k} \\
 &=& \binom{n}{k} p^k (1-p)^{n-k},
\end{eqnarray}$$

where the last line is obviously true, because $$P(x = k \mid p,n)$$ is the
probability density function of the binomial distribution as written in $$(\ref{binomial-pdf})$$.
That proves the desired equality.

## 1.4 Clopper-Pearson Bounds: Summary

In summary, the calculations give us _two sided_ a $$\gamma$$-confidence interval
for the true probability of success $$p$$ in a series of $$n$$ Bernoulli experiments
given an observation of $$k$$ _or more_ successes. That interval is:

$$\boxed{p_L < p < p_U}, \tag{13}\label{two-sided}$$

with $$p_L$$ and $$p_U$$ calculated as in eqns. $$(\ref{pl})$$ and $$(\ref{pu})$$,
respectively.


## 2 A One-Sided Clopper-Pearson Style Bound

Often, we don't really care about an upper bound for the probability and we
are only interested in a lower limit, given $$k$$ _or more_ successes in
a series of $$n$$ experiments. Using the same logic that lead to the two-sided
confidence interval


## References

(Bro01) Lawrence D. Brown, T. Tony Cai, Anirban DasGupta. "Interval Estimation for a Binomial Proportion."
Statistical Science, 16(2) 101-133 May 2001. [link](https://doi.org/10.1214/ss/1009213286)

(Thu14) Måns Thulin. "The cost of using exact confidence intervals for a binomial proportion." Electronic Journal of
Statistics, 8(1) 817-840 2014. [link](https://doi.org/10.1214/14-EJS909)


## Endnotes

[^sample-overest]: This might or might not be a problem in practice. If we have are dealing with _in silico_ simulations, then increasing then increasing the number of samples might be reasonably cheap. If we have to e.g. recruit patients for a study, this will be 
[^conservative]: Do keep in mind that Brown _et al._ characterize the bounds overly conservative.
[^garth]: I've been re-watching [Garth Marenghi's Darkplace](https://www.channel4.com/programmes/garth-marenghis-darkplace) again recently... and so should you.
_at least_ $$k$$ successes.
