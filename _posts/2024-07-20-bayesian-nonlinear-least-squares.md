---
layout: post
tags: least-squares algorithm math bayesian
#categories: []
date: 2024-07-20
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Nonlinear Least Squares Fitting - A Bayesian Tutorial'
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

!!!!!!!!!! REDO INTRODUCTION

# 1. Nonlinear Least Squares Fitting

Assume we have a vector of observations $$\boldsymbol{y} \in \mathbb{R}^{N_y}$$
that we want to "fit" with a _model function_
$$\boldsymbol{f}(\boldsymbol{p}) \in \mathbb{R}^{N_y}$$ that depends on $$N_p$$
parameters $$\boldsymbol{p} \in \mathbb{R}^{N_p}$$. Then, the process of least
squares _fitting_ a function is to find the parameters that minimize the weighted
squared difference of the function and the observations. We call those parameters
$$\boldsymbol{p}^\dagger$$, formally:

$$ \boldsymbol{p}^\dagger = \arg\min_{\boldsymbol{p}} \frac{1}{2} \lVert W \left(\boldsymbol{y} - \boldsymbol{f}(\boldsymbol{p})\right) \rVert^2 \label{lsqr-fitting}\tag{1.1},$$

where$$\lVert\cdot\rVert$$ is the $$\ell 2$$ norm of a vector and $$\boldsymbol{W} \in \mathbb{R}^{N_y \times N_y}$$ is a matrix
of weights. We'll spend much more time on what those weights mean in
the following sections. For now, let's introduce some helpful abbreviations
and rewrite the equation above:

$$ \boldsymbol{p}^\dagger = \arg\min_{\boldsymbol{p}} g(\boldsymbol{p}) \label{lsqr-fitting-g}\tag{1.2},$$

where $$g$$ is called the _objective function_ of the minimization, which
we can write in terms of the (weighted) residuals:

$$\begin{eqnarray} 
g(\boldsymbol{p}) &:=& \frac{1}{2} \boldsymbol{r}_w^T(\boldsymbol{p}) \boldsymbol{r_w}(\boldsymbol{p}), \label{objective-function} \tag{1.3}\\
  &=& \frac{1}{2} \boldsymbol{r}^T(\boldsymbol{p}) (\boldsymbol{W}^T \boldsymbol{W}) \boldsymbol{r}(\boldsymbol{p}) \\
  &=& \frac{1}{2} \sum_j (y_j - f_j(\boldsymbol{p}))^2 \\
\boldsymbol{r}(\boldsymbol{p}) &:=& \boldsymbol{y}-\boldsymbol{f}(\boldsymbol{p}) \label{residuals}\tag{1.4} \\
\boldsymbol{r}_w(\boldsymbol{p}) &:=& \boldsymbol{W} \boldsymbol{r}(\boldsymbol{p}) \label{weighted-residuals}\tag{1.5}
\end{eqnarray}$$

