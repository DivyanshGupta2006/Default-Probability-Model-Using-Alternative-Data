import pandas as pd
import random as rd
import random
import numpy as np
from faker import Faker
import os


fake = Faker()
Faker.seed(42)
np.random.seed(42)
rd.seed(42)
# Define tiers and cities
tier_cities = {
    "Tier 1": ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai"],
    "Tier 2": ["Jaipur", "Pune", "Lucknow", "Ahmedabad", "Indore"],
    "Tier 3": ["Ranchi", "Patna", "Bhopal", "Kanpur", "Guwahati"]
}

# Smart card types
smart_card_types = [
    "Metro Smart Card",
    "Bus/Train Travel Card",
    "Shopping Card",
    "Fuel Card",
    "Wallet-linked Smart Card"
]

# Output directory
output_dir = "d:/Vids/python/boi hackathon/data"
os.makedirs(output_dir, exist_ok=True)

# Generate data
data = []
person_id = 1

for tier, cities in tier_cities.items():
    num_people = 3333 if tier != "Tier 3" else 3334  # total 10,000
    for _ in range(num_people):
        city = random.choice(cities)
        name = fake.name()

        # Tier-wise smart card ownership logic
        if tier == "Tier 1":
            num_cards = random.randint(2, 4)
        elif tier == "Tier 2":
            num_cards = random.randint(1, 3)
        else:
            num_cards = random.randint(0, 2)

        owned_cards = random.sample(smart_card_types, k=num_cards)

        for card in owned_cards:
            data.append({
                "PersonID": person_id,
                "Name": name,
                "City": city,
                "Tier": tier,
                "Smart Card Type": card
            })

        person_id += 1

# Save to DataFrame
df = pd.DataFrame(data)

# Save CSV
csv_path = os.path.join(output_dir, "smart_card_ownership.csv")
df.to_csv(csv_path, index=False)

# Save Excel
xlsx_path = os.path.join(output_dir, "smart_card_ownership.xlsx")
df.to_excel(xlsx_path, index=False)

print(f"Files saved:\n- {csv_path}\n- {xlsx_path}")
