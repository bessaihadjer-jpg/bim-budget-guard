import pandas as pd
import numpy as np
import uuid
import random

def generate_schedule(num_rows=50, is_risky=False):
    categories = ['Walls', 'Floors', 'Structural Columns', 'Structural Framing']
    materials = ['Concrete - Cast-in-Place', 'Steel - ASTM A992', 'Timber - Softwood', 'Generic Wall', '']
    
    data = []
    for _ in range(num_rows):
        cat = random.choice(categories)
        material = random.choice(materials) if not is_risky else random.choice([materials[3], materials[4], 'Concrete - Cast-in-Place'])
        
        vol = round(random.uniform(0.5, 15.0), 2)
        if is_risky and random.random() > 0.7:
            vol = 0.0
            
        unit_cost = round(random.uniform(50, 500), 2)
        if is_risky and random.random() > 0.6:
            unit_cost = np.nan

        data.append({
            'Element_ID': str(uuid.uuid4())[:8],
            'Category': cat,
            'Family_and_Type': f"Basic {cat} - {random.randint(1, 5)}",
            'Volume_m3': vol,
            'Area_m2': round(vol * random.uniform(2, 5), 2),
            'Material': material,
            'Unit_Cost_USD': unit_cost
        })
        
    df = pd.DataFrame(data)
    filename = 'risky_schedule.csv' if is_risky else 'clean_schedule.csv'
    df.to_csv(filename, index=False)
    print(f"Generated {filename} with {num_rows} elements.")

if __name__ == "__main__":
    generate_schedule(50, is_risky=False)
    generate_schedule(50, is_risky=True)