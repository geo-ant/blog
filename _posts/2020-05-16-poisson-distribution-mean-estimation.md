---
layout: post
tags: bayesian-probability-theory math
#categories: []
date: 2020-05-16
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Estimating the Mean from Poisson Distributed Count Data'
comments_id: 8
math: true
---

Assume we want to estimate the mean for Poisson count data: is it better to keep all the data, or is the sum and the size of the dataset enough? Let me do the calculations here. I'll also give the posterior distribution for three different choices of prior.

# The Problem

Assume we have a set of size $$N$$ of count data $${k_j} \in \mathbb{N}$$. The counts are indepentent and identically distributed (i.i.d.) with a Poisson distribution with an (unknown) mean $$\mu \in \mathbb{R}^+$$: 

$$k_j \sim \text{Pois}(\mu), j=1,...,N$$

I am interested in estimating the mean from the *sum of all observed counts* $$K = \sum_{j=1}^N k_j$$. The sum of poisson distributed random variables [is again Poisson distributed](https://en.wikipedia.org/wiki/Poisson_distribution#Sums_of_Poisson-distributed_random_variables). The [mean of the resulting distribution](https://math.stackexchange.com/questions/221078/poisson-distribution-of-sum-of-two-random-independent-variables-x-y) for $$K$$ is $$N\mu$$:

$$K \sim \text{Pois}(N\mu)$$

We will get back to estimating the mean from the complete set of results, but first let's look at estimating it from the sum of the results.

# Estimating the Mean from the Sum

We are interested in the posterior probability of $$\mu$$ given the sum of counts $$K$$ and the number of experiments $$N$$.

$$P(\mu \vert K,N,I) = \frac{P(K\vert \mu, N, I) \cdot P(\mu\vert I)}{P(K\vert N, I)}$$

All probabilities are conditioned on $$I$$ which is the accumulation of our *a priori* state of knowledge. The *likelihood* $$P(K\vert \mu, N, I)$$ is given by the poisson distribution with mean $$N\mu$$:

$$P(K\vert \mu,N,I) = \frac{(N\mu)^K}{K!} \exp(-N\mu)$$

The *prior* probability of $$\mu$$ having a certain value does not depend on the number of experiments. Thus, I can write $$P(\mu \vert N,I)=P(\mu\vert I)$$. Our prior state of knowledge will play a key role in expressing the prior probability. In the next sections I will explore different priors. The *evidence* (or marginal likelihood) term in the denominator acts as a normalization constant with respect to $$\mu$$. It can be calculated as the integral of the numerator over all possible valuse of $$\mu$$:

$$P(K\vert N, I) = \int_0^\infty d\mu\, P(K,\mu\vert N,I) = \int_0^\infty d\mu\, P(K\vert \mu, N,I)\cdot P(\mu \vert I)$$

Since this expression also depends on the prior, I will calculate it in the later sections. If we were just interested in the maximum of the posterior distribution we need not calculate the evidence term, because it does not depend on $$\mu$$.

# The Posterior Distribution for the Sum
In the following I will calculate the posterior distribution for $$\mu$$ for different choices of the prior. We can later use these expressions as the basis for all further calculations, e.g. the *maximum a posteriori* estimate $$\hat{\mu}$$.

## Flat Priors: Maximum Likelihood
A flat prior means that we are sure that the value of  $$\mu$$ is in an interval $$[\mu_{max}-\mu_{min}]$$, where it could take any of these values with equal probability:

$$P(\mu\vert I) = \left\{\begin{array}{ll} 1/(\mu_{max}-\mu_{min}), & \mu\in[\mu_{min},\mu_{max}]\\ 0, & else\end{array}\right.,$$

Note that $$\mu$$ is confined to a *finite interval*, so that the normalization of the prior can be performed. Note further that the interval might clip the maximum of the likelihood function. If we just want to use the flat prior as a justification of the maximum likelihood method, we can just say the interval is "suitably large" and estimate the maximum a posteriori  value $$\hat{\mu}$$ as the maximum of the likelihood function. We can even specify the prior as $$P(\mu\vert I)=c \in \mathbb{R}$$ without a definition range because the posterior can still be normalized for any $$c$$. The posterior is calculated [with a little help from Wolfram Alpha](https://www.wolframalpha.com/input/?i=int%28mu%5Ek%2Fk%21*exp%28-mu%29%2C+mu%2C+0%2C+inf%29):

$$P(\mu\vert K,N,I) = \frac{N^{K+1}}{\Gamma(K+1)}\mu^{(K+1)-1}\exp(-N\mu) \sim \text{Gamma}(K+1,N),$$

where I have used $$\Gamma(K+1)=K!$$ for $$K\in\mathbb{N}$$. I have written the posterior so peculiarly so that we can see that it is a [Gamma distribution](https://en.wikipedia.org/wiki/Gamma_distribution) with shape $$K+1$$ and rate $$N$$.

## Jeffreys' Prior
[Harold Jeffreys himself recommended](https://royalsocietypublishing.org/doi/abs/10.1098/rspa.1946.0056) $$P(\mu\vert I) \propto 1/\mu$$ as an uninformative prior for the Poisson distribution[^jefpois]. I will refer to this prior as Jeffreys' prior[^jefprio]. It is worth noting that the prior, like the flat prior cannot be normalized on an infinite interval. Thus, similar considerations as above apply. As the flat prior, the Jeffreys prior still leads to a well behaved (normalizable) posterior for $$\mu\in[0,\infty)$$ regardless[^improp].

Using some [help from Wolfram Alpha](https://www.wolframalpha.com/input/?i=int%28mu%5E%28K-1%29*exp%28-N*mu%29%2Cmu%29) we can see that the integral in the denominator is $$\int_0^\infty d\mu\,\mu^{K-1}\exp(-N\mu)=N^{-K} \Gamma(K)$$. So finally we have our posterior:

$$P(\mu \vert K,N,I)=\frac{N^K}{\Gamma(K)}\cdot \mu^{K-1} \exp(-N\mu) \sim \text{Gamma}(K,N)$$

This is a Gamma distribution, as was the case for the flat prior, but with shape $$K$$ and rate $$N$$.


## Conjugate Prior
The [conjugate prior](https://en.wikipedia.org/wiki/Conjugate_prior#Table_of_conjugate_distributions) for the Poisson distribution[^gamcon] is a Gamma distribution: 


$$P(\mu \vert I) = \frac{b^a}{\Gamma(a)} \mu^{a-1}\exp(-b\mu) \sim \text{Gamma}(a,b),$$

where we use $$a, b$$ as the shape and rate parameter of the prior distribution. [Calculating the evidence integral](https://www.wolframalpha.com/input/?i=int%28mu%5E%28K%2Ba-1%29*exp%28%28-N%2Bb%29*mu%29%2Cmu%2C0%2Cinf%29) and plugging it into the posterior leads us to

$$P(\mu \vert K,N,I) = \frac{(N+b)^{K+a}}{\Gamma(K+a)}\mu^{K+a-1}\exp(-(N+b)\mu) \sim \text{Gamma}(K+a,N+b),$$

which is, again, a Gamma distribution but with shape $$K+a$$ and rate $$N+b$$. It is worth noting that this distribution *kind of* contains the calculations above as special cases. This is because the Gamma prior for $$(a,b)=(1,0)$$ is the flat prior. If we disregard for a moment the fact that $$\Gamma(0)$$ is not defined then the case $$(a,b)=(0,0)$$ becomes Jeffreys' prior.

## All Roads Lead to the Gamma
We see that the posterior distribution for the sum is a Gamma distribution for all priors that I considered:

$$P(\mu \vert K, N ,I) \sim \text{Gamma}(\alpha, \beta),$$

where the shape $$\alpha$$ and rate $$\beta$$ depends on the choice of prior. As the sum $$K$$ and the number of experiments $$N$$ grow large, all distrubutions converge towards the same posterior.

$$(\alpha,\beta) \rightarrow (K,N) \text{ as } K\rightarrow\infty, N\rightarrow \infty$$

For large $$K,N$$ the distribution could be further approximated by a Gaussian.

# Estimating the Mean from the Complete Dataset
Until now I have derived the posterior probabilities from the sum of the i.i.d variables. This means we have reduced our set of results $$\{k_j\}_{j=1,...,N}$$ to two values, namely the sum $$K = \sum_{j=1}^N k_j$$ and the number of summands $$N$$. Now lets see if the posterior would look any different if we kept the information about the whole set. Because of the independence of the results, the likelihood term can be [written as a product](https://www.tandfonline.com/doi/full/10.1080/03610926.2019.1619768):

$$\begin{eqnarray}
P(\{k_j\}\vert \mu, N, I) &=& \prod_j P(k_j\vert \mu, I) \\
 &=& \frac{\mu^{\sum_j k_j}}{\prod_j k_j!}\exp(-N\mu) \\
 &=& \frac{K!}{N^K\cdot\prod_j k_j!}\cdot\frac{(N\mu)^K}{K!}\exp(-N\mu) \\
 &=& \frac{K!}{N^K\cdot\prod_j k_j!} P(K \vert \mu , N, I).
\end{eqnarray}$$

So we see that the likelihood term for obtaining the set is identical to the likelihood term of obtaining the sum multiplied by a constant *that does not depend on $$\mu$$*. When calculating the posterior distribution this constant will cancel and leave us with the same posterior as we had calculated before.

To me this result is somewhat remarkable. It means, for this particular case, that we can reduce the dataset to two numbers $$K$$ and $$N$$ and still estimate the mean with the same confidence as if we had kept all the data. Maybe this should not have surprised me, because estimating the mean from $$K$$ and $$N$$ is something that makes sense intuitively. I still wonder if there is more to this. Would this result have followed from a more general principle that I am unaware of? I'll have to [ask somewhere else](https://stats.stackexchange.com/questions/463941/estimating-mean-from-sum-of-data-vs-estimating-from-complete-set).

# Estimators for The Mean
To estimate the most likely *a posteriori* mean $$\hat{\mu}$$ we have to maximize $$P(\mu\vert N, K, I)$$. It's easier to find the maximum for $$\log P(\mu\vert N, K, I)$$. And it's much easier still after we realize we're always dealing with a $$\text{Gamma}(\alpha,\beta)$$ distribution with shape $$\alpha$$ and rate $$\beta$$. So the position of the maximum is $$\hat{\mu}=(\alpha-1)/\beta$$.

So for the *flat prior* we arrive at 

$$\hat{\mu}_{MLE}=\frac{K}{N},$$

which is the maximum likelihood estimator. For *Jeffreys' prior* we get

$$\hat{\mu}_{J} = \frac {K-1}{N},$$

and for the conjugate prior, which is a $$\text{Gamma}(a,b)$$ distribution, we have

$$\hat{\mu}_{CP} = \frac {K+a-1}{N+b}.$$

As $$K$$ and $$N$$ get large, we can see that all estimates tend towards the same value.

# Quantifying Our Confidence
Now we know how to estimate the mean from a collection of Poisson distributed random variables. All we need is the sum of the variables and the number of trials. However, we have not looked into credible intervals. Since we always end up with a Gamma distribution there should be information out there. Maybe [here](https://www.tandfonline.com/doi/full/10.1080/03610926.2019.1619768) is a good place to start. Another time...

# Endnotes
[^jefprio]: This is different from the prior that results when applying Jeffreys' Rule. See [here](https://www.statisticshowto.com/jeffreys-prior/) for an explanation of the confusing nomenclature 


[^jefpois]: The astute reader will have noticed that Jeffreys' prior is meant for a Poisson distribution with mean $$\mu$$ and not $$N\mu$$ like we have here. However, transforming these functions would only [introduce a constant](https://math.stackexchange.com/questions/1325284/find-the-distribution-of-linear-combination-of-independent-random-variables/1325545) for this particular prior, if I am not mistaken. The constant would cancel out because it appears in the integral in the denominator as well as the numerator.

[^improp]: As is the case for the flat prior. Both are called [improper priors](https://en.wikipedia.org/wiki/Prior_probability#Improper_priors).

[^gamcon]: The same considerations as in the footnote above[^jefpois] apply.
