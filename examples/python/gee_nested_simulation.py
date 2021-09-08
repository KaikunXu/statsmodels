#!/usr/bin/env python
# coding: utf-8

# DO NOT EDIT
# Autogenerated from the notebook gee_nested_simulation.ipynb.
# Edit the notebook and then sync the output with this file.
#
# flake8: noqa
# DO NOT EDIT

# ## GEE nested covariance structure simulation study
#
# This notebook is a simulation study that illustrates and evaluates the
# performance of the GEE nested covariance structure.
#
# A nested covariance structure is based on a nested sequence of groups,
# or "levels".  The top level in the hierarchy is defined by the `groups`
# argument to GEE.  Subsequent levels are defined by the `dep_data` argument
# to GEE.

import numpy as np
import pandas as pd
import statsmodels.api as sm

# Set the number of covariates.

p = 5

# These parameters define the population variance for each level of
# grouping.

groups_var = 1
level1_var = 2
level2_var = 3
resid_var = 4

# Set the number of groups

n_groups = 100

# Set the number of observations at each level of grouping.  Here,
# everything is balanced, i.e. within a level every group has the same size.

group_size = 20
level1_size = 10
level2_size = 5

# Calculate the total sample size.

n = n_groups * group_size * level1_size * level2_size

# Construct the design matrix.

xmat = np.random.normal(size=(n, p))

# Construct labels showing which group each observation belongs to at each
# level.

groups_ix = np.kron(np.arange(n // group_size),
                    np.ones(group_size)).astype(int)
level1_ix = np.kron(np.arange(n // level1_size),
                    np.ones(level1_size)).astype(int)
level2_ix = np.kron(np.arange(n // level2_size),
                    np.ones(level2_size)).astype(int)

# Simulate the random effects.

groups_re = np.sqrt(groups_var) * np.random.normal(size=n // group_size)
level1_re = np.sqrt(level1_var) * np.random.normal(size=n // level1_size)
level2_re = np.sqrt(level2_var) * np.random.normal(size=n // level2_size)

# Simulate the response variable.

y = groups_re[groups_ix] + level1_re[level1_ix] + level2_re[level2_ix]
y += np.sqrt(resid_var) * np.random.normal(size=n)

# Put everything into a dataframe.

df = pd.DataFrame(xmat, columns=["x%d" % j for j in range(p)])
df["y"] = y + xmat[:, 0] - xmat[:, 3]
df["groups_ix"] = groups_ix
df["level1_ix"] = level1_ix
df["level2_ix"] = level2_ix

# Fit the model.

cs = sm.cov_struct.Nested()
dep_fml = "0 + level1_ix + level2_ix"
m = sm.GEE.from_formula(
    "y ~ x0 + x1 + x2 + x3 + x4",
    cov_struct=cs,
    dep_data=dep_fml,
    groups="groups_ix",
    data=df,
)
r = m.fit()

# The estimated covariance parameters should be similar to `groups_var`,
# `level1_var`, etc. as defined above.

r.cov_struct.summary()