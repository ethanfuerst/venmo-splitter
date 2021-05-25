import urllib.parse
import pandas as pd
import tabulate
import plotly.graph_objects as go
import streamlit as st
from functions import calculator as calc

def main():

    site_url = 'www.tidbitstatistics.com'

    st.title('Venmo Splitter')
    st.write("Enter in each persons items line by line, as well as a discount, fees, tax and tip " +
        "(if available).\n\n I'll split up the payments and give you some venmo request links!")

    st.header('What is this for?')
    desc = st.text_input('Name of restaraunt, bar, etc.')
    # if no desc just calculated with link to site
    desc = f'{desc} - calculated with {site_url}' if desc else f'Calculated with {site_url}'
    desc = urllib.parse.quote(desc)

    # Input transactions
    st.header('Input your transactions here')
    with st.beta_expander(label='Accepted Formats'):
        st.write('''
            On each line, provide the name of the person and each associated cost separated by a number of spaces,
            with a ':' or a ',' if you'd like.
            ```
            Michael 8.99  10.99   5.99
            Mitchell:    14.50    13.50
            Cole 12.99,   1.09
            Ethan: 1.99 3.50
            ```'''
        )

    data = st.text_area('Input the items here', height=180)

    totals = calc.splitter(data)

    st.markdown(totals.to_markdown())

    subtotal = totals['Subtotals'].sum()

    st.write(f'Subtotal: {subtotal}')

    # Discount, Fees, Tax, Tip
    st.header('Any discounts, fees, tip or tax?')
    col1, col2 = st.beta_columns(2)

    discounts = col1.number_input('Discounts (subtracted equally)', step=1.0, min_value=0.0)
    fees = col2.number_input('Fees (added equally)', step=1.0, min_value=0.0)
    tax = col1.number_input('Tax (distributed relative to subtotal)', step=1.0, min_value=0.0)
    tip = col2.number_input('Tip (distributed relative to subtotal)', step=1.0, min_value=0.0)

    st.header('Give me the total so I know I did my math correctly!')
    # Input Total (optional?)
    total = st.number_input('Put the total here')

    final_df = calc.final_calc(
        totals,
        discounts=discounts,
        fees=fees,
        tax=tax,
        tip=tip,
        total=total
    )

    format_radio_1 = lambda x: 'Request' if x == 'charge' else 'Pay'
    format_radio_2 = lambda x: 'Private' if x == 'private' else \
        ('Just friends' if x == 'friends' else 'Public')

    venmo_type = st.radio(
        "Do you want links to request or send money?",
        ['charge', 'pay'],
        format_func=format_radio_1
    )
    audience = st.radio(
        "Who do you want to see the request?",
        ['private', 'friends', 'public'],
        format_func=format_radio_2
    )

    # Press Button
    if st.button('Calculate my totals!'):
        # if items don't match the total, show a message showing the difference
        if not isinstance(final_df, pd.core.frame.DataFrame):
            st.write(f'Whoops! Your inputted total was {"${:,.2f}".format(total)}, ' +
                f'but I calculated your total as {"${:,.2f}".format(final_df)}.')
            st.write("Double check all your inputs " +
                "(or if you don't care just change the total to what I calculated)")
        else:
            st.header('Here are your totals, complete with links to charge your friends on venmo!')

            final_df['URL'] = "https://venmo.com/?txn=" + venmo_type + "&amp;audience=" + \
                audience + "&amp;amount=" + final_df['Total'].astype(str) + "&amp;note=" + desc

            final_df['Link'] = '[Link](' + final_df['URL'] + ')'

            final_df = final_df.reset_index().copy()

            final_df['Subtotals'] = final_df['Subtotals'].apply('${:,.2f}'.format)
            final_df['Fees'] = final_df['Fees'].apply('${:,.2f}'.format)
            final_df['Discounts'] = final_df['Discounts'].apply('${:,.2f}'.format)
            final_df['Taxes'] = final_df['Taxes'].apply('${:,.2f}'.format)
            final_df['Tip'] = final_df['Tip'].apply('${:,.2f}'.format)
            final_df['Total NF'] = final_df['Total']
            final_df['Total'] = final_df['Total'].apply('${:,.2f}'.format)

            disp_col = ['Person', 'Subtotals', 'Fees', 'Discounts', 'Taxes', 'Tip', 'Total', 'Link']
            st.markdown(final_df[disp_col].to_markdown(index=False))

            if tip > 0:
                bef_tax_tip = (tip/subtotal) * 100
                tip_str = f'Your tip was {bef_tax_tip:.2f}%'

                if tax > 0:
                    aft_tax_tip = (tip/(subtotal + tax)) * 100
                    tip_str = tip_str + f' before tax and {aft_tax_tip:.2f}% after tax'

                st.write(tip_str)

            if tax > 0:
                tax_pct = (tax/subtotal) * 100
                st.write(f'The tax rate was {tax_pct:.2f}%')

            if discounts > 0:
                discount_pct = (discounts/subtotal) * 100
                st.write(f'You saved {discount_pct:.2f}% with your discount')

            if fees > 0:
                fee_pct = (fees/subtotal) * 100
                st.write(f'Your fees added an extra {fee_pct:.2f}% to your subtotal')

            # Pie chart
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=final_df['Person'],
                        values=final_df['Total NF'],
                        text=final_df['Total'],
                        hovertemplate='%{label}: <br>%{text}<br>%{percent}<extra></extra>'
                    )
                ]
            )

            st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()
