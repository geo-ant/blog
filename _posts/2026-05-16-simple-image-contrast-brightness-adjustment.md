---
layout: post
tags: image-processing least-squares
#categories: []
date: 2026-04-17
last_updated:
#excerpt: ''
#image:
#description:
#permalink:
title: "A Simple Image Brightness And Contrast Adjustment Technique"
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

I recently found myself squinting at two images at work and wondering if one
is actually "better" than the other. The two images were
showing the same object but they had slightly _but noticeably_ different value
ranges. That made it hard for me to understand which of the differences were
due to display brightness and contrast settings and which were part of the
actual structure of the image. Then I remembered a simple technique that
I've been using on and off since my PhD days.

# The Problem

So let's say we have two images $$\boldsymbol{I}$$ and $$\boldsymbol{J}$$ we
want to normalize to a common brightness range. Despite showing the same
structures, maybe we have generated the two images using slightly different
processing techniques. The structures of interest might present a little differently,
but also the value ranges might be shifted noticeably between the images. Using
the minimum and maximum values to normalize the value ranges is often a bad idea
because those properties can be very sensitive to noise. On the other hand,
using the mean or mode to scale one image to the other is often good enough,
but gives us only one degree of freedom. Note that we assume that the images
are spatially aligned and the only thing we want to correct is a brightness
transform.

# A Simple Brightness Transform

Now let's find a simple brightness transform that maps image $$\boldsymbol{J}$$
to image $$\boldsymbol{I}$$. Let's allow a linear brightness transform with
coefficients because such a transform is typically so constrained that it won't
alter the structures of interest. It will only help us shift one image to the
value range of the other image to make it comparable[^template]. Every pixel
$$J_k$$ at index $$k$$ of image $$\boldsymbol{J}$$ is transformed as[^pixel-index]:

$$J_k \mapsto a J_k + b, \tag{1} \label{transform}$$

where $$a, b \in \mathbb{R}$$ are the coefficients of the transformation.
So, what are the _best_ coefficients $$a, b$$ such that the brightness
variations between the images are minimized? Well, we can e.g. minimize
the pixelwise deviations of the images in a least squares sense[^lsqr]:

$$\min_{a,b} \frac{1}{N} \sum_{k=1}^{N} \left( a J_k +b - I_k \right)^2 \tag{2} \label{ols}$$

The neat thing is that there's an analytical solution for the coefficients,
which can be found by simply calculating the point at which the partial
derivatives $$\partial/\partial a, \partial/\partial b$$ of the expression
both vanish. After some rewriting this leads us to:

$$\begin{eqnarray}
a &=& \frac{\text{cov}(\boldsymbol{I},\boldsymbol{J})}{\text{var}(\boldsymbol{J})} \label{a-ols} \tag{3a}\\
b &=& \text{mean}(\boldsymbol{I}) - a\cdot \text{mean}(\boldsymbol{J}) \label{b-ols} \tag{3b},
\end{eqnarray}$$

