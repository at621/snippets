Below is a high‐level illustration of how one can implement each of the three “portfolio‐level” Vasicek‐type methods in Python, given *only* a time‐series of overall (annual) portfolio default rates (i.e.\ without transition matrices). We assume you have 10 annual observations of historical default rates.

---
## 1) **Indirect Moment Approach**

### Conceptual Overview

In the “indirect moment” approach (sometimes referred to as a moment‐matching approach), one uses the fact that in the one‐factor Vasicek setup:

\[
\text{PD} 
\;=\; 
\Phi\!\Bigl(
  \frac{k - \sqrt{\rho}\,Z}{\sqrt{1-\rho}}
\Bigr),
\]

where 
- \(\Phi(\cdot)\) is the standard normal CDF,  
- \(\rho\) is the asset (default) correlation,  
- \(k\) is the “threshold” (sometimes also called the “distance to default” boundary),  
- \(Z\sim N(0,1)\) is the systematic factor.

By inverting the observed default rates via the standard normal quantile (the “z‐score” of the observed PD), one can derive sample statistics (mean and standard deviation) of those inverted values.  Under certain simplifying assumptions, one obtains the relationships (see many standard references on Vasicek single‐factor models):

\[
\text{mean}\bigl(\Phi^{-1}(\text{PD})\bigr)
  \;=\;
  \frac{k}{\sqrt{1-\rho}},
\qquad
\text{stdev}\bigl(\Phi^{-1}(\text{PD})\bigr)
  \;=\;
  \frac{\sqrt{\rho}}{\sqrt{1-\rho}}.
\]

Hence one can solve directly for \(\rho\) and \(k\):

1. From the standard deviation relationship:
   \[
     \sigma_{\text{PD-inv}} \;=\; \frac{\sqrt{\rho}}{\sqrt{1-\rho}}
     \;\;\Longrightarrow\;\;
     \rho \;=\; 
     \frac{\sigma_{\text{PD-inv}}^{2}}{\,1 + \sigma_{\text{PD-inv}}^{2}\!}.
   \]

2. From the mean relationship:
   \[
     k 
     \;=\; 
     \mu_{\text{PD-inv}}
     \,\sqrt{\,1-\rho\,}\,.
   \]

Once \(\rho\) and \(k\) are found, you can back out year‐by‐year estimates of the systematic factor \(Z_t\) or re‐compute a “worst‐case” PD if needed.

### Python Example

```python
import numpy as np
import pandas as pd
from scipy.stats import norm

# 1) Example data: 10 years of observed annual default rates (in decimal form)
default_rates = np.array([0.01, 0.015, 0.008, 0.012, 0.02,
                          0.018, 0.013, 0.009, 0.017, 0.011])

# 2) Convert observed PDs to “z‐scores” via inverse standard normal
pd_inverted = norm.ppf(default_rates)

# 3) Sample mean and std of these inverted PDs
mu_pd_inv = np.mean(pd_inverted)
sigma_pd_inv = np.std(pd_inverted, ddof=1)  # ddof=1 for sample stdev

# 4) Solve for rho from stdev formula
#    sigma_pd_inv = sqrt(rho)/( sqrt(1-rho) ) ==> rho = s^2 / (1 + s^2)
s2 = sigma_pd_inv**2
rho = s2 / (1 + s2)

# 5) Solve for k from mean formula
#    mu_pd_inv = k / sqrt(1-rho) ==> k = mu_pd_inv * sqrt(1-rho)
k = mu_pd_inv * np.sqrt(1 - rho)

print("Indirect Moment Approach Estimates:")
print(f"  Estimated correlation (rho): {rho:.4f}")
print(f"  Estimated threshold (k):     {k:.4f}")
```

That is the simplest, closed‐form “indirect moment” estimator.  It treats all years identically and relies on the empirical mean/stdev of the inverse‐normal‐transformed default rates.

---

## 2) **Direct Moment (Likelihood) Approach**

### Conceptual Overview

In the “direct moment” approach, one uses the first and second moments of observed default rates more explicitly and sets up a likelihood function based on the Vasicek model assumptions.  Typically:

- Let \(m_1\) be the *average* observed default rate over \(T\) years:  
  \[
    m_1 = \frac{1}{T}\sum_{t=1}^T \text{DR}_t.
  \]
- Let \(m_2\) be the *average of the squared* default rates:  
  \[
    m_2 = \frac{1}{T}\sum_{t=1}^T (\text{DR}_t)^2.
  \]
- We posit that the correlation parameter \(\rho\) and the “true” default probability \(p\) (or threshold \(k\)) produce the best fit to these observed moments (and/or the entire time‐series).

A more rigorous way is to write down the Vasicek‐based probability distribution for a single period’s default rate and then form the joint likelihood over all \(T\) observations.  One then numerically maximizes that likelihood with respect to (\(\rho,\,p\)).  

Below is a *simplified* illustration using a negative log‐likelihood function.  (In practice, one may have to specify how many obligors are in the portfolio each year, whether the distribution is binomial or normal approximation, etc.)

### Python Example (Numerical Optimization)

```python
import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import minimize

# Example data: 10 years of observed default rates (decimal)
default_rates = np.array([0.01, 0.015, 0.008, 0.012, 0.02,
                          0.018, 0.013, 0.009, 0.017, 0.011])
T = len(default_rates)

# We define a negative log-likelihood (NLL) function
# The "direct moment" approach can be cast in many ways, but here is a simple MLE
# under a normal approximation for each year's DR around p with correlation rho:
def vasicek_nll(params):
    # params[0] = p (long-run PD), params[1] = rho
    p, rho = params
    
    # Keep rho in valid range via transform if desired:
    if not (0 < rho < 1):
        return 1e10  # large penalty
    
    # For each year's observed DR, the one-factor model says:
    # DR ~ E[DR] = p,  Var[DR] depends on rho, etc.
    # A simplistic approach is to treat each year's DR_t as drawn from
    # a distribution with mean p and some function of rho. 
    # (In reality, you'd use the binomial-Vasicek or moment-based formula.)
    
    # We'll do a naive normal approximation, stdev ~ sqrt(p*(1-p)/N_eff), adjusted by (1-rho)
    # This part can be changed to match your exact direct-moment formula.
    
    # We'll just use some arbitrary 'N' to represent portfolio size:
    N_eff = 10000  # Example: large portfolio
    var_dr = p*(1-p)/N_eff * (1 + rho)  # toy illustration
    sd_dr = np.sqrt(var_dr)
    
    # negative log-likelihood
    nll = 0.0
    for dr in default_rates:
        # probability density under normal approximation
        pdf_val = 1e-30 + (1/np.sqrt(2*np.pi*sd_dr**2))*np.exp(-0.5*((dr - p)/sd_dr)**2)
        nll -= np.log(pdf_val)
    return nll

# Perform the optimization
x0 = np.array([0.01, 0.2])  # initial guess: p=1%, rho=0.2
bnds = ((1e-5, 0.99), (1e-5, 0.99))  # bounds to keep p and rho in (0,1)
res = minimize(vasicek_nll, x0, bounds=bnds)

if res.success:
    p_hat, rho_hat = res.x
    print("Direct Moment (Likelihood) Approach Estimates:")
    print(f"  p (long-run PD): {p_hat:.4f}")
    print(f"  rho (correlation): {rho_hat:.4f}")
else:
    print("Optimization failed:", res.message)
```

> **Note**  
> - The code above is *illustrative* only: real‐world “direct moment” or “likelihood” calibrations often involve more sophisticated binomial log‐likelihoods or closed‐form moment equations from Vasicek.  
> - You would adapt the negative‐log‐likelihood formula to match exactly how you believe default rates are distributed under the single‐factor model (including finite number of obligors, etc.).  
> - The key idea is that \((p,\,\rho)\) are chosen to *maximize* the likelihood (i.e. *minimize* the negative log‐likelihood).  

---

## 3) **Vasicek Probability Density Function Approach**

### Conceptual Overview

A third approach often seen is to write the full Vasicek PDF for the default rate (or the “loss rate”) and then find the correlation \(\rho\) that maximizes the likelihood of the observed default‐rate time‐series.  In many references, the density of a realized default fraction \(x\) (with mean PD \(m_1\)) under a one‐factor model can be approximated as:

