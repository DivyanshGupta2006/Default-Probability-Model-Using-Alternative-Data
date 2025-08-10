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
        stats_list,           # list of (mean, std, min, max, type) — type in {"continuous", "binary"}
        correlation_matrix,   # correlation matrix (len(stats_list) x len(stats_list))
        n=10000,
        precision=2,
        nan_probability=0
):
    num_vars = len(stats_list)
    correlation_matrix = np.array(correlation_matrix, dtype=float)

    # --- Step 1: Validate correlation matrix size ---
    if correlation_matrix.shape != (num_vars, num_vars):
        raise ValueError("Correlation matrix size does not match number of variables")

    # --- Step 2: Ensure positive semi-definiteness ---
    eigvals, eigvecs = eigh(correlation_matrix)
    if np.any(eigvals < 0):
        eigvals[eigvals < 0] = 0  # force non-negative eigenvalues
        correlation_matrix = (eigvecs @ np.diag(eigvals) @ eigvecs.T)

    # --- Step 3: Generate base multivariate normal ---
    std_devs = np.array([s[1] for s in stats_list])
    cov_matrix = correlation_matrix * np.outer(std_devs, std_devs)
    means = np.array([s[0] for s in stats_list])
    mvn_data = np.random.multivariate_normal(means, cov_matrix, size=n)

    # --- Step 4: Transform each column according to type ---
    for i, (mean, std, min_val, max_val, var_type) in enumerate(stats_list):

        if var_type == "continuous":
            # Convert to truncated normal
            a, b = (min_val - mean) / std, (max_val - mean) / std
            mvn_data[:, i] = truncnorm(a, b, loc=mean, scale=std).rvs(size=n)

            # Round to given precision
            mvn_data[:, i] = np.round(mvn_data[:, i], precision)

        elif var_type == "binary":
            # Map MVN variable through normal CDF -> uniform -> binary
            prob = norm.cdf((mvn_data[:, i] - mean) / std)  # convert to [0,1]
            mvn_data[:, i] = (prob > 0.5).astype(int)

        else:
            raise ValueError(f"Unknown variable type: {var_type}")

    # --- Step 5: Inject NaNs ---
    if nan_probability > 0:
        mask = np.random.rand(*mvn_data.shape) < nan_probability
        mvn_data[mask] = np.nan

    return mvn_data

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