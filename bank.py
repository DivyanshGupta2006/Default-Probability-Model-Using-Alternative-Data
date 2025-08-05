import pandas as pd
import random as rd
import numpy as np
import random
from faker import Faker
import os

# Set seeds for reproducibility
fake = Faker()
Faker.seed(42)
np.random.seed(42)
rd.seed(42)

# Create 'data' directory if it doesn't exist
output_dir = "d:/Vids/python/boi hackathon/data"
os.makedirs(output_dir, exist_ok=True)

# Define tiers and their cities
tier_cities = {
    "Tier 1": ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai"],
    "Tier 2": ["Jaipur", "Pune", "Lucknow", "Ahmedabad", "Indore"],
    "Tier 3": ["Ranchi", "Patna", "Bhopal", "Kanpur", "Guwahati"]
}

# Account types
account_types = [
    "Savings Account", "Current Account", "Salary Account",
    "Recurring Deposit", "Fixed Deposit", "PPF Account", 
    "NPS Account", "Joint Account", "Minor Account"
]

data = []

person_id = 1
for tier, cities in tier_cities.items():
    for _ in range(3333 if tier != "Tier 3" else 3334):  # Total 10,000
        city = random.choice(cities)
        name = fake.name()
        is_earning_member = random.choices(["Yes", "No"], weights=[0.7, 0.3])[0]

        # Tier-based number of accounts
        if tier == "Tier 1":
            num_accounts = random.randint(2, 5)
        elif tier == "Tier 2":
            num_accounts = random.randint(1, 4)
        else:
            num_accounts = random.randint(1, 3)

        person_accounts = random.sample(account_types, k=num_accounts)

        for account in person_accounts:
            data.append({
                "PersonID": person_id,
                "Name": name,
                "City": city,
                "Tier": tier,
                "Earning Member": is_earning_member,
                "Account Type": account
            })

        person_id += 1

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
csv_path = os.path.join(output_dir, "financial_accounts_by_tier.csv")
df.to_csv(csv_path, index=False)

# Save to Excel
xlsx_path = os.path.join(output_dir, "financial_accounts_by_tier.xlsx")
df.to_excel(xlsx_path, index=False)

print(f"Files saved:\n- CSV: {csv_path}\n- Excel: {xlsx_path}")
