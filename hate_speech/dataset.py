import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path

# Configuration
DATA_DIR = Path("data")  # Assumes your csv is in a folder named 'data'
INPUT_FILE = DATA_DIR / "final_data.csv"
TRAIN_FILE = DATA_DIR / "train.csv"
VAL_FILE = DATA_DIR / "val.csv"
TEST_FILE = DATA_DIR / "test.csv"

# Split Ratios
TEST_SIZE = 0.1
VAL_SIZE = 0.1
RANDOM_STATE = 42

def split_and_save_data():
    # 1. Load the data
    if not INPUT_FILE.exists():
        print(f"Error: File not found at {INPUT_FILE}")
        return

    print(f"Loading data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)

    # Check if 'label' column exists for stratification
    # (Stratification ensures each split has the same proportion of classes)
    stratify_col = df['label'] if 'label' in df.columns else None

    # 2. First Split: Separate Train from the rest (Val + Test)
    # The size of 'temp' needs to be (val_size + test_size)
    total_val_test_size = VAL_SIZE + TEST_SIZE
    
    train_df, temp_df = train_test_split(
        df, 
        test_size=total_val_test_size, 
        random_state=RANDOM_STATE, 
        stratify=stratify_col
    )

    # 3. Second Split: Separate Validation and Test from the 'temp' data
    # We need to recalculate the ratio relative to the temp dataframe
    relative_test_size = TEST_SIZE / total_val_test_size

    # Re-define stratify for the temp set
    stratify_col_temp = temp_df['label'] if 'label' in temp_df.columns else None

    val_df, test_df = train_test_split(
        temp_df, 
        test_size=relative_test_size, 
        random_state=RANDOM_STATE, 
        stratify=stratify_col_temp
    )

    # 4. Save the files
    print("Saving files...")
    train_df.to_csv(TRAIN_FILE, index=False)
    val_df.to_csv(VAL_FILE, index=False)
    test_df.to_csv(TEST_FILE, index=False)

    # 5. Print Summary
    print("-" * 30)
    print(f"Total samples: {len(df)}")
    print(f"Train set:     {len(train_df)} ({len(train_df)/len(df):.0%}) -> saved to {TRAIN_FILE}")
    print(f"Val set:       {len(val_df)} ({len(val_df)/len(df):.0%}) -> saved to {VAL_FILE}")
    print(f"Test set:      {len(test_df)} ({len(test_df)/len(df):.0%}) -> saved to {TEST_FILE}")
    print("-" * 30)

if __name__ == "__main__":
    print("running")
    split_and_save_data()