# Demo Scripts

This folder contains demonstration scripts for Bills Tracker v3 features.

## Purpose

Demo scripts showcase specific features and help users understand how to use the application effectively.

## Files

- `demo_confirmation_number.py` - Demonstrates payment confirmation number feature
- `demo_date_selector.py` - Shows advanced date selection capabilities
- `demo_advanced_filtering.py` - Demonstrates filtering and search features

## Usage

To run a demo script:

```bash
cd demo
python demo_confirmation_number.py
python demo_date_selector.py
python demo_advanced_filtering.py
```

## Demo Categories

### Feature Demos
- Show specific functionality in action
- Provide step-by-step examples
- Demonstrate best practices

### Integration Demos
- Show how features work together
- Demonstrate complete workflows
- Test feature combinations

### Educational Demos
- Explain complex concepts
- Show real-world usage scenarios
- Provide learning examples

## Creating New Demos

When adding new features, create corresponding demo scripts:

1. Create a demo file with descriptive name (e.g., `demo_feature_name.py`)
2. Include clear setup and explanation
3. Show both basic and advanced usage
4. Provide helpful output and feedback
5. Update this README with new demo details

## Demo Best Practices

- Keep demos focused on one feature
- Include clear explanations and comments
- Use realistic sample data
- Provide helpful output messages
- Make demos runnable independently

## Available Demos

### 1. Next Month Filter Demo
**File:** `demo_next_month_filter.py`

Tests the new "Next Month" period filter functionality.

**Features:**
- Creates test bills with various due dates (this month, last month, next month)
- Tests the filtering logic for next month bills
- Demonstrates how the UI filter works

**Usage:**
```bash
cd Bills_tracker_v3
python demo/demo_next_month_filter.py
```

**What it does:**
1. Creates test bills with different due dates
2. Tests the next month filtering logic
3. Shows all bills in the database
4. Provides instructions for testing the UI filter

## Running the Demos

1. Make sure you're in the `Bills_tracker_v3` directory
2. Ensure the database exists (run the main app first if needed)
3. Run any demo script with: `python demo/[script_name].py`

## Testing the UI Features

After running the demo scripts, you can test the UI features:

1. Start the main application: `python run.py`
2. Navigate to the Bills view
3. Use the Period dropdown to select different time periods:
   - All
   - This Month
   - Last Month
   - Previous Month
   - **Next Month** (new feature)
   - This Year
   - Last Year

## Notes

- Demo scripts will create test data in your database
- You can delete test bills through the UI if needed
- The "Next Month" filter correctly handles year transitions (December → January) 