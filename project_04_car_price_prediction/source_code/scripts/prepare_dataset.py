"""
Script to generate or fetch the Car Price dataset.
This dataset replicates and expands upon the standard Kaggle CarDekho dataset
used widely in machine learning regression benchmarks.
"""

import os
import random
import numpy as np
import pandas as pd

def generate_car_dataset(num_samples: int = 400, random_seed: int = 42) -> pd.DataFrame:
    np.random.seed(random_seed)
    random.seed(random_seed)

    car_catalog = [
        {"name": "Maruti Swift", "brand": "Maruti", "base_price": 6.8, "fuel": ["Petrol", "Diesel", "CNG"], "type": "Hatchback"},
        {"name": "Maruti Dzire", "brand": "Maruti", "base_price": 7.4, "fuel": ["Petrol", "Diesel", "CNG"], "type": "Sedan"},
        {"name": "Maruti Baleno", "brand": "Maruti", "base_price": 7.9, "fuel": ["Petrol", "CNG"], "type": "Hatchback"},
        {"name": "Maruti Brezza", "brand": "Maruti", "base_price": 9.5, "fuel": ["Petrol", "CNG"], "type": "Compact SUV"},
        {"name": "Maruti Wagon R", "brand": "Maruti", "base_price": 5.8, "fuel": ["Petrol", "CNG"], "type": "Hatchback"},
        {"name": "Maruti Ciaz", "brand": "Maruti", "base_price": 10.2, "fuel": ["Petrol", "Diesel"], "type": "Sedan"},
        {"name": "Maruti Ertiga", "brand": "Maruti", "base_price": 10.5, "fuel": ["Petrol", "CNG"], "type": "MUV"},
        {"name": "Hyundai i20", "brand": "Hyundai", "base_price": 8.2, "fuel": ["Petrol", "Diesel"], "type": "Hatchback"},
        {"name": "Hyundai Grand i10", "brand": "Hyundai", "base_price": 6.2, "fuel": ["Petrol", "CNG"], "type": "Hatchback"},
        {"name": "Hyundai Verna", "brand": "Hyundai", "base_price": 12.8, "fuel": ["Petrol", "Diesel"], "type": "Sedan"},
        {"name": "Hyundai Creta", "brand": "Hyundai", "base_price": 14.5, "fuel": ["Petrol", "Diesel"], "type": "SUV"},
        {"name": "Hyundai Venue", "brand": "Hyundai", "base_price": 9.8, "fuel": ["Petrol", "Diesel"], "type": "Compact SUV"},
        {"name": "Honda City", "brand": "Honda", "base_price": 13.2, "fuel": ["Petrol", "Diesel"], "type": "Sedan"},
        {"name": "Honda Civic", "brand": "Honda", "base_price": 20.5, "fuel": ["Petrol", "Diesel"], "type": "Sedan"},
        {"name": "Honda Amaze", "brand": "Honda", "base_price": 7.8, "fuel": ["Petrol", "Diesel"], "type": "Sedan"},
        {"name": "Honda CR-V", "brand": "Honda", "base_price": 28.0, "fuel": ["Petrol", "Diesel"], "type": "SUV"},
        {"name": "Toyota Fortuner", "brand": "Toyota", "base_price": 35.5, "fuel": ["Petrol", "Diesel"], "type": "SUV"},
        {"name": "Toyota Innova Crysta", "brand": "Toyota", "base_price": 22.0, "fuel": ["Petrol", "Diesel"], "type": "MUV"},
        {"name": "Toyota Corolla Altis", "brand": "Toyota", "base_price": 17.5, "fuel": ["Petrol", "Diesel"], "type": "Sedan"},
        {"name": "Toyota Glanza", "brand": "Toyota", "base_price": 8.0, "fuel": ["Petrol", "CNG"], "type": "Hatchback"},
        {"name": "Toyota Urban Cruiser", "brand": "Toyota", "base_price": 10.2, "fuel": ["Petrol"], "type": "Compact SUV"},
        {"name": "Ford EcoSport", "brand": "Ford", "base_price": 9.8, "fuel": ["Petrol", "Diesel"], "type": "Compact SUV"},
        {"name": "Ford Endeavour", "brand": "Ford", "base_price": 33.0, "fuel": ["Diesel"], "type": "SUV"},
        {"name": "Volkswagen Polo", "brand": "Volkswagen", "base_price": 8.5, "fuel": ["Petrol", "Diesel"], "type": "Hatchback"},
        {"name": "Volkswagen Vento", "brand": "Volkswagen", "base_price": 11.2, "fuel": ["Petrol", "Diesel"], "type": "Sedan"},
        {"name": "Tata Nexon", "brand": "Tata", "base_price": 9.9, "fuel": ["Petrol", "Diesel"], "type": "Compact SUV"},
        {"name": "Tata Harrier", "brand": "Tata", "base_price": 17.5, "fuel": ["Diesel"], "type": "SUV"},
        {"name": "Mahindra XUV500", "brand": "Mahindra", "base_price": 16.0, "fuel": ["Diesel"], "type": "SUV"},
        {"name": "Mahindra Thar", "brand": "Mahindra", "base_price": 14.0, "fuel": ["Petrol", "Diesel"], "type": "SUV"},
        {"name": "BMW 3 Series", "brand": "BMW", "base_price": 45.0, "fuel": ["Petrol", "Diesel"], "type": "Luxury Sedan"},
        {"name": "Audi A4", "brand": "Audi", "base_price": 44.0, "fuel": ["Petrol", "Diesel"], "type": "Luxury Sedan"},
        {"name": "Mercedes-Benz C-Class", "brand": "Mercedes", "base_price": 50.0, "fuel": ["Petrol", "Diesel"], "type": "Luxury Sedan"}
    ]

    current_year = 2024
    rows = []

    for _ in range(num_samples):
        car = random.choice(car_catalog)
        car_name = car["name"]
        
        # Year between 2008 and 2023
        year = int(np.random.choice(
            np.arange(2008, 2024),
            p=[0.02, 0.02, 0.03, 0.04, 0.05, 0.07, 0.09, 0.11, 0.12, 0.12, 0.11, 0.09, 0.06, 0.04, 0.02, 0.01]
        ))
        age = current_year - year

        # Present price with slight inflation/trim variation
        present_price = round(car["base_price"] * np.random.uniform(0.9, 1.25), 2)

        # Kilometers driven based on age (average 8,000 - 18,000 km per year)
        avg_annual_km = np.random.uniform(7000, 16000)
        kms_driven = int(max(1000, age * avg_annual_km + np.random.normal(0, 5000)))

        # Fuel type
        fuel_type = random.choice(car["fuel"])

        # Seller type: Dealer (65%) or Individual (35%)
        seller_type = np.random.choice(["Dealer", "Individual"], p=[0.68, 0.32])

        # Transmission: Manual (72%) or Automatic (28%)
        # Luxury cars have higher automatic probability
        auto_prob = 0.85 if car["base_price"] > 25 else 0.25
        transmission = np.random.choice(["Automatic", "Manual"], p=[auto_prob, 1 - auto_prob])

        # Number of previous owners (0, 1, 2, 3)
        if age <= 2:
            owner = 0
        elif age <= 5:
            owner = np.random.choice([0, 1], p=[0.75, 0.25])
        elif age <= 9:
            owner = np.random.choice([0, 1, 2], p=[0.50, 0.40, 0.10])
        else:
            owner = np.random.choice([0, 1, 2, 3], p=[0.25, 0.45, 0.22, 0.08])

        # Price calculation modeling real vehicle depreciation:
        # 1. Base depreciation: 10% year 1, 8% each year after, bounded at ~75% max depreciation
        deprec_factor = (1 - 0.09) ** age
        deprec_factor = max(0.18, deprec_factor)

        # 2. Mileage impact: -1% per 15,000 km
        km_penalty = min(0.25, (kms_driven / 15000) * 0.012)

        # 3. Fuel impact: Diesel holds value slightly better in SUVs, CNG budget appeal
        fuel_multiplier = 1.05 if fuel_type == "Diesel" else (0.95 if fuel_type == "CNG" else 1.0)

        # 4. Transmission premium: Automatic +5%
        trans_multiplier = 1.06 if transmission == "Automatic" else 1.0

        # 5. Seller markup: Dealers ask ~6% more
        seller_multiplier = 1.06 if seller_type == "Dealer" else 0.96

        # 6. Owner penalty: -5% per prior owner
        owner_penalty = 1.0 - (owner * 0.05)

        # 7. Brand retention premium (Toyota, Honda, Maruti have higher resale retention)
        brand_retention = 1.08 if car["brand"] in ["Toyota", "Maruti", "Honda"] else 0.98

        price = present_price * deprec_factor * (1 - km_penalty) * fuel_multiplier * trans_multiplier * seller_multiplier * owner_penalty * brand_retention

        # Add realistic market noise (+/- 6%)
        noise = np.random.normal(1.0, 0.05)
        selling_price = max(0.4, round(price * noise, 2))

        rows.append({
            "Car_Name": car_name,
            "Year": year,
            "Selling_Price": selling_price,
            "Present_Price": present_price,
            "Kms_Driven": kms_driven,
            "Fuel_Type": fuel_type,
            "Seller_Type": seller_type,
            "Transmission": transmission,
            "Owner": owner
        })

    df = pd.DataFrame(rows)

    # Introduce a couple of realistic missing values to demonstrate data cleaning in pipeline
    # E.g. 3 missing Kms_Driven, 2 missing Present_Price
    df.loc[12, "Kms_Driven"] = np.nan
    df.loc[45, "Present_Price"] = np.nan
    df.loc[78, "Fuel_Type"] = np.nan

    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_car_dataset(num_samples=450, random_seed=42)
    output_path = "data/car_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Dataset generated successfully with {len(df)} records at {output_path}")
    print(df.head())
    print("\nDataset Info:")
    print(df.info())