Note, that the objective function is a quadratic form with the matrix
$$\boldsymbol{W}^T\boldsymbol{W}$$. Sometimes the objective function
is written as $$\boldsymbol{r}^T \boldsymbol{W'} \boldsymbol{r}$$ or
$$\boldsymbol{r}^T \boldsymbol{S^{-1}} \boldsymbol{r}$$. All forms are equivalent,
but it does influence how exactly the elements of the weighting matrix appear
in the later equations. This determines their precise meaning. One can always transform
one representation into another, but the important thing is to pick one and 
apply it consistently. For the purposes of this article, we stick with the objective function as
stated above.

Our ultimate goal here is answer the following questions: why do we minimize
the sum of squares, as opposed to e.g. the sum of absolutes or 4th powers?
What exactly do the weights represent? What are the statistical
properties (such as estimated variance) of the best fit parameters? What are the
confidence bands (or _credible intervals_ to be more precise) of the best model
after the fit? We'll try and answer this by building nonlinear least squares from the ground up.

## 1.1 Helpful Identities

Before we dive in to the Bayesian perspective, let's state some helpful equations
that will come in handy later. These formulas are found e.g. in the classic (Noc06)
or the very nice thesis (Kal22). The gradient of the objective function is

$$
\nabla g(\boldsymbol{p}) = \boldsymbol{J}^T_{r_w}(\boldsymbol{p})\; \boldsymbol{r}_w(\boldsymbol{p}), \label{gradient-objective}\tag{1.6}
$$

where $$\boldsymbol{J}_{r_w}(\boldsymbol{p})$$ is the Jacobian Matrix of 
the weighted residuals $$\boldsymbol{r}_w(\boldsymbol{p})$$.
Often the Jacobian is only denoted by a simple $$\boldsymbol{J}$$, but for this post
it pays to be precise, because there is also the Jacobian $$\boldsymbol{J}_f$$ of 
the model function $$\boldsymbol{f}(\boldsymbol{p})$$, which is related to $$\boldsymbol{J}_{r_w}$$
by 

$$\boldsymbol{J}_{r_w}(\boldsymbol{p}) = -\boldsymbol{W} \boldsymbol{J}_f(\boldsymbol{p}).\label{jac-rw-f}\tag{1.7}$$

The Hessian matrix of $$g(\boldsymbol{p})$$ is calculated as follows, using
the notation $$r_{w,j}$$ for the element at index $$j$$ of $$\boldsymbol{r}_w$$:

$$\begin{eqnarray}
\boldsymbol{H}_{g}(\boldsymbol{p}) = \nabla^2 g(\boldsymbol{p}) &=& \boldsymbol{J}_{r_w}^T(\boldsymbol{p}) \boldsymbol{J}_{r_w}(\boldsymbol{p})+\sum_{j} r_{w,j}(\boldsymbol{p}) \nabla^2 r_{w,j}(\boldsymbol{p}) \label{hessian-g-exact} \tag{1.8} \\
 &\approx& \boldsymbol{J}_{r_w}^T(\boldsymbol{p}) \boldsymbol{J}_{r_w}(\boldsymbol{p}) \label{hessian-g-approx} \tag{1.9},
\end{eqnarray}$$

The approximation is very commonly used in least squares fitting and we will
also employ it in this article. With those bits of housekeeping out of the way,
let's now jump into the Bayesian perspective.

# 2. Bayesian Perspective on Least Squares

The fundamental assumption that will bring us to nonlinear least squares is
that the data can be modeled by a normal distribution. Why is that? One way
to think of it, is that the measured data is the sum of a _true_ underlying value
with additive zero mean Gaussian noise.

$$Y = Y_{true} + N,$$

where the noise is normally distributed $$N \sim \mathcal{N}(0,\sigma)$$. If we
assume the true value is one exact value, we can model its distribution as a delta
peak. Thus, the sum of the true value and the noise will follow a normal
distribution centered around the true value. In our case, we don't know the
true value, but instead we model it by the function $$\boldsymbol{f}(\boldsymbol{p})$$.
Thus, if the parameters $$\boldsymbol{p}$$ are given, the likelihood of observing data $$\boldsymbol{y}$$ is
given as a [multivariate Normal distribution](https://en.wikipedia.org/wiki/Multivariate_normal_distribution)
with mean $$\boldsymbol{f}(\boldsymbol{p})$$ and covariance matrix $$\Sigma \in \mathbb{R}^{N_y\times N_y}$$. 
The covariance matrix informs us about the observed variance (and covariance) _in the observed data_. For
example, on the $$j$$-th position on the diagonal it has the _variance_ $$\sigma_j^2$$
of the data element at $$j$$. 

For this article, let's make the assumption that the elements
$$y_j$$ are [statistically independent](https://en.wikipedia.org/wiki/Independence_(probability_theory))
of each other. Some of the calculations in this article will be true even if they
aren't, but finding  out which ones is left as an _exercise to the reader_[^exercise-reader].
The statistical independence implies that the covariance matrix is nonzero
only on the diagonal:

$$\Sigma = \text{diag}(\sigma^2_1,\dots,\sigma^2_{N_y}) \label{covariance-diag}\tag{2.1}$$

We can now write the likelihood of observing data $$y_j$$ at index $$j$$, given
the parameters $$\boldsymbol{p}$$ and the standard deviation $$\sigma_j$$ at $$j$$ as:

$$P(y_j | \boldsymbol{p}, \sigma_j) = \frac{1}{\sqrt{2\pi}\sigma_j}\exp\left( -\frac{1}{2}\frac{(y_j-f_j(\boldsymbol{p}))^2}{\sigma_j^2} \right).\label{likelihood-yi}\tag{2.2}$$

This allows us to write the likelihood of observing the data vector $$\boldsymbol{y}$$
given the parameters $$\boldsymbol{p}$$ and the set of standard deviations $$\{\sigma_j\}$$ 
as the product:

$$P(\boldsymbol{y}|\boldsymbol{p},\{\sigma_j\}) = \prod_j P(y_j|\boldsymbol{p},\sigma_j) \label{likelihood} \tag{2.3}$$

with $$\boldsymbol{r}$$ as in eq. $$\eqref{residuals}$$. From a Bayesian point of view, we are interested
in the posterior distribution that describes the probability density of $$\boldsymbol{p}$$
given our observations $$\boldsymbol{y}$$. Bayes Theorem brings us a step closer towards
this: 

$$P(\boldsymbol{p},\{\sigma_j\}|\boldsymbol{y}) = \frac{P(\boldsymbol{y}|\boldsymbol{p},\{\sigma_j\})\cdot P(\boldsymbol{p},\{\sigma_j\})}{P(\boldsymbol{y})}.\label{joint-posterior}\tag{2.4}$$

This is actually the joint posterior probability for the parameters $$\boldsymbol{p}$$ _and_
the standard deviations $$\{\sigma_j\}$$. Now let's make another assumption, which
is that the standard deviations $$\{\sigma_j\}$$ are also statistically independent.
This implies

$$P(\boldsymbol{p}, \{\sigma_j\}) = \prod_j P(\boldsymbol{p}, \sigma_j),$$

which, together with eq. $$\eqref{likelihood}$$ allows us to write:

$$P(\boldsymbol{p},\{\sigma_j\}|\boldsymbol{y}) \propto \prod_j P(y_j|\boldsymbol{p},\sigma_j)\cdot P(\boldsymbol{p},\sigma_j), $$

where we have omitted constants that don't depend on the parameters or the standard
deviations, such as the marginal probability $$P(\boldsymbol{y})$$. Annoyingly,
this posterior still contains the standard deviations. What's nice is, that
we can [marginalize out](https://en.wikipedia.org/wiki/Marginal_distribution)
the dependency on the standard deviations in the posterior by integration:

$$
P(\boldsymbol{p}|\boldsymbol{y}) \propto \int  \prod_j P(y_j|\boldsymbol{p},\sigma_j)\cdot P(\boldsymbol{p},\sigma_j) \;\text{d}\{\sigma_j\}\label{posterior}\tag{2.5}, \\
$$

where the integral is multidimensinal over all $$\sigma_j$$. This is finally 
the posterior distribution for the parameters that we are looking for.
It allows us for example to find the maximum _a posteriori_ estimate for the parameters.
There is just one problem: to actually find an expression for that, we need to
solve the integral. And to do that we have to make some assumptions about
the _prior_ probability distributions $$P(\boldsymbol{p},\sigma_j)$$. 

In the next sections,
we'll think through the implications of different priors
and we'll relate them to the least squares problem eq. $$\eqref{lsqr-fitting}$$.
We'll see how different assumptions end up giving us the same estimate for the best
parameters, but that there are differences in the associated uncertainties.
Let's start with the simplest case first.

# 3. Nonlinear Least Squares with Known Standard Deviations

If, for some reason, we _know_ the standard deviations $$\{\sigma_j\}$$, then
things get very simple. First, let's rewrite the joint prior distribution 
as 

$$P(\boldsymbol{p}|\boldsymbol{y}) P(\boldsymbol{p},\sigma_j) = P(\boldsymbol{p}|\sigma_j)\,P(\sigma_j) = P(\boldsymbol{p})\,P(\sigma_j).$$

Here, we have used that $$\boldsymbol{p}$$ and $$\sigma_j$$ are statistically
independent in our case. Since we know all the standard deviations, the
probability densities $$P(\sigma_j)$$ become delta-functions, such that the
posterior eq. $$\eqref{posterior}$$ becomes:

$$P(\boldsymbol{p}|\boldsymbol{y}) \propto \prod_j P(y_j|\boldsymbol{p},\sigma_j)\cdot P(\boldsymbol{p}), \tag{3.1}$$

where all the $$\sigma_j$$ are known constants. Now, we assume a uniform (or _flat_) prior
for the parameters:

$$P(\boldsymbol{p}) = \text{const.} \tag{3.2}$$

From a Bayesian perspective, this is a naive way of conveying ignorance about
the values of the parameters [^uniform-prior]<sup>,</sup>[^ignorance].
This lets us write the joint posterior probability eq. $$\eqref{joint-posterior}$$
as:

$$\begin{eqnarray}
P(\boldsymbol{p}&|&\boldsymbol{y}) \propto \exp\left(- g(\boldsymbol{p})\right) \label{posterior-known-sigma}\tag{3.4} \\
\text{with } &\boldsymbol{W}& = \text{diag}(1/\sigma_1,\dots,1/\sigma_{N_y}) \label{weights-known-sigma}\tag{3.5}
\end{eqnarray}$$

and with $$g(\boldsymbol{p})$$ as in eq. $$\eqref{objective-function}$$.
It is now trivial to show, that maximizing the posterior distribution is equivalent
to the least squares problem $$\eqref{lsqr-fitting}$$. It's important to note that
the weights must be a diagonal matrix as in eq. $$\eqref{weights-known-sigma}$$.

## 3.1 The Covariance Matrix for the Best Fit Parameters

We will now derive an approximation for the covariance matrix $$\boldsymbol{C}_{p^\dagger}$$
of the best fit parameters. This matrix is of interest e.g. because on the diagonal 
it contains the variances of the elements of the parameter vector. If we know
those, we can give estimates of probable ranges for the parameters. We can
also use the covariance matrix to calculate [correlations](https://en.wikipedia.org/wiki/Correlation#Correlation_matrices)
between the parameters. Let's start by examining the posterior probability
for the parameters.

In general, we won't be able to say much about the functional form of the
posterior probability $$\eqref{posterior-known-sigma}$$,
because it depends on $$\boldsymbol{f}(\boldsymbol{p})$$. However, in the vicinity
of the best fit parameters $$\boldsymbol{p}^\dagger$$, we can make some 
useful approximations. 

Using a Taylor expansion we can write $$g$$ around the best fit parameter $$\boldsymbol{p}^\dagger$$
as

$$
g(\boldsymbol{p}) = g(\boldsymbol{p}^\dagger) + \nabla g(\boldsymbol{p}^\dagger) \cdot (\boldsymbol{p}-\boldsymbol{p}^\dagger) + \frac{1}{2} (\boldsymbol{p}-\boldsymbol{p}^\dagger)^T\, \boldsymbol{H}_g(\boldsymbol{p}^\dagger) (\boldsymbol{p}-\boldsymbol{p}^\dagger) + \mathcal{O}(\lVert \boldsymbol{p}-\boldsymbol{p}^\dagger\rVert^3)
$$

where $$\nabla g(\boldsymbol{p}^\dagger)$$ is the gradient of $$g$$ and $$\boldsymbol{H}_g(\boldsymbol{p}^\dagger)$$
is the Hessian of $$g$$, both evaluated at $$\boldsymbol{p}^\dagger$$. Since
$$\boldsymbol{p}^\dagger$$ minimizes $$g$$, we know that the gradient must vanish, 
such that we can approximate $$g$$ up to second order as

$$
g(\boldsymbol{p}) \approx g(\boldsymbol{p}^\dagger) + \frac{1}{2} (\boldsymbol{p}-\boldsymbol{p}^\dagger)^T\, \boldsymbol{H}_g(\boldsymbol{p}^\dagger) (\boldsymbol{p}-\boldsymbol{p}^\dagger). \label{taylor-approx-g}\tag{3.6}
$$

We can use these results to approximate the posterior probability distribution
around the best fit parameters:

$$P(\boldsymbol{p}|\boldsymbol{y}) \approx K \cdot \exp\left(-\frac{1}{2} (\boldsymbol{p}-\boldsymbol{p}^\dagger)^T\, \boldsymbol{H}_g(\boldsymbol{p}^\dagger) (\boldsymbol{p}-\boldsymbol{p}^\dagger)\right), \label{posterior-p-approximation}\tag{3.7}$$

where $$K\in\mathbb{R}$$ is a constant of integration that also absorbs the constant
first term in $$\eqref{taylor-approx-g}$$. It acts as the normalization. This
turns out to be the a [multivariate Gaussian distribution](https://en.wikipedia.org/wiki/Multivariate_normal_distribution)
with expected value $$\boldsymbol{p}^\dagger$$ and covariance matrix $$\boldsymbol{H}_g^{-1}(\boldsymbol{p}^\dagger)$$.

$$\boldsymbol{C}_{p^\dagger} = \boldsymbol{H}_g^{-1}(\boldsymbol{p}^\dagger) \approx \left( \boldsymbol{J}_{r_w}^T (\boldsymbol{p}^\dagger) \boldsymbol{J}_{r_w}(\boldsymbol{p}^\dagger)\right)^{-1} = (\boldsymbol{J}_f^T(\boldsymbol{p}^\dagger) \; \boldsymbol{W}^T\boldsymbol{W} \;\boldsymbol{J}_f(\boldsymbol{p}^\dagger))^{-1}, \label{covariance-matrix-known-weights} \tag{3.9}$$

where $$\boldsymbol{J}_f$$ is the Jacobian of $$\boldsymbol{f}(\boldsymbol{p})$$
and thus $$\boldsymbol{J}_{r_w} = -\boldsymbol{W}\boldsymbol{J}_f$$. We
have used the common approximation for the Hessian of $$g$$ as given in eq. $$\eqref{hessian-g-approx}$$.
Note, that eq. $$\eqref{covariance-matrix-known-weights}$$ is the covariance for _known standard deviations_, where the weights
must be chosen as specified in $$\eqref{weights-known-sigma}$$.

This concludes our analysis for the case of known standard deviations. Let's now
turn to cases where we don't know the standard deviations.

# 4. Nonlinear Least Squares with Unknown Standard Deviations with a Known Relative Scaling

Okay, the section heading is a mouthful, but it's important to be precise. We'll examine
a special case of unknown standard deviations, which is as follows: Assume that
the exact standard deviations are unknown, but that we (again, _for some reason_) 
know a relative scaling between them, formally:

$$\sigma_j = w_j \, \sigma, \label{relative-scaling} \tag{4.1} $$

where $$\sigma\in\mathbb{R}$$ is unknown, but the relative scaling $$w_j$$ _is_ known. We'll
see that the naming of $$w_j$$ is not an accident, because if we set

$$\boldsymbol{W} = \text{diag}(w_1,\dots,w_{N_y}) \label{relative-weights-matrix}\tag{4.2}, $$

then we can rewrite the posterior as:

$$\begin{eqnarray}
P(\boldsymbol{p} | \boldsymbol{y}) &\propto& \int_0^\infty \frac{1}{\sigma^{N_y}}\exp\left(-\frac{1}{2\sigma^2} \sum_{j=1}^{N_y} \frac{(y_j - f_j(\boldsymbol{p}))^2}{w_j^2} \right) P(\boldsymbol{p},\sigma)\; \text{d}\sigma\label{posterior-rel-sigma}\tag{4.3} \\
 &=& \int_0^\infty \frac{1}{\sigma^{N_y}}\exp\left(-\frac{1}{2\sigma^2} \lVert \boldsymbol{r}_w(\boldsymbol{p})\rVert^2\right) P(\boldsymbol{p},\sigma)\; \text{d}\sigma, \label{posterior-rel-sigma-r2} \tag{4.4}
\end{eqnarray}$$

where $$\boldsymbol{W}$$ must be defined as in eq. $$\eqref{relative-weights-matrix}$$ and
$$\boldsymbol{r}_w$$ is defined as in eq. $$\eqref{weighted-residuals}$$. This is
already a much simpler expression than the more general posterior in eq. $$\eqref{posterior}$$,
since the integral now is only along the one scalar $$\sigma$$. However, we still need
a joint prior distribution for $$P(\boldsymbol{p},\sigma)$$.

## 4.1 Uniform Prior 

Since the uniform prior for $$P(\boldsymbol{p})$$ did pretty well for us in the
case of known standard deviations, let's see what we can achieve when we assume
a uniform prior for the joint distribution like so:

$$P(\boldsymbol{p},\sigma) = \text{const.}$$

This leads us (using a [little help from Wolfram Alpha](https://www.wolframalpha.com/input?i=int%281%2Fsigma%5EN*exp%28-1%2F%282*sigma%5E2%29*+r%5E2%29%29))
to the following expression for the posterior distribution, where we have omitted all constants:

$$P(\boldsymbol{p}| \boldsymbol{y}) \propto (\lVert \boldsymbol{r}_w(\boldsymbol{p})\rVert^2)^{-\frac{N_y-1}{2}}. \label{posterior-uniform-prior}\tag{4.5}$$

Glossing over the fact that this is possibly an [improper posterior](https://onlinelibrary.wiley.com/doi/full/10.1111/sjos.12550),
we can already see that the posterior probability is maximal exactly at the least squares
estimate $$\boldsymbol{p}^\dagger$$ as given in the introduction in eq. $$\eqref{lsqr-fitting}$$. 

### 4.1.2 Laplace's Approximation

Now, we'll employ a common step in Bayesian analysis to make the posterior
probability more tractable by approximating it as a Gaussian. This is an approximation that can,
in principle, be applied to all posterior probabilities with varying degrees of
accuracy. It's called [Laplace's Approximation](https://en.wikipedia.org/wiki/Laplace%27s_approximation)
and we will quickly go through it step by step, independent of our specific
posterior. We'll get back to eq. $$\eqref{posterior-uniform-prior}$$
To start, we define the negative log-posterior as 

$$L(\boldsymbol{p}) = -\log P(\boldsymbol{p}|\boldsymbol{y}). \label{log-posterior}\tag{4.6}$$

Maximizing the posterior probability with respect to the parameters is obviously
the same as minimizing the negative log-posterior. Let's denote the parameter that
minimizes $$L$$ with $$\boldsymbol{p}^\star$$. Note that in our case 
$$\boldsymbol{p}^\star=\boldsymbol{p}^\dagger$$ is just the least squares estimate
as defined in eq. $$\eqref{lsqr-fitting}$$. 

$$\boldsymbol{p}^\star = \arg \min_{\boldsymbol{p}} L(\boldsymbol{p})$$ 

Now, just like we did [in this section](/blog/2024/bayesian-nonlinear-least-squares/#31-the-covariance-matrix-for-the-best-fit-parameters),
we can approximate $$L(\boldsymbol{p})$$ by a second order Taylor expansion around
it's minimum

$$
L(\boldsymbol{p}) \approx L(\boldsymbol{p}^\star) + \frac{1}{2} (\boldsymbol{p}-\boldsymbol{p}^\star)^T\, \boldsymbol{H}_L(\boldsymbol{p}^\star) (\boldsymbol{p}-\boldsymbol{p}^\star), \label{taylor-approx-L}\tag{4.7}
$$

where $$\boldsymbol{H}_L(\boldsymbol{p}^\star)$$ is the Hessian of $$L$$ evaluated
at the minimum $$\boldsymbol{p}^\star$$. By inverting eq. $$\eqref{log-posterior}$$
we can approximate the posterior as

$$P(\boldsymbol{p}|\boldsymbol{y}) \approx K^\star \cdot \exp\left(-\frac{1}{2} (\boldsymbol{p}-\boldsymbol{p}^\star)^T\, \boldsymbol{H}_L(\boldsymbol{p}^\star) (\boldsymbol{p}-\boldsymbol{p}^\star) \right),\label{posterior-p-approximation-L}\tag{4.8}$$

which is a multivariate normal distribution with covariance matrix

$$\boldsymbol{C}_{p^\star} = \boldsymbol{H}_L^{-1}(\boldsymbol{p}^\star). \label{covariance-HL}\tag{4.9}$$

That means we can estimate the covariance of the best fit parameters under this
approximation as the inverse of the Hessian of $$L$$ at the best fit parameters.

### 4.1.3 Covariance of the Best Fit Parameters

To find the covariance matrix for the best fit parameters given our prior, we
have to calculate $$L(\boldsymbol{p})$$ and its Hessian at the best fit parameters.

$$L(\boldsymbol{p}) = -\log P(\boldsymbol{p}|\boldsymbol{y}) = \frac{N_y-1}{2} \log \lVert \boldsymbol{r}(\boldsymbol{p})\rVert^2. \label{L-uniform}\tag{4.10}$$ 

After some calculations (which I have relegated to the appendix), we see that
we can approximate the Hessian as

$$\boldsymbol{H}_L(\boldsymbol{p}^\dagger)\approx \frac{2}{\lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2}\boldsymbol{J}^T_{r_w}(\boldsymbol{p}^\dagger) \boldsymbol{J}_{r_w}(\boldsymbol{p}^\dagger) \label{hessian-uniform}\tag{4.11},$$

which finally leads us to an approximation of the covariance matrix of the best fit
parameters as

$$\boldsymbol{C}_{p^\dagger} \approx \frac{\lVert \boldsymbol{r}(\boldsymbol{p^\dagger})\rVert^2}{N_y-1} (\boldsymbol{J}^T_{r_w}(\boldsymbol{p}^\dagger) \boldsymbol{J}_{r_w}(\boldsymbol{p}^\dagger))^{-1}. \label{cov-uniform}\tag{4.12}$$

It's important to note that this covariance matrix holds only for the assumptions
made in section 4.1 up to here. I'll have more to say about the exact form of the
covariance matrix, but I'll say it in a dedicated section further below. Next,
let's see how the choice of prior influences our estimation of the covariance
matrix of the best fit parameters.

## 4.2 Jeffrey's Prior

[Jeffrey's prior](https://en.wikipedia.org/wiki/Jeffreys_prior) is another commonly
used prior distribution that conveys gross ignorance about the scale of unknown
parameters (Gel13, sections 2.8, 3.2).

!!!
As I mentioned before,

# 5. !!!!!!!!!!! summary section relating lsqr to bayesian coeff via a table or something
# !!! prefactor sigma-dash and weight matrix for different assumptions

# 6. Credible Intervals for the Best Fit Model

Let's take a step back and look at what we have done above: we have related
how the uncertainties in $$\boldsymbol{y}$$ [propagate to the uncertainties](https://en.wikipedia.org/wiki/Propagation_of_uncertainty)
in $$\boldsymbol{p}^\dagger$$. The covariance matrix of the best fit parameters 
allows us to give confidence intervals of the parameters via their standard deviations,
since posterior distributions for the parameters were approximately normal.

Now we will do the same thing again, in a way. We are now interested what the uncertainties in $$\boldsymbol{p}^\dagger$$ tell
us about the uncertainties of the best-fit solution $$\boldsymbol{f}(\boldsymbol{p})$$.
The information we are most interested in, are the standard deviations for each
element $$f_j$$. If we know those, we can give intervals around each $$f_j$$, which
together make up the confidence band around the best fit solution.

We treat $$\boldsymbol{z}=\boldsymbol{f}(\boldsymbol{p})$$ as a new variable
and we are interested in the probability distribution of $$\boldsymbol{z}$$,
which we can obtain from the posterior probability distribution of $$\boldsymbol{p}$$
by performing a [change of variables](https://en.wikipedia.org/wiki/Probability_density_function#Function_of_random_variables_and_change_of_variables_in_the_probability_density_function),
where I am following the notation of Sivia and Skilling (Siv06):

$$
P(\boldsymbol{z}|\boldsymbol{y}) = P(\boldsymbol{p}=\boldsymbol{f}^{-1}(\boldsymbol{z})|\boldsymbol{y})\cdot \text{det} \frac{d\boldsymbol p}{d \boldsymbol{z}} \label{change-of-var}\tag{13},
$$

where the factor on the right hand side is the determinant of the Jacobian of $$\boldsymbol{p}$$
with respect to $$z$$. To get a grip on this expression we approximate $$\boldsymbol{y}$$
around the best fit parameters by a first order Taylor series:

$$\boldsymbol{z} = \boldsymbol{f}(\boldsymbol{p}) \approx \boldsymbol{f}(\boldsymbol{p}^\dagger) + \boldsymbol{J}_f(\boldsymbol{p}^\dagger)\,(\boldsymbol{p}-\boldsymbol{p}^\dagger),$$

where $$\boldsymbol{J}_f(\boldsymbol{p}^\dagger)$$ is the Jacobian of $$\boldsymbol{f}(\boldsymbol{p})$$
evaluated at $$\boldsymbol{p}^\dagger$$. Note, that there is nothing about $$\boldsymbol{p}^\dagger$$
that would make this approximation particularly well-suited, in contrast to
the approximation in eq. $$\eqref{taylor-approx-g}$$.
We just use it because it is analytically convenient. This allows us to write

$$ \boldsymbol{p} = \boldsymbol{f}^{-1}(\boldsymbol{z}) \approx \boldsymbol{J}_f^{-1}(\boldsymbol{p}^\dagger) (\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger))+\boldsymbol{p}^\dagger$$

If we go ahead and plug
this approximation and eq. $$\eqref{posterior-p-approximation}$$ into eq. $$\eqref{change-of-var}$$, the determinant becomes
a constant and we can write:

$$\begin{eqnarray}
P(\boldsymbol{z}|\boldsymbol{y}) &\approx& K'\cdot \exp\left(-\frac{1}{2} (\boldsymbol{J_f}^{-1}(\boldsymbol{p}^\dagger)(\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger)))^T\, \boldsymbol{H}_g(\boldsymbol{p}^\dagger) (\boldsymbol{J_f}^{-1}(\boldsymbol{p}^\dagger)(\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger))) \right) \\
  &=&  K'\cdot \exp\left(-\frac{1}{2} (\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger))^T\, (\boldsymbol{J_f}^T)^{-1}(\boldsymbol{p}^\dagger)\boldsymbol{H}_g(\boldsymbol{p}^\dagger) \boldsymbol{J_f}^{-1}(\boldsymbol{p}^\dagger)(\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger)) \right) \\
  &=&  K'\cdot \exp\left(-\frac{1}{2} (\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger))^T\, (\boldsymbol{J_f}^T)^{-1}(\boldsymbol{p}^\dagger) \boldsymbol{C}_{p^\dagger}^{-1} \boldsymbol{J_f}^{-1}(\boldsymbol{p}^\dagger)(\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger)) \right) \\
  &=&  K'\cdot \exp\left(-\frac{1}{2} (\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger))^T\, (\boldsymbol{J_f}(\boldsymbol{p}^\dagger) \boldsymbol{C}_{p^\dagger} \boldsymbol{J_f}^{T}(\boldsymbol{p}^\dagger))^{-1} (\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger)) \right) \\
  &=&  K'\cdot \exp\left(-\frac{1}{2} (\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger))^T\, \boldsymbol{C}_f^{-1} (\boldsymbol{z}-\boldsymbol{f}(\boldsymbol{p}^\dagger)) \right) ,
\end{eqnarray}$$

where we have absorbed all constant factors into $$K'$$. We can see that this is
again a [multivariate normal](https://en.wikipedia.org/wiki/Multivariate_normal_distribution)
with a covariance matrix of $$\boldsymbol{C}_f$$. That means that we can calculate
the covariance of the model values at the best fit parameters under this approximation
as:

$$\boldsymbol{C}_f = \boldsymbol{J_f}(\boldsymbol{p}^\dagger) \boldsymbol{C}_{p^\dagger} \boldsymbol{J_f}^{T}(\boldsymbol{p}^\dagger) \label{cov-f}\tag{14}.$$

In essence, we have derived the law of [Propagation of Uncertainty](https://en.wikipedia.org/wiki/Propagation_of_uncertainty)
for our special case[^prop-uncertainty]. The well-known formula for propagation of uncertainty
is also derived under the approximation of linearity of the transformation.

## From Covariance Matrix to Credible Intervals

So now that we have the covariance matrix, how do we use it to construct
[credible intervals](https://en.wikipedia.org/wiki/Credible_interval#Contrasts_with_confidence_interval)
around the best fit function[^conf-bands]? Luckily we already know everything we need.

We have approximated the elements of $$\boldsymbol{f}(\boldsymbol{p^\dagger})$$ values as
normally distributed with a covariance matrix of $$\boldsymbol{C}_f$$. That means
that the variance for each entry $$f_j$$ of $$\boldsymbol{f}$$ is on index $$j$$
of the diagonal of $$\boldsymbol{C}_f$$. Let's express this in vector notation:

$$(\sigma_{f_1}^2,\dots,\sigma^2_{f_{N_y}})^T = \text{diag} (\boldsymbol{C}_f). \label{variance-vector}\tag{15}$$

It would be numerically wasteful to calculate the whole matrix $$\boldsymbol{C}_f$$
just to then immediately discard everything except the diagonal elements. There
is a better way. To see this, we write the Jacobian as a collection using row-vectors:

$$
\boldsymbol{J}_f(\boldsymbol{p}^\dagger) = \begin{bmatrix}
- \boldsymbol{j}_1^T -\\
- \boldsymbol{j}_2^T -\\
\vdots \\
- \boldsymbol{j}_n^T -
\end{bmatrix},
$$

where $$\boldsymbol{j}_i^T$$ is the $$i$$-th _row_ of the Jacobian of $$\boldsymbol{f}$$ at the
best fit parameters. Now we can write the variance for each element of $$\boldsymbol{f}$$
as

$$\sigma_{f_i}^2 = \boldsymbol{j}_i^T \boldsymbol{C}_f \boldsymbol{j}_i, \label{efficient-sigma-f}\tag{16}$$

where, again $$\boldsymbol{j}_i^T$$ is a _row_ vector representing a row of the Jacobian.
Wolberg arrives at the same formula using a slightly different approach (Wol06, section 2.5).
Using this way of calculating the variances saves a significant amount of computations
and should be preferred to calculating the complete matrix product. The credible
intervals for a given probability can now be obtained using the quantile function
of the normal distribution. 

!!!!!!!!TODO gaussian quantiles credible band radius
!!!!!!!!!!!!!!

As a final note to this already very long article, we note that Wolberg gives
an almost identical expression for the confidence bands around the best fit
parameters (Wol06, section 2.6). The only difference is that he uses the 
quantile function of Student's t-distribution instead of the Gaussian quantile
function, but unfortunately no rationale is provided for that.

# Conclusion

I know article was a _tour de force_ through the method of nonlinear least squares
fitting from the ground up. I hope that seeing it like this helps others (as it helped
me) to demystify and understand the method itself, but especially the statistical analysis
of the parameters and the best fit model. This part is often overlooked. If your usecase
is not covered by this article, I hope that you'll find the tools here to modify
the calculations according to your needs. And finally, if you find errors please
let me know via mail or by commenting below.

# References
(Noc06) J Nocedal & SJ Wright: "Numerical Optimization", Springer, 2nd ed, 2006

(Siv06) D Sivia & J Skilling: "Data Analysis - A Bayesian Tutorial", Oxford University Press, 2<sup>nd</sup> ed, 2006

(Wol06) J Wolberg: "Data Analysis Using the Method of Least Squares", Springer, 2006

(Gel13) A Gelman _et al_: "Bayesian Data Analysis", CRC Press, 3<sup>rd</sup> ed, 2013 ([freely available from the author](http://www.stat.columbia.edu/~gelman/book/))

(Kal22) M Kaltenbach: "The Levenberg-Marquardt Method and its Implementation in Python", Diploma Thesis, Uni Konstanz, 2022, ([link](http://nbn-resolving.de/urn:nbn:de:bsz:352-2-1ofyba49ud2jr5))

# Appendix

## A. Calculating the Hessian of $$\log \lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2$$

To derive eq. $$\eqref{hessian-uniform}$$ we need to calculate the Hessian of 
$$\log \lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2$$. Let's do the calculation
element wise by repeatedly applying the chain rule. 

$$\begin{eqnarray}
\boldsymbol{H}\{\log \lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2\}_{kl} &=& \frac{\partial^2}{\partial p_k \partial p_l}\log\lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2 \\
 &=& \frac{\partial}{\partial p_k} \left(\frac{1}{\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2} \cdot \frac{\partial}{\partial p_l}\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2\right) \\
 &=& \frac{\partial}{\partial p_k} \frac{1}{\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^{2}}\cdot \frac{\partial}{\partial p_l}\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2+\frac{\partial^2}{\partial p_k\partial p_l}\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2 \\ 
 &=& \frac{\partial}{\partial p_k} \frac{1}{\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^{2}}\cdot \frac{\partial}{\partial p_l}\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2+ \frac{1}{\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2}\boldsymbol{H}\{\lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2\}_{kl}\\ 
\end{eqnarray}$$

We are interested in evaluating the Hessian at an extremum of $$\log \lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2$$,
which implies that $$\nabla \log\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2=\boldsymbol{0}$$,
which implies $$\nabla \lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2=\boldsymbol{0}$$,
which implies $$\frac{\partial}{\partial p_l} \lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2=0$$
for all indices $$l$$. That makes the first term in the equation vanish, so that
we can write the hessian of the log transformed sum of squares as:

$$
\boldsymbol{H}\{\log \lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2\}(\boldsymbol{p}^\dagger) = \frac{1}{\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2}\boldsymbol{H}\{\lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2\}(\boldsymbol{p}^\dagger)
$$

We know an approximation for the Hessian of $$\frac{1}{2}\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2$$
from eq. $$\eqref{hessian-g-approx}$$, so that we can write:

$$
\boldsymbol{H}\{\log \lVert \boldsymbol{r}(\boldsymbol{p}) \rVert^2\}(\boldsymbol{p}^\dagger) \approx \frac{2}{\lVert\boldsymbol{r}(\boldsymbol{p}) \rVert^2} \boldsymbol{J}_{r_w}^T(\boldsymbol{p}^\dagger)\boldsymbol{J}_{r_w}(\boldsymbol{p}^\dagger)
$$

Now  $$\eqref{hessian-uniform}$$ follows trivially.

## B. Calculating Jeffrey's Prior

To calculate [Jeffrey's prior](https://en.wikipedia.org/wiki/Jeffreys_prior), we
first have to calculate the Fisher information matrix. For a given likelihood
$$P(\boldsymbol{y}|\boldsymbol{\theta})$$, where $$\boldsymbol{\theta}$$
are the parameters, the elements of the [Fisher information matrix](https://en.wikipedia.org/wiki/Fisher_information#Matrix_form)
$$\boldsymbol{I}(\boldsymbol{\theta}$$ are given as:

$$[\boldsymbol{I}(\boldsymbol{\theta})]_{kl} = E\left[ \left. \left(\frac{\partial}{\partial \theta_k}\log P(\boldsymbol{y}|\boldsymbol{\theta}) \right)\left(\frac{\partial}{\partial \theta_l}\log P(\boldsymbol{y}|\boldsymbol{\theta}) \right) \right| \boldsymbol{\theta}\right],$$

where $$E[ \boldsymbol{\phi}(\boldsymbol{y})\vert\boldsymbol{\theta}]=\int \boldsymbol{\phi}(\boldsymbol{y}) P(\boldsymbol{y}|\boldsymbol{\theta}) \text{d}\boldsymbol{y}$$ denotes the expected value 
of $$\boldsymbol{\phi}(\boldsymbol{y})$$. Note that this is a volume integral over
$$\boldsymbol{y}$$, but we won't actually have to calculate it like this in the
following derivations. For the following sections we'll abbreviate $$E[\boldsymbol{\phi}(\boldsymbol{y})\vert\boldsymbol{\theta}]$$
as $$E[\boldsymbol{\phi}(\boldsymbol{y})]$$ purely for notational convenience.

In our case, the parameter vector $$\boldsymbol{\theta}$$ consists of the elements 
of the vector $$\boldsymbol{p}$$ and the single scalar $$\sigma$$:

$$\boldsymbol{\theta} = (\boldsymbol{p}^T,\sigma)^T.$$

That means $$\boldsymbol{\theta}\in \mathbb{R}^{N_p+1}$$, which means the 
derivative $$\partial/\partial \theta_k = \partial/\partial p_k$$ for $$k=1,\dots,N_p$$ 
and $$\partial/\partial \theta_{N_p+1} = \partial/\partial \sigma$$. That means
we can write the Fisher information matrix as a block matrix like so:

$$I(\boldsymbol{p},\sigma) = \left(\begin{matrix} \boldsymbol{I}_{PP}(\boldsymbol{p},\sigma) & \boldsymbol{I}_{P\sigma}(\boldsymbol{p},\sigma) \\
                           \boldsymbol{I}_{P\sigma}(\boldsymbol{p},\sigma) & I_{\sigma\sigma} \\
\end{matrix}\right)$$
                    




!!!!!!!!!!!!!! todo

# Endnotes
[^a-posteriori]: Maximizing the likelihood is the equivalent to maximizing the posterior probability, given uniform priors.
[^uniform-prior]: Some problems arise when thinking in depth about the meaning of uniform priors. Those don't have a lot of practical importance, but are interesting nonetheless. They are discussed e.g. in Sivia's brilliant [Data Analysis - A Bayesian Tutorial](https://global.oup.com/academic/product/data-analysis-9780198568322https://global.oup.com/academic/product/data-analysis-9780198568322).
[^log-likelihood]: Maximizing the posterior is the same as minimizing the negative logarithm of the posterior $$L(p)=-\log\,P(p\vert y)$$, which leads us again to the least squares minimization expression at the start of the article.
[^gsl-weights]: Note that they use a slightly different definition for the weight matrix. The meaning is equivalent, but they don't square the weight matrix with the residual, so that it appears differently in the formulae.
[^prop-uncertainty]: The formula for propagation of uncertainty is also derived under the approximation of linearity of the transformation.
[^exercise-reader]: Finally I have an opportunity to be the one writing it.
[^ignorance]: Priors conveying ignorance are actually surprisingly tricky. We'll see another one of those that has a vastly different functional form later.
[^conf-bands]: Credible intervals are not (quite) the same as [confidence bands](https://en.wikipedia.org/wiki/Confidence_and_prediction_bands). The former are a Bayesian concept, while the latter are a frequentist concept. Both serve a conceptually similar purpose.
