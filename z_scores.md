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
