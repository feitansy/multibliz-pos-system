"""
Filter Superstore Dataset for Printing Business
================================================
This script filters the Superstore dataset to keep only items relevant
to a printing service business in the Philippines.
"""

import pandas as pd

# Load the original dataset
print("Loading Superstore dataset...")
df = pd.read_csv('training_ML/Sample - Superstore.csv', encoding='latin-1')

print(f"Original dataset: {len(df)} rows")
print("\nOriginal Categories:")
print(df['Category'].value_counts())

print("\n" + "=" * 80)
print("OFFICE SUPPLIES Sub-Categories:")
print("=" * 80)
office_df = df[df['Category'] == 'Office Supplies']
print(office_df['Sub-Category'].value_counts())

print("\n" + "=" * 80)
print("FILTERING LOGIC FOR PRINTING BUSINESS")
print("=" * 80)

# Define what's relevant to a printing service business
printing_relevant_subcategories = {
    'Paper': 'YES - Core printing supply',
    'Binders': 'YES - Document binding services',
    'Labels': 'YES - Label printing',
    'Envelopes': 'YES - Envelope printing',
    'Art': 'YES - Art supplies for design/printing',
    'Fasteners': 'YES - Document assembly',
    'Storage': 'MAYBE - Can be used for organizing printed materials',
}

print("\nRECOMMENDED FILTERING:")
for subcategory, reason in printing_relevant_subcategories.items():
    count = len(office_df[office_df['Sub-Category'] == subcategory])
    print(f"  • {subcategory:15s} ({count:4d} rows) - {reason}")

print("\nREMOVE (Not relevant to printing):")
remove_subcategories = ['Appliances', 'Supplies']
for subcategory in office_df['Sub-Category'].unique():
    if subcategory not in printing_relevant_subcategories:
        count = len(office_df[office_df['Sub-Category'] == subcategory])
        print(f"  • {subcategory:15s} ({count:4d} rows) - Not used in printing business")

print("\n" + "=" * 80)
print("APPLYING FILTER")
print("=" * 80)

# Filter to keep only relevant Office Supplies sub-categories
keep_subcategories = ['Paper', 'Binders', 'Labels', 'Envelopes', 'Art', 'Fasteners']

filtered_df = df[
    (df['Category'] == 'Office Supplies') & 
    (df['Sub-Category'].isin(keep_subcategories))
]

print(f"\nFiltered dataset: {len(filtered_df)} rows")
print(f"Reduction: {len(df) - len(filtered_df)} rows removed ({((len(df) - len(filtered_df)) / len(df) * 100):.1f}%)")

print("\nFiltered Sub-Categories:")
print(filtered_df['Sub-Category'].value_counts())

# Save the filtered dataset
output_file = 'training_ML/Filtered_Printing_Business.csv'
filtered_df.to_csv(output_file, index=False)
print(f"\n✅ Filtered dataset saved to: {output_file}")

# Show some sample products
print("\n" + "=" * 80)
print("SAMPLE PRODUCTS IN FILTERED DATASET")
print("=" * 80)
for subcategory in keep_subcategories:
    products = filtered_df[filtered_df['Sub-Category'] == subcategory]['Product Name'].unique()[:3]
    print(f"\n{subcategory}:")
    for p in products:
        print(f"  - {p}")

print("\n" + "=" * 80)
print("DATE RANGE IN FILTERED DATA")
print("=" * 80)
filtered_df['Order Date'] = pd.to_datetime(filtered_df['Order Date'])
print(f"From: {filtered_df['Order Date'].min()}")
print(f"To:   {filtered_df['Order Date'].max()}")
print(f"Total days: {(filtered_df['Order Date'].max() - filtered_df['Order Date'].min()).days}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✓ Kept 6 relevant sub-categories: {', '.join(keep_subcategories)}")
print(f"✓ Removed Furniture, Technology, and non-printing Office Supplies")
print(f"✓ Final dataset: {len(filtered_df)} transactions")
print(f"✓ Ready for ML training!")
