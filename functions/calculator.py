import pandas as pd
import re

# Gets raw trasactions and determines total and split values
def splitter(data):
    # parse data from string to df
    lines = data.split('\n')

    totals = []
    for line in lines:
        nums = list(filter(None, re.split(r'(?:[^\d\.])', line)))
        all_splits = list(filter(None, re.split(r'(?: |:|,)+', line)))

        name = ' '.join(all_splits[:len(all_splits) - len(nums)])
        total = sum([float(num) for num in nums])

        totals.append((name, round(total, 2)))

    # return df of totals and links
    return pd.DataFrame(totals, columns=['Person', 'Subtotals']).set_index('Person')

def final_calc(df, fees, discounts, tax, tip, total):
    df['pct_total'] = df['Subtotals'] / round(df['Subtotals'].sum(), 2)

    df['Fees'] = fees / len(df)
    df['Discounts'] = discounts / len(df)

    df['Taxes'] = round(df['pct_total'] * tax, 2)
    df['Tip'] = round(df['pct_total'] * tip, 2)

    def total_check(x, total):
        remainder = round(total - x.sum(), 2)
        if remainder == 0:
            return x
        x.iloc[-1] = x.iloc[-1] + remainder
        return x

    # Rounding errors, am I right?
    df['Fees'] = total_check(df['Fees'], fees)
    df['Discounts'] = total_check(df['Discounts'], discounts)
    df['Taxes'] = total_check(df['Taxes'], tax)
    df['Tip'] = total_check(df['Tip'], tip)

    df['Total'] = round(df['Subtotals'] + df['Fees'] - df['Discounts'] + df['Taxes'] + df['Tip'], 2)
    # check if correct

    if round(df['Total'].sum(), 2) != total:
        return df['Total'].sum()
    return df
