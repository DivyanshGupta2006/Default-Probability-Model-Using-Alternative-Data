from faker import Faker
import numpy as np
import pandas as pd
import random as rd
from scipy.stats import truncnorm, norm
from numpy.linalg import eigh

n = 10000  # data-points
fake = Faker('en_IN')  # Faker instance
Faker.seed(42)
np.random.seed(42)
rd.seed(42)


def fabricate_base_data(
        num_rows=n,
        id_range=(10 ** 11, 10 ** 12 - 1),
        age_stats=(36.17, 12.68, 18, 65),
        city_categories=('TIER-I', 'TIER-II', 'TIER-III', 'VILLAGE'),
        city_stats=(25.9, 3.1, 2.2, 68.8),
        gender_categories=('Male', 'Female', 'Other'),
        gender_stats=(51.55, 48.41, 0.04)
):
    data = []
    aadhar = rd.sample(range(id_range[0], id_range[1] + 1), num_rows)
    ages = create_truncated_norm_distribution(age_stats, precision=0)
    genders = create_categorical_distribution(gender_categories, gender_stats)
    cities = create_categorical_distribution(city_categories, city_stats)
    for _ in range(num_rows):
        aadhar_no = aadhar[_]
        age = ages[_]
        gender = genders[_]
        city = cities[_]
        name = fake.name()
        phone = fake.phone_number()
        data.append([aadhar_no, name, age, gender, city, phone])
    df = pd.DataFrame(data, columns=['Aadhar No.', 'Name', 'Age', 'Gender', 'City', 'Phone No.'])
    df.set_index('Aadhar No.', inplace=True)
    return df


def create_truncated_norm_distribution(
        stats,
        precision=2,
        nan_probability=0):
    a = (stats[2] - stats[0]) / stats[1]
    b = (stats[3] - stats[0]) / stats[1]
    data = truncnorm(a, b, loc=stats[0], scale=stats[1]).rvs(size=n)
    data = np.round(data, precision)
    mask = np.random.rand(n) < nan_probability
    data[mask] = np.nan
    return data


def create_correlated_distribution(
    stats_list,              # list of (mean, std, min, max, type)
    correlation_matrix,      # (p x p) correlation matrix in the SAME order as stats_list
    n=10000,
    precision=2,
    nan_probability=0.0,
    eps_regularize=1e-8
):
    p = len(stats_list)
    corr = np.array(correlation_matrix, dtype=float)

    # --- 0. quick checks ---
    if corr.shape != (p, p):
        raise ValueError("correlation_matrix must be shape (len(stats_list), len(stats_list))")

    # Symmetrize and force PSD (clip negative eigenvalues)
    corr = (corr + corr.T) / 2.0
    eigvals, eigvecs = eigh(corr)
    if np.any(eigvals < 0):
        eigvals[eigvals < 0] = 0.0
        corr = eigvecs @ np.diag(eigvals) @ eigvecs.T
        # rescale diagonal to 1 (numerical fix)
        d = np.sqrt(np.diag(corr))
        corr = corr / np.outer(d, d)
        np.fill_diagonal(corr, 1.0)

    # tiny regularization to ensure positive-definite for sampling
    corr = corr + np.eye(p) * eps_regularize

    # --- 1. Sample correlated standard normals (Gaussian copula) ---
    z = np.random.multivariate_normal(mean=np.zeros(p), cov=corr, size=n)  # shape (n, p)

    # --- 2. Map to uniforms using standard normal CDF ---
    u = norm.cdf(z)   # values in (0,1), shape (n,p)

    # --- 3. Transform uniforms to target marginals using inverse CDFs ---
    out = np.empty_like(u, dtype=float)
    for i, (mean, std, min_val, max_val, var_type) in enumerate(stats_list):
        if var_type == "continuous":
            # truncated normal parameters relative to standard normal
            a, b = (min_val - mean) / std, (max_val - mean) / std
            # ppf of truncnorm maps uniform -> truncated normal with desired mean/std
            out[:, i] = truncnorm.ppf(u[:, i], a=a, b=b, loc=mean, scale=std)
            out[:, i] = np.round(out[:, i], precision)

        elif var_type == "binary":
            # Interpret 'mean' as probability if in [0,1]
            if 0.0 <= mean <= 1.0:
                p_true = mean
            else:
                # fallback: convert mean/std to a probability via normal cdf (less preferred)
                p_true = norm.cdf((mean) / max(std, 1e-8))
            out[:, i] = (u[:, i] < p_true).astype(int)

        else:
            raise ValueError(f"Unknown var_type '{var_type}' for variable index {i}")

    # --- 4. Inject NaNs if requested ---
    if nan_probability and nan_probability > 0:
        mask = np.random.rand(*out.shape) < nan_probability
        out[mask] = np.nan

    return out
def create_correlated_positive_norm_distribution(
        stats,
        data,
        correlation_columns,
        correlation,
        precision=2,
        nan_probability=0
):
    data = []
    return data


def create_categorical_distribution(
        categories,
        stats,
        nan_probability=0
):
    data = []
    for _ in range(n):
        if np.random.rand() < nan_probability:
            data.append(np.nan)
        else:
            data.append(rd.choices(categories, weights=stats, k=1)[0])

    return data


def create_correlated_categorical_distribution(
        categories,
        stats,
        correlation_columns,
        correlation,
        nan_probability=0
):
    data = []
    return data