\[
f(x)\;=\;\sqrt{\frac{1-\rho}{\rho}}\;
 \exp\!\biggl[
    0.5\,s(x; m_1)^2
 \biggr], 
\]

where the exponent depends on \(\rho\), \(m_1\), and the second moment \(m_2\).  One then forms the log‐likelihood by summing \(\ln f(\text{DR}_t)\) over \(t=1,\dots,T\) and maximizes w.r.t.\ \(\rho\) (and possibly w.r.t.\ the unconditional PD as well).

Below is a simple illustrative code snippet.

### Python Example (Log‐Likelihood Using Vasicek PDF)

```python
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from math import log, sqrt, exp

# Example data
default_rates = np.array([0.01, 0.015, 0.008, 0.012, 0.02,
                          0.018, 0.013, 0.009, 0.017, 0.011])
T = len(default_rates)

m1_obs = np.mean(default_rates)  # average default rate
m2_obs = np.mean(default_rates**2)  # average of squared DR

# Define a function for the "Vasicek-type" PDF at a single observed DR
# For demonstration, we keep it very simplistic: 
def vasicek_pdf(x, m1, m2, rho):
    """
    Illustrative form of the Vasicek-like density
    (Exact functional forms can vary by reference.)
    """
    if rho<=0 or rho>=1: 
        return 1e-30  # invalid => near 0 density
    
    # A naive example formula (not necessarily the exact one in your reference):
    # f(x) ~ C(rho) * exp(  -some function of (x,m1,m2,rho) )
    
    try:
        const_factor = sqrt((1-rho)/rho)
        
        # Example exponent using difference between x and m1
        # (This is a toy version, you might have the standard -0.5(...)^2 form.)
        # We'll do something proportionate to (x - m1)^2:
        exponent = -0.5 * ((x - m1)/sqrt(m2 - m1**2 + 1e-9))**2 / (1-rho + 1e-9)
        
        val = const_factor * exp(exponent)
        return val if val>1e-30 else 1e-30
    except:
        return 1e-30

def neg_log_likelihood(rho):
    # We treat the unconditional PD (mean) as fixed to the observed average m1
    # (Sometimes you might also optimize over the unconditional PD.)
    
    ll = 0.0
    for x in default_rates:
        fval = vasicek_pdf(x, m1_obs, m2_obs, rho)
        ll += log(fval)
    return -ll  # negative log-likelihood

# Optimize w.r.t. rho
res = minimize(lambda r: neg_log_likelihood(r[0]), x0=[0.2], bounds=[(1e-5, 0.9999)])
if res.success:
    rho_hat = res.x[0]
    print("Vasicek PDF Approach Estimate:")
    print(f"  rho (correlation): {rho_hat:.4f}")
else:
    print("Optimization failed:", res.message)
```

> **Note**  
> - In practice, you would use a more precisely derived PDF for the default‐rate under the one‐factor model (many texts provide the exact formula).  
> - You might *also* want to treat the unconditional PD as an unknown parameter to be fit alongside \(\rho\).  
> - Again, the idea is that each observed default‐rate is assumed to come from that Vasicek distribution, and you maximize the joint likelihood across all years.

---

# Summary of the Three Approaches

1. **Indirect Moment Approach**  
   - Easiest closed‐form.  Simply take all observed default rates, compute their standard‐normal‐inverses, match the sample mean/stdev to the Vasicek mean/stdev formula, and solve for \(\rho\) and \(k\).  
   - Very fast to implement, but can be sensitive to outliers and the normal‐quantile transformation.

2. **Direct Moment (MLE) Approach**  
   - Write down how *each year’s* default rate arises from a distribution parameterized by \(\rho\) and \(p\).  
   - Form a likelihood function or set of moment equations (e.g.\ matching the first and second moments across time).  
   - Numerically find the \((p, \rho)\) that maximize likelihood or best match the empirical moments.

3. **Vasicek PDF Approach**  
   - Use the known closed‐form Vasicek distribution for a portfolio default‐rate (or loss rate).  
   - For each observed default rate, compute the PDF value under that distribution.  
   - Sum (or multiply) over all years to get a likelihood, and maximize w.r.t.\ \(\rho\) (and possibly also the unconditional PD).  

All three methods are *portfolio‐level* in that they use *only* the historical default‐rate time‐series, without needing transition‐matrix details of how loans migrate across states.  They differ primarily in how the correlation \(\rho\) (and threshold \(k\), or unconditional PD \(p\)) gets inferred from those observed default rates.

========================================================
========================================================
========================================================

Below is a more “realistic” end‐to‐end illustration in Python. We will:

1. **Simulate** a 10‐year history of *annual portfolio default rates* using a one‐factor Vasicek model with “true” \(\rho\) and “true” PD (\(p\)).  
2. **Estimate** \(\rho\) (and \(p\) or the threshold \(k\), depending on the method) with each of the three approaches:

   - **Indirect Moment** approach (closed‐form).  
   - **Direct (likelihood‐based) Moment** approach (binomial MLE).  
   - **Vasicek PDF** approach (likelihood from the continuous Vasicek density).

We will end up with (i) the *simulated* default‐rate time series, and (ii) the *estimated* parameters that best fit that series under each approach. This way, you see a concrete, reproducible workflow.

> **Note**  
> - We use a large notional portfolio each year (10,000 obligors) to get realistic default rates.  
> - All code is self‐contained; just copy‐paste into a Python script or notebook.  
> - In practice, you would replace the “simulation” step with your *actual* 10 years of observed default rates; the rest of the pipeline remains the same.

---

# 1) Set Up and Simulate “Real” Data

```python
import numpy as np
import pandas as pd
from scipy.stats import norm, binom

# Fix random seed for reproducibility
np.random.seed(12345)

# Parameters for "true" portfolio
N = 10000  # number of obligors each year
T = 10     # number of years
p_true = 0.02  # true unconditional PD
rho_true = 0.15  # true asset correlation

# Convert PD -> threshold k (in a standard normal sense)
k_true = norm.ppf(p_true)  # e.g. ~ -2.0537 for 2%

# We simulate each year's portfolio defaults under a 1-factor model:
#   R_{t,i} = sqrt(rho)*Z_t + sqrt(1-rho)*E_{t,i}
#   Default if R_{t,i} < k
# Here Z_t ~ N(0,1) (systematic), E_{t,i} ~ N(0,1) (idiosyncratic).
# Then we compute default rate = (# of defaults) / N for each year.

default_rates = []
for t in range(T):
    # Draw systematic factor
    Z_t = np.random.normal(0,1)
    
    # Draw idiosyncratic factors for each obligor
    E_t = np.random.normal(0,1,size=N)
    
    # Asset returns
    R_t = np.sqrt(rho_true)*Z_t + np.sqrt(1-rho_true)*E_t
    
    # Count how many are below threshold k
    num_defaults = np.sum(R_t < k_true)
    
    # Default rate
    dr_t = num_defaults / N
    default_rates.append(dr_t)

default_rates = np.array(default_rates)

print("Simulated (Observed) Annual Default Rates:")
for i,dr in enumerate(default_rates, start=1):
    print(f"  Year {i}: {dr*100:.2f}%")
```

At this point, `default_rates` is our “realistic” historical series of 10 annual default rates. You can imagine these as your actual observed portfolio default rates over 10 years.

---

# 2) Indirect Moment Approach

This uses the closed‐form relationships between the sample mean and stdev of the *inverse‐normal*‐transformed default rates, and \((k,\rho)\).  

\[
\mu_{\text{inv}} = \frac{k}{\sqrt{1-\rho}}, 
\quad
\sigma_{\text{inv}} = \frac{\sqrt{\rho}}{\sqrt{1-\rho}}.
\]

Solving these gives:

\[
\rho \;=\; \frac{\sigma_{\text{inv}}^2}{1 + \sigma_{\text{inv}}^2}, 
\quad
k \;=\; \mu_{\text{inv}}\;\sqrt{1-\rho}.
\]