where $$\text{mean}$$ calculates the mean value of an image,
$$\text{cov}$$ is the [covariance](https://en.wikipedia.org/wiki/Covariance),
and $$\text{var}$$ is the [variance](https://en.wikipedia.org/wiki/Variance):

$$\begin{eqnarray}
\text{mean}(\boldsymbol{I}) &=& \frac{1}{N} \sum_{k=1}^{N} I_k \tag{4a} \label{mean}\\
\text{cov}(\boldsymbol{I},\boldsymbol{J}) &=& \frac{1}{N-1} \sum_{k=1}^{N} (I_k-\text{mean}(\boldsymbol{I}))\cdot(J_k- \text{mean}(\boldsymbol{J})) \tag{4b} \label{cov}\\
\text{var}(\boldsymbol{J}) &=& \text{cov}(\boldsymbol{J},\boldsymbol{J}) \tag{4c} \label{var}
\end{eqnarray}$$

That means using eq. $$\eqref{transform}$$ with coefficients from $$\eqref{a-ols}$$
and $$\eqref{b-ols}$$ to adjust the brightness values in image $$\boldsymbol{J}$$
will adjust the image to fit the brightness range of image $$\boldsymbol{I}$$.

## Weighted Least Squares

There's one more improvement to the technique we can make quite easily, which
is to use _weighted least squares_ as the minimization objective rather than
the _ordinary least squares_ we used above. This allows us to give each
pixel $$k$$ a corresponding weight $$w_k$$ that modifies its contribution to
the objective function. For example, if our images contain large areas of
near-zero background, we could force areas with higher signal to contribute
more strongly by setting the weights as $$w_k = I_k$$; we could also set the
weights for pixels below a threshold to $$0$$. There are many possible
ways to improve the optimization with weighting.

For weighted least squares, our minimization objective becomes

$$\min_{a,b} \frac{1}{N} \sum_{k=1}^{N} w_k \left( a J_k +b - I_k \right)^2 \tag{5} \label{wls},$$

and we can find very similar analytical solutions for the coefficients

$$\begin{eqnarray}
a &=& \frac{\text{cov}_{\boldsymbol{w}}(\boldsymbol{I},\boldsymbol{J})}{\text{var}_{\boldsymbol{w}}(\boldsymbol{J})} \label{a-wls} \tag{6a}\\
b &=& \text{mean}_{\boldsymbol{w}}(\boldsymbol{I}) - a\cdot \text{mean}_{\boldsymbol{w}}(\boldsymbol{J}) \label{b-wls} \tag{6b}.
\end{eqnarray}$$

Now we have to use the _weighted_ mean, covariance, and variance defined as

$$\begin{eqnarray}
\text{mean}_{\boldsymbol{w}}(\boldsymbol{I}) &=& \frac{1}{\sum_{k=1}^N w_k} \sum_{k=1}^{N} w_k I_k \tag{7a} \label{mean-w}\\
\text{cov}_{\boldsymbol{w}}(\boldsymbol{I},\boldsymbol{J}) &=& \frac{N}{N-1}\frac{\sum_{k=1}^{N} w_k (I_k-\text{mean}_{\boldsymbol{w}}(\boldsymbol{I}))\cdot(J_k- \text{mean}_{\boldsymbol{w}}(\boldsymbol{J}))}{\sum_{k=1}^N w_k}  \tag{7b} \label{cov-w}\\
\text{var}_{\boldsymbol{w}}(\boldsymbol{J}) &=& \text{cov}_{\boldsymbol{w}}(\boldsymbol{J},\boldsymbol{J}) \tag{7c} \label{var-w}
\end{eqnarray}$$

# Prior Art and Further Reading

Obviously, I wasn't the first to come up with this least-squares-based linear
brightness normalization technique. In remote sensing it's known as
_radiometric normalization_ and described, e.g., by [Zhang _et al._](https://www.tandfonline.com/doi/full/10.1080/01431160701271990?scroll=top&needAccess=true)
[^zhang]. The results in this article are found in eqn. (1) and (2) in the paper.
The authors also propose an iterative reweighting that goes beyond the
scope of this article. For a much more sophisticated framework specific to this field, see
[Canty _et al_.](https://www.sciencedirect.com/science/article/abs/pii/S0034425707003495)
[^canty]

# Outlook

This simple technique is already pretty powerful for two images. The one thing
we implicitly did was pick one image as the template, in our case image $$\boldsymbol{I}$$,
and transform the other image into its brightness range. How do we know which
image to pick? This might seem pedantic for two images, but the problem becomes
more obvious if we have a set of more than 2 images that we want to transform
into the same brightness range. We can certainly choose one image as a template
and transform all others into its brightness range, and often that is just fine.
But what if the one image is an outlier and corrupted by noise or artifacts?
Least squares isn't famous for dealing well with outliers anyway, but in this
case it's more obvious that the choice of template image can introduce an
unfavorable bias.

Those considerations quickly get us into the territory of joint optimizations
and _latent images_, where the math and algorithms get really interesting really
fast, despite our simple model. I might tackle this in a follow-up article.

# Endnotes
[^pixel-index]: We can use a linear index for the pixels instead of $x,y$ because the position does not matter for our model. The important thing is that each value of $$k$$ corresponds to the same unique pixel position in both images.
[^template]: We have implicitly designated image $$\boldsymbol{I}$$ as the _template image_. It might not seem obvious, but it _does_ matter which image we map to which. If the images are sufficiently similar, this isn't a problem and in practice we can always try to map the other way round to see if the results are better. While it's still a theoretical problem in the two-image case, it becomes much more of a practical problem which image we select as the template image. There are also formulations that don't require a template image, but assume the existence of a _latent image_ and reformulate the problem.
[^lsqr]: Least squares fitting has a couple of nice properties. First of all, it emerges as the maximum likelihood estimator of Gaussian probability distributions. Second of all, it is very tractable analytically. Both things make it appealing for our use case, though a formal Bayesian description of our image mapping process can get tricky quickly. So we'll allow ourselves to use least squares here because it's a good heuristic.
[^zhang]: See [here](https://www.researchgate.net/publication/234800535_Automatic_relative_radiometric_normalization_using_iteratively_weighted_least_square_regression) for a PDF copy.
[^zhang2]: They use a slightly different multiplier for variance and covariance than presented here, but it doesn't matter because that cancels out anyways.
[^canty]: See [here](https://www2.imm.dtu.dk/pubdb/pubs/5362-full.html) for a PDF version.
