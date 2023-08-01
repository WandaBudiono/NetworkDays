import pandas as pd
from datetime import date
import holidays
import streamlit as st

# Function to read the uploaded CSV file and return a DataFrame
def read_csv_file(uploaded_file):
    return pd.read_csv(uploaded_file)

# Add a file uploader widget to the app
st.sidebar.header('Upload CSV File')
uploaded_file = st.sidebar.file_uploader('Choose a CSV file', type=['csv'])

# Check if a file has been uploaded
if uploaded_file is not None:
    # Read the uploaded CSV file into a DataFrame
    Tugas_2 = read_csv_file(uploaded_file)

    # Your existing code here
    Tugas_2['PR Date Create'] = pd.to_datetime(Tugas_2['PR Date Create'])
    Tugas_2['PR Date Approve'] = pd.to_datetime(Tugas_2['PR Date Approve'])
    Tugas_2['VS Date Created'] = pd.to_datetime(Tugas_2['VS Date Created'])

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
    Tugas_2['Range (days)'] = (Tugas_2['VS Date Created'] - Tugas_2['PR Date Approve']).dt.days

    # Calculate the number of Saturdays for each row in the DataFrame
    Tugas_2['Number of Saturdays'] = Tugas_2.apply(lambda row: count_saturdays(row['PR Date Approve'], row['VS Date Created']), axis=1)

    # Calculate the number of Sundays for each row in the DataFrame
    Tugas_2['Number of Sundays'] = Tugas_2.apply(lambda row: count_sundays(row['PR Date Approve'], row['VS Date Created']), axis=1)

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
    Tugas_2['Range (days)'] = (Tugas_2['VS Date Created'] - Tugas_2['PR Date Approve']).dt.days

    # Calculate the number of Indonesian holidays (excluding weekends) for each row in the DataFrame
    Tugas_2['Number of Indonesian Holidays'] = Tugas_2.apply(lambda row: count_holidays(row['PR Date Approve'], row['VS Date Created']), axis=1)

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

    # Group by 'VS Created By' and 'Grouped Work Days', and then calculate the counts
    grouped = Tugas_2.groupby(['VS Created By', 'Network Days']).size().reset_index(name='Count')

    # Pivot the table based on 'VS Created By' and 'Grouped Work Days'
    pivot_table = grouped.pivot_table(index='VS Created By', columns='Network Days', values='Count', fill_value=0)

    # Calculate the total of 'Grouped Work Days' for each 'VS Created By'
    pivot_table['Total'] = pivot_table.sum(axis=1)

    pivot_table['Sum Same Day - N+7']= pivot_table['Same Day']+pivot_table['N+1']+pivot_table['N+2']+pivot_table['N+3']+pivot_table['N+4']+pivot_table['N+5']+pivot_table['N+6']+pivot_table['N+7']

    # Calculate the total of 'Grouped Work Days' for each 'n+1', 'n+2', 'n+3', etc.
    totals = pivot_table.sum()
    totals.name = 'Total'
    pivot_table = pivot_table.append(totals)
    pivot_table = pivot_table[['Same Day','N+1','N+2','N+3','N+4','N+5','N+6','N+7','N++','Sum Same Day - N+7','Total']]

    # calculate the values
    PR_Item_Received = Tugas_2['PR Date Approve'].count()
    PR_Item_to_VS_Created = Tugas_2['VS Date Created'].count()
    Overdue = Tugas_2['VS Date Created'].isna().sum()

    # Create individual DataFrames for each value
    PR_Item_Received = pd.DataFrame({'PR Item Received': [PR_Item_Received]})
    PR_Item_to_VS_Created = pd.DataFrame({'PR Item to VS Created': [PR_Item_to_VS_Created]})
    Overdue = pd.DataFrame({'Overdue': [Overdue]})
    # Concatenate the DataFrames vertically
    Measurable_objective = pd.concat([PR_Item_Received, PR_Item_to_VS_Created, Overdue], axis=1)

    # Display the pivot table
    st.write(pivot_table)
    st.dataframe(pivot_table)

    # Display the measurable objectives
    st.write(Measurable_objective)
    st.dataframe(Measurable_objective)
else:
    # If no file is uploaded, show a message
    st.warning('Please upload a CSV file.')