```python
from scipy.stats import norm

# 1) Invert the observed default rates via the standard normal quantile
pd_inverted = norm.ppf(default_rates)

# 2) Compute sample mean and sample std (unbiased) of these inverted PDs
mu_inv = np.mean(pd_inverted)
sd_inv = np.std(pd_inverted, ddof=1)

# 3) Solve for rho
sd_inv_sq = sd_inv**2
rho_indirect = sd_inv_sq / (1 + sd_inv_sq)

# 4) Solve for k
k_indirect = mu_inv * np.sqrt(1 - rho_indirect)

print("\n--- Indirect Moment Approach ---")
print(f"Estimated correlation (rho): {rho_indirect:.4f}")
print(f"Estimated threshold (k):     {k_indirect:.4f}")

# If you want an implied "long-run PD" from that threshold:
p_indirect = norm.cdf(k_indirect)
print(f"Implied long-run PD:        {p_indirect:.4%}")
```

---

# 3) Direct Moment (Binomial MLE) Approach

Here, we treat each year’s number of defaults out of N as a binomial random variable \( \text{Binomial}(N, p_t) \). Under the 1‐factor model, all obligors share the same systematic factor but have correlation \(\rho\). Strictly, that leads to a more complicated distribution of total defaults. However, a common approximation is to assume that each year has an *effective* PD that depends on the realized systematic factor, with average PD = \(p\) and correlation \(\rho\).

A more precise route is to write the probability of observing \(d_t\) defaults (out of \(N\)) given \((p,\rho)\) by integrating out the systematic factor. That integral has a closed‐form known as the “Vasicek binomial distribution.” We can then form the log‐likelihood across all \(T\) years and maximize w.r.t. \(p\) and \(\rho\).

Below is a standard approach (sometimes called “Vasicek binomial MLE”):

\[
P(\text{Defaults} = d)
=
\int_{-\infty}^{+\infty}
  \binom{N}{d}
  [\Phi(\alpha(z))]^d\,[1 - \Phi(\alpha(z))]^{N-d}
  \,\frac{1}{\sqrt{2\pi}} e^{-\frac{z^2}{2}} \,dz,
\]
where 
\[
\alpha(z) 
= 
\frac{\Phi^{-1}(p) - \sqrt{\rho}\,z}{\sqrt{1-\rho}}.
\]

We will numerically approximate this integral (e.g.\ via Gaussian quadrature or a simpler approach). For 10 data points, we can afford some numerical integration.

### Code

