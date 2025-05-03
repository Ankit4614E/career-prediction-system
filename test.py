import pandas as pd
import numpy as np

# Load your original dataset
df = pd.read_csv("finalized_dataset.csv")

# Flip target labels for 10% of the rows (label noise)
target_col = df.columns[-1]  # assuming last column is the target
n_flip = int(0.1 * len(df))  # 10% of rows
flip_indices = np.random.choice(df.index, size=n_flip, replace=False)

# Unique classes
classes = df[target_col].unique()

# Flip labels to a different class
for idx in flip_indices:
    current_label = df.at[idx, target_col]
    new_label = np.random.choice([c for c in classes if c != current_label])
    df.at[idx, target_col] = new_label

# Save updated dataset
df.to_csv("noisy_dataset_with_flipped_labels.csv", index=False)
print("Noise added by flipping 10% of the labels.")
