import streamlit as st
import numpy as np
import datetime
import pandas as pd
from datetime import date
import holidays
import plotly.express as px
from io import BytesIO


st.title ("PR Item to VS Item")

# Upload CSV file using Streamlit's sidebar
Tugas_2 = st.sidebar.file_uploader('Upload a CSV file', type=['csv'])

# Check if a file has been uploaded
if Tugas_2 is not None:
    Tugas_2 = pd.read_csv(Tugas_2)
    
    Tugas_2['Approval Date (PR)'] = pd.to_datetime(Tugas_2['Approval Date (PR)'])
    Tugas_2['VS Created Date'] = pd.to_datetime(Tugas_2['VS Created Date'])
    Tugas_2 = Tugas_2[Tugas_2["PR Status"] == "Approved"]
    selected_columns = ['Request ID', 'Title', 'Asset Type', 'Request Date', 'PR Item Description', 'PR Line Created Date', 'PR Status', 'Approval Date (PR)', 'VS ID Name','VS Title', 'VS Created By', 'VS Created Date','VSA Number','VS Approved By', 'VS Approval Date', 'VS Status']
    Tugas_2 = Tugas_2[selected_columns]

    # Function to count Saturdays in the date range
    def count_saturdays(date_start, date_end):
        count = 0
        current_date = date_start
        while current_date <= date_end:
            if current_date.weekday() == 5:  # Saturday is represented by 5 in Python's datetime.weekday() function
                count += 1
            current_date += pd.Timedelta(days=1)  # Move to the next day
        return count

    # Function to count Sundays in the date range
    def count_sundays(date_start, date_end):
        count = 0
        current_date = date_start
        while current_date <= date_end:
            if current_date.weekday() == 6:  # Sunday is represented by 6 in Python's datetime.weekday() function
                count += 1
            current_date += pd.Timedelta(days=1)  # Move to the next day
        return count

    # Calculate the difference between 'VS Date Created' and 'PR Date Approve' in days
    Tugas_2['Range (days)'] = (Tugas_2['VS Created Date'] - Tugas_2['Approval Date (PR)']).dt.days

    # Calculate the number of Saturdays for each row in the DataFrame
    Tugas_2['Number of Saturdays'] = Tugas_2.apply(lambda row: count_saturdays(row['Approval Date (PR)'], row['VS Created Date']), axis=1)

    # Calculate the number of Sundays for each row in the DataFrame
    Tugas_2['Number of Sundays'] = Tugas_2.apply(lambda row: count_sundays(row['Approval Date (PR)'], row['VS Created Date']), axis=1)

    # Create a list of Indonesian holidays
    indonesia_holidays = holidays.Indonesia(years=date.today().year)

    # Function to count Indonesian holidays in the date range (excluding weekends)
    def count_holidays(start_date, end_date):
        count = 0
        current_date = start_date
        while current_date <= end_date:
            # Check if the current date is a holiday and not a weekend (Saturday or Sunday)
            if current_date in indonesia_holidays and current_date.weekday() not in [5, 6]:
                count += 1
            current_date += pd.Timedelta(days=1)  # Move to the next day
        return count

    # Calculate the difference between 'VS Date Created' and 'PR Date Approve' in days
    Tugas_2['Range (days)'] = (Tugas_2['VS Created Date'] - Tugas_2['Approval Date (PR)']).dt.days

    # Calculate the number of Indonesian holidays (excluding weekends) for each row in the DataFrame
    Tugas_2['Number of Indonesian Holidays'] = Tugas_2.apply(lambda row: count_holidays(row['Approval Date (PR)'], row['VS Created Date']), axis=1)

    # Calculate the total work days for each row in the DataFrame
    Tugas_2['Total Work Days'] = Tugas_2['Range (days)'] - (Tugas_2['Number of Saturdays'] + Tugas_2['Number of Sundays'] + Tugas_2['Number of Indonesian Holidays'])

    # Create a function to apply the grouping logic
    def apply_grouping(total_work_days):
        if pd.isnull(total_work_days):
            return "Overdue"
        elif total_work_days == 0:
            return "Same Day"
        elif total_work_days == 1:
            return 'N+1'
        elif total_work_days == 2:
            return 'N+2'
        elif total_work_days == 3:
            return 'N+3'
        elif total_work_days == 4:
            return 'N+4'
        elif total_work_days == 5:
            return 'N+5'
        elif total_work_days == 6:
            return 'N+6'
        elif total_work_days == 7:
            return 'N+7'
        else:
            return 'N++'

    # Apply the grouping function to the 'Total Work Days' column
    Tugas_2['Network Days'] = Tugas_2['Total Work Days'].apply(apply_grouping)

    #kolom bulan
    Tugas_2['Month'] = Tugas_2["VS Created Date"].apply(lambda x : x.month)
    # Fungsi untuk mengubah angka bulan menjadi nama bulan
    def angka_ke_nama_bulan(angka):
        nama_bulan = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December'
        }
        return nama_bulan.get(angka, np.nan)

    Tugas_2['Month'] = Tugas_2['Month'].map(angka_ke_nama_bulan)

    PR_Item_Received = Tugas_2['Approval Date (PR)'].count()
    PR_Item_to_VS_Created = Tugas_2['VS Created Date'].count()
    Overdue = Tugas_2['VS Created Date'].isna().sum()

    # Create individual DataFrames for each value
    PR_Item_Received_df = pd.DataFrame({'PR Item Received': [PR_Item_Received]})
    PR_Item_to_VS_Created_df = pd.DataFrame({'PR Item to VS Created': [PR_Item_to_VS_Created]})
    Overdue_df = pd.DataFrame({'Overdue': [Overdue]})

    # Concatenate the DataFrames vertically
    Measurable_objective = pd.concat([PR_Item_Received_df, PR_Item_to_VS_Created_df, Overdue_df], axis=1)

    Month = ['April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December','January', 'February', 'March']
    January = Tugas_2[Tugas_2['Month'] == 'January']
    February = Tugas_2[Tugas_2['Month'] == 'February']
    March = Tugas_2[Tugas_2['Month'] == 'March']
    April = Tugas_2[Tugas_2['Month'] == 'April']
    May = Tugas_2[Tugas_2['Month'] == 'May']
    June = Tugas_2[Tugas_2['Month'] == 'June']
    July = Tugas_2[Tugas_2['Month'] == 'July']
    August = Tugas_2[Tugas_2['Month'] == 'August']
    September = Tugas_2[Tugas_2['Month'] == 'September']
    October = Tugas_2[Tugas_2['Month'] == 'October']
    November = Tugas_2[Tugas_2['Month'] == 'November']
    December = Tugas_2[Tugas_2['Month'] == 'December']

    def calculate_metrics(input_dataframe):
        if input_dataframe.empty:
            return None

        PR_Item_Received = Tugas_2['Approval Date (PR)'].count()
        PR_Item_to_VS_Created = Tugas_2['VS Created Date'].count()
        Overdue = Tugas_2['VS Created Date'].isna().sum()

        # Create individual DataFrames for each value
        PR_Item_Received_df = pd.DataFrame({'PR Item Received': [PR_Item_Received]})
        PR_Item_to_VS_Created_df = pd.DataFrame({'PR Item to VS Created': [PR_Item_to_VS_Created]})
        Overdue_df = pd.DataFrame({'Overdue': [Overdue]})

        # Concatenate the DataFrames vertically
        Measurable_objective = pd.concat([PR_Item_Received_df, PR_Item_to_VS_Created_df, Overdue_df], axis=1)

        # Group by 'VS Created By' and 'Network Days', and then calculate the counts
        grouped = input_dataframe.groupby(['VS Created By', 'Network Days']).size().reset_index(name='Count')

        # Pivot the table based on 'VS Created By' and 'Network Days'
        pivot_table = grouped.pivot_table(index='VS Created By', columns='Network Days', values='Count', fill_value=0)

        # Calculate the total of 'Grouped Work Days' for each 'VS Created By'
        pivot_table['Total'] = pivot_table.sum(axis=1)

        columns_to_sum = ['Same Day', 'N+1', 'N+2', 'N+3', 'N+4', 'N+5', 'N+6', 'N+7']

        # Initialize the sum column with zeros
        pivot_table['Sum Same Day - N+7'] = 0

        # Iterate through the columns and calculate the sum
        for col in columns_to_sum:
            if col in pivot_table.columns:
                pivot_table['Sum Same Day - N+7'] += pivot_table[col]

        # Fill NaN values with 0 after performing the pivot operation
        pivot_table = pivot_table.fillna(0)

        # Calculate the total of 'Grouped Work Days' for each 'n+1', 'n+2', 'n+3', etc.
        totals = pivot_table.sum(numeric_only=True, axis=0)
        totals.name = 'Total'
        pivot_table = pd.concat([pivot_table, totals.to_frame().T], axis=0)

        values_to_add = ['Sum Same Day - N+7', 'Total']

        # Remove 'Overdue' from the unique Network Days values
        network_days_unique = input_dataframe['Network Days'].unique()
        network_days_filtered = [value for value in network_days_unique if value != 'Overdue']

        # Combine the filtered unique Network Days values with the values to add
        new_network_days = np.append(network_days_filtered, values_to_add)

        # Filter the pivot_table DataFrame columns based on new_network_days
        pivot_table = pivot_table[new_network_days]

        # Counting percentage for each network days
        pivot_table_Transpose = pivot_table.T

        def format_percentage(x):
            if pd.notna(x):
                return f'{x:.2f}%'
            return ''

        pivot_table_Transpose["Percentage"] = (pivot_table_Transpose['Total'] / PR_Item_Received) * 100
        pivot_table_Transpose['Percentage'] = pivot_table_Transpose['Percentage'].apply(format_percentage)
        pivot_table = pivot_table_Transpose.T

        columns_to_sort = ['Same Day', 'N+1', 'N+2', 'N+3', 'N+4', 'N+5', 'N+6', 'N+7', 'Sum Same Day - N+7', 'Total']

        # Mengambil hanya kolom-kolom yang ada dalam DataFrame
        existing_columns = [col for col in columns_to_sort if col in pivot_table.columns]

        # Mengurutkan DataFrame berdasarkan kolom yang ada
        pivot_table = pivot_table[existing_columns]

        return pivot_table

    cum_sum = pd.DataFrame()

    for month in [April, May, June, July, August, September, October, November, December, January, February, March]:
        temp_df = calculate_metrics(month)  # You need to define this function
        if temp_df is not None:
            temp = float(temp_df['Total'].iloc[-1].split('%')[0])
            temp_series = pd.Series([temp])
            cum_sum = pd.concat([cum_sum, temp_series], ignore_index=True)
        else:
            temp_series = pd.Series([0])
            cum_sum = pd.concat([cum_sum, temp_series], ignore_index=True)
            
    # Concatenate DataFrames side by side
    result = pd.concat([pd.DataFrame(Month), cum_sum.cumsum()], axis=1)

    result.columns = ['Month','Achievement']
    result.set_index('Month')
    result['Target'] = 93
    percentage_result = result
    percentage_result['Achievement'] = percentage_result['Achievement'].apply(lambda x: f'{x:.2f}%')
    percentage_result['Target'] = percentage_result['Target'].apply(lambda x: f'{x:.0f}%')

    # Create a line chart using Plotly Express
    fig = px.line(result, x='Month', y=['Achievement', 'Target'], title='Achievement vs Target')
    fig.update_traces(
        line=dict(width=2),  # Line width
        mode='lines+markers',  # Show lines and markers
        marker=dict(size=8),  # Marker size
        hovertemplate='%{y}',  # Customize hover text
        line_shape='linear',  # Use linear line shapeF
    )

    all_month = calculate_metrics(Tugas_2)
    st.subheader("PR Item to VS Created")
    st.dataframe(Measurable_objective)
    st.caption("Count of Network Days")
    st.dataframe(all_month)
    st.caption("Achievement vs Target")
    st.dataframe(percentage_result)
    st.plotly_chart(fig)
    
    if st.button("Export to Excel"):
        excel_filename = "Result.xlsx"
        with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
            Measurable_objective.to_excel(writer, sheet_name="Sheet_1", startcol=2, startrow=3, header=True, index=False) # Default position: cell A1.
            all_month.to_excel(writer, sheet_name="Sheet_1", startcol=8, startrow=3, header=True, index=True) 
            percentage_result.to_excel(writer, sheet_name="Sheet_1", startcol=2, startrow=6, header=True, index=False)
            # Mengubah file Excel menjadi bytes
        byte_io = BytesIO()
        with open(excel_filename, "rb") as file:
            byte_io.write(file.read())
        byte_io.seek(0)
        st.download_button(label="Download Excel", data=byte_io, file_name=excel_filename)
    
    select_month = st.multiselect('Select Month:', Tugas_2['Month'].unique())
    if select_month:
        selected_data = Tugas_2[Tugas_2['Month'].isin(select_month)]
        if not selected_data.empty:
            # Display metrics for the selected months
            st.dataframe(calculate_metrics(selected_data))
        else:
            st.write("No data available for the selected months.")
    else:
        st.write("")  
    
    
    if st.button("Export to Excel with Selected Data"):
        excel_filename = "Result.xlsx"
        with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
            Measurable_objective.to_excel(writer, sheet_name="Sheet_1", startcol=2, startrow=3, header=True, index=False) # Default position: cell A1.
            all_month.to_excel(writer, sheet_name="Sheet_1", startcol=8, startrow=3, header=True, index=True) 
            percentage_result.to_excel(writer, sheet_name="Sheet_1", startcol=2, startrow=6, header=True, index=False)
            (calculate_metrics(selected_data)).to_excel(writer, sheet_name="Sheet_1", startcol=2, startrow=35, header=True, index=True)
            # Mengubah file Excel menjadi bytes
        byte_io = BytesIO()
        with open(excel_filename, "rb") as file:
            byte_io.write(file.read())
        byte_io.seek(0)
        st.download_button(label="Download Excel", data=byte_io, file_name=excel_filename)
else:
    st.warning("Please upload a CSV file to get started.")

st.write(
    '<div style="position: fixed; bottom: 10px; right: 10px;">'
    '© 2023 Irwanda B. Matematika ITS.'
    '</div>',
    unsafe_allow_html=True
)