```python
import numpy as np
from scipy.optimize import minimize
from scipy.special import comb, loggamma
from math import log, sqrt, exp

# We have T=10 years, each year observed "d_t" = # of defaults, and "N" = # of obligors.
# Let's define a function that, given p,rho, returns the negative log-likelihood
# across all T years of observed defaults.

# 1) Extract counts for each year from the default rate * N
defaults_per_year = (default_rates * N).astype(int)

def vasicek_binomial_logpmf(d, N, p, rho, num_points=20):
    """
    Log of the probability mass function for the number of defaults 'd'
    out of N, under the Vasicek single-factor model with
    unconditional PD = p, correlation = rho.

    We approximate via a numeric integration over the standard normal distribution of Z.
    """
    # binomial coefficient part (constant for a given d,N)
    # We'll do it in log form to avoid underflow:
    log_binom_coeff = ( loggamma(N+1)
                        - loggamma(d+1)
                        - loggamma(N-d+1) )

    k_ = norm.ppf(p)  # threshold for unconditional PD

    # We build a set of points z_i for integration (Gauss-Hermite or simpler)
    # For demonstration, let's do a simple equally-spaced approach on e.g. [-4,+4].
    # For real production, you might do better quadrature.
    z_grid = np.linspace(-4,4,num_points)
    w = (z_grid[1]-z_grid[0])  # spacing

    # We'll accumulate the integral in log-space carefully. 
    # We do fZ(z) * Binomial(...) integrated over z, 
    # where fZ(z) = standard normal pdf
    # and Binomial(...) uses p_cond = Phi( (k - sqrt(rho)*z) / sqrt(1-rho) ).

    log_probs = []
    for z in z_grid:
        # standard normal pdf at z
        pdf_z = (1.0/np.sqrt(2*np.pi)) * np.exp(-0.5*z**2)

        # conditional PD = Phi( alpha(z) )
        alpha_z = (k_ - np.sqrt(rho)*z)/np.sqrt(1-rho)
        p_cond = norm.cdf(alpha_z)

        # log [ p_cond^d * (1-p_cond)^(N-d) ]
        # = d*log(p_cond) + (N-d)*log(1-p_cond)
        if p_cond<=0 or p_cond>=1:
            # extreme cases => log(...) might blow up
            lp = -999999999
        else:
            lp = d*np.log(p_cond) + (N-d)*np.log(1-p_cond)

        # total log (including binomial coefficient), ignoring integral weighting for now
        # => log_binom_coeff + lp
        # then we multiply by pdf_z for the integration
        # => exp( log_binom_coeff + lp ) * pdf_z
        # We'll keep in linear space for integration, but do it carefully:
        val = np.exp(log_binom_coeff + lp)*pdf_z
        log_probs.append(val)

    # numeric approximation of integral
    pmf_approx = np.sum(log_probs)*w
    if pmf_approx<=0:
        return -999999999
    return np.log(pmf_approx)

def vasicek_binomial_nll(params):
    # we'll optimize over p in (0,1) and rho in (0,1)
    p, rho = params
    if p<=0 or p>=1 or rho<=0 or rho>=1:
        return 1e12  # invalid => penalize

    total_loglike = 0.0
    for d in defaults_per_year:
        lp = vasicek_binomial_logpmf(d, N, p, rho)
        total_loglike += lp
    return -total_loglike  # negative log-likelihood

# Now we run the minimization
res = minimize(vasicek_binomial_nll, x0=[0.01, 0.20],
               bounds=[(1e-5,0.9999),(1e-5,0.9999)],
               method='L-BFGS-B')

print("\n--- Direct Moment (Vasicek Binomial MLE) Approach ---")
if res.success:
    p_hat, rho_hat = res.x
    print(f"Estimated PD p:            {p_hat:.5f}")
    print(f"Estimated correlation rho: {rho_hat:.5f}")
else:
    print("Optimization failed:", res.message)
```

This is a “real” direct MLE approach using the *binomial* distribution each year under the *Vasicek* factor model. We used a simple numeric integration for each year’s likelihood. You can refine it with more integration points or better quadrature for production use.

---

# 4) Vasicek (Continuous) PDF Approach

Some practitioners model the *default rate* itself (rather than the count of defaults) as drawn from the Vasicek (continuous) distribution for the fraction. If you have a large portfolio, that is often a good approximation. Then you form:

\[
f(\text{DR}_t \mid p, \rho)
\]
 
directly from the closed‐form Vasicek “distribution of default rates.” The negative log‐likelihood is:

\[
-\sum_{t=1}^T \ln f(\text{DR}_t \mid p, \rho).
\]

Below is a more direct approach for the fraction (rather than the count). We’ll use the standard formula:

\[
f(x) 
= 
\frac{\sqrt{1-\rho}}{\sqrt{\rho}\;\phi(\Phi^{-1}(x))}
\exp\!\bigl(
  -\frac{1}{2\rho}
  \bigl[\Phi^{-1}(x)-\sqrt{\rho}\,\Phi^{-1}(p)\bigr]^2
  + \frac{1}{2}\,[\Phi^{-1}(x)]^2
\bigr)
\]

where \(\phi\) is the standard normal pdf, \(\Phi\) is the CDF.  (There are various equivalent ways to write it.)

### Code

```python
def vasicek_fraction_pdf(x, p, rho):
    """
    Continuous Vasicek PDF for the default fraction x in [0,1],
    with unconditional PD = p, correlation = rho.
    Reference formula can be found in many credit risk texts.
    """
    if x <= 0 or x >= 1 or p <= 0 or p >= 1 or rho <= 0 or rho >= 1:
        return 1e-30  # near 0 or invalid

    z_x = norm.ppf(x)
    z_p = norm.ppf(p)

    # standard normal pdf for z_x
    phi_zx = (1.0/np.sqrt(2*np.pi))*np.exp(-0.5*z_x**2)

    # We'll implement the known formula for f(x). One version is:
    # f(x) = 
    #   sqrt( (1-rho)/rho ) * 
    #   exp( (1/(2*rho)) * [ 2*sqrt(rho)*z_p*z_x - z_p^2 - z_x^2 ] )
    # all divided by phi(z_x).
    # We'll do it carefully in log form.

    # log version
    term1 = 0.5*np.log((1-rho)/rho)
    term2 = (1/(2*rho))*(2*np.sqrt(rho)*z_p*z_x - z_p**2 - z_x**2)
    # subtract the log of phi(z_x):
    term3 = - np.log(phi_zx)

    log_f = term1 + term2 + term3
    val = np.exp(log_f)
    if val < 1e-30:
        return 1e-30
    return val

def vasicek_fraction_nll(params):
    p, rho = params
    # penalize out-of-bounds
    if p<=0 or p>=1 or rho<=0 or rho>=1:
        return 1e12
    
    # sum of -log( f( default_rate_t | p, rho ) )
    nll = 0.0
    for x in default_rates:
        pdf_val = vasicek_fraction_pdf(x, p, rho)
        nll -= np.log(pdf_val)
    return nll

res2 = minimize(vasicek_fraction_nll, x0=[0.01, 0.20],
                bounds=[(1e-5,0.9999),(1e-5,0.9999)], method='L-BFGS-B')

print("\n--- Vasicek (Continuous Fraction) PDF Approach ---")
if res2.success:
    p_hat2, rho_hat2 = res2.x
    print(f"Estimated PD p:            {p_hat2:.5f}")
    print(f"Estimated correlation rho: {rho_hat2:.5f}")
else:
    print("Optimization failed:", res2.message)
```

This assumes your default rates \( \text{DR}_t \) come from the continuous Vasicek distribution. With large \(N\), that’s a reasonable approximation.  

---

## Comparison of Results

At the end, you will have something like:

- “True” parameters:  
  \[
    p_{\text{true}} = 0.02,\quad \rho_{\text{true}} = 0.15.
  \]
- Indirect moment approach:  
  \[
    \rho_{\text{indirect}},\quad k_{\text{indirect}} \Rightarrow p_{\text{indirect}} = \Phi(k_{\text{indirect}}).
  \]
- Direct binomial MLE approach:  
  \[
    p_{\text{MLE}},\; \rho_{\text{MLE}}.
  \]
- Continuous fraction (Vasicek PDF) approach:  
  \[
    p_{\text{frac}},\; \rho_{\text{frac}}.
  \]

All of these should be *somewhat close* to \((0.02,\,0.15)\) if the simulation is not too pathological. Because we only have 10 years of data, there is sampling noise. If you re‐run with bigger \(T\), the estimates will converge more tightly around the true parameters.

---

# Final Notes

1. **In Real Life**  
   - You do **not** do the simulation step; you already have 10 historical default rates (one per year). Just replace `default_rates` with your actual historical data.  
   - The rest of the code remains the same: you calibrate \(\rho\) (and PD or \(k\)) to those observed data points.  

2. **Computational Complexity**  
   - The *indirect moment* approach is *instantaneous* (just closed‐form).  
   - The *binomial MLE* or *continuous PDF* approach involves numerical optimization (and possibly numerical integration). For 10 data points, this is still quite fast.  

3. **Extensions**  
   - You can incorporate *macroeconomic regressions* by modeling how \(p\) or the systematic factor evolves with macro variables.  
   - You can “forecast” PDs by forecasting the factor \(Z\).  

4. **Choice of Approach**  
   - The “best” approach depends on your portfolio size, internal modeling frameworks, IFRS9 requirements, etc. The binomial MLE is quite standard if you want to properly account for discrete default counts. The continuous fraction PDF is a good approximation for large portfolios. The indirect moment approach is extremely common in practice for a quick correlation estimate.  

All three yield *portfolio‐level PD and correlation estimates* from *just a time series of default rates*, no transition matrices needed.
