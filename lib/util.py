from faker import Faker
import numpy as np
import pandas as pd
import random as rd
from scipy.stats import truncnorm

n = 10000 # data-points
fake = Faker('en_IN') # Faker instance
Faker.seed(42)
np.random.seed(42)
rd.seed(42)

def fabricate_base_data(num_rows=n, id_range=(10**11, 10**12-1) ,age_stats=(36.17, 12.68, 18, 65)):
    data = []
    aadhar = rd.sample(range(id_range[0], id_range[1] + 1), num_rows)
    ages=create_truncated_norm_distribution(age_stats, precision=0)
    for _ in range(num_rows):
        aadhar_no = aadhar[_]
        age = ages[_]
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        data.append([aadhar_no, name, age, email, phone])
    df = pd.DataFrame(data, columns=['Aadhar No.', 'Name', 'Age', 'E-mail', 'Phone No.'])
    df.set_index('Aadhar No.', inplace=True)
    return df

def create_positive_norm_distribution(stats, precision=2, nan_probability=0):
    data = []
    for _ in range(n):
        datafield = np.random.normal(stats[0], stats[1])
        datafield = max(0, round(datafield, precision))
        if np.random.rand() < nan_probability:
            datafield = np.nan
        data.append(datafield)
    return data
def create_norm_distribution(stats, precision=2, nan_probability=0):
    data = []
    for _ in range(n):
        datafield = np.random.normal(stats[0], stats[1])
        datafield = round(datafield, precision)
        if np.random.rand() < nan_probability:
            datafield = np.nan
        data.append(datafield)
    return data
def create_truncated_norm_distribution(stats, precision=2, nan_probability=0):
    a = (stats[2] - stats[0]) / stats[1]
    b = (stats[3] - stats[0]) / stats[1]
    data=truncnorm(a, b, loc=stats[0], scale=stats[1]).rvs(size=n)
    data = np.round(data, precision)
    mask = np.random.rand(n) < nan_probability
    data[mask] = np.nan
    return data

from scipy.stats import truncnorm
import numpy as np

def create_correlated_norm_distribution(
        stats_list,  # list of (mean, std, min, max) for each variable
        correlation_matrix,  # correlation matrix (len(stats_list) x len(stats_list))
        n=100,
        precision=2,
        nan_probability=0
):
    num_vars = len(stats_list)
    correlation_matrix = np.array(correlation_matrix)

    # Validate matrix size
    if correlation_matrix.shape != (num_vars, num_vars):
        raise ValueError("Correlation matrix size does not match number of variables")

    # Create covariance matrix
    std_devs = np.array([s[1] for s in stats_list])
    cov_matrix = correlation_matrix * np.outer(std_devs, std_devs)

    # Generate correlated normal samples
    means = np.array([s[0] for s in stats_list])
    raw_data = np.random.multivariate_normal(means, cov_matrix, size=n)

    # Truncate values while keeping correlation
    for i, (mean, std, min_val, max_val) in enumerate(stats_list):
        raw_data[:, i] = np.clip(raw_data[:, i], min_val, max_val)

    # Round
    raw_data = np.round(raw_data, precision)

    # Inject NaNs
    if nan_probability > 0:
        mask = np.random.rand(*raw_data.shape) < nan_probability
        raw_data[mask] = np.nan

    return raw_data


