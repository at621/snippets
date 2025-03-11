import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

def create_amortization_schedule(loans_df):
    """
    Create amortization schedules for loans with different amortization types.
    
    Parameters:
    -----------
    loans_df : pandas.DataFrame
        DataFrame containing loan information with columns:
        - amortisation_type (linear, bullet, annuity)
        - interest_rate (annual percentage)
        - starting_amount (initial loan amount)
        - start_date (when the loan begins)
        - end_date (when the loan matures)
        - balance_type (on_balance or off_balance, optional)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing the amortization schedule for each loan with columns:
        - loan_id
        - amortisation_type
        - interest_rate
        - starting_amount
        - start_date
        - end_date
        - balance_type
        - payment_date
        - principal_payment
        - interest_payment
        - total_payment
        - remaining_balance
    """
    # Initialize an empty list to store all payment schedules
    all_schedules = []
    
    # Check if balance_type column exists, if not, default to 'on_balance'
    if 'balance_type' not in loans_df.columns:
        loans_df['balance_type'] = 'on_balance'
    
    # Process each loan
    for idx, loan in loans_df.iterrows():
        loan_id = idx
        amortisation_type = loan['amortisation_type']
        interest_rate = loan['interest_rate']  # Annual interest rate as a percentage
        starting_amount = loan['starting_amount']
        start_date = pd.to_datetime(loan['start_date'])
        end_date = pd.to_datetime(loan['end_date'])
        balance_type = loan['balance_type']
        
        # Generate payment dates based on balance_type
        payment_dates = []
        
        if balance_type.lower() == 'off_balance':
            # For off-balance: only one payment exactly 1 year after start date
            payment_date = start_date + relativedelta(years=1)
            
            # If payment date exceeds end date, use end date instead
            if payment_date > end_date:
                payment_date = end_date
                
            payment_dates.append(payment_date)
        else:  # on_balance
            # Generate monthly payment dates (preserving the day of the month from start_date)
            current_date = start_date
            
            while current_date < end_date:
                next_date = current_date + relativedelta(months=1)
                
                # Make sure we don't go beyond the end date
                if next_date > end_date:
                    payment_dates.append(end_date)
                    break
                    
                payment_dates.append(next_date)
                current_date = next_date
            
            # If there are no payment dates (loan term less than a month),
            # use the end date as the only payment date
            if not payment_dates:
                payment_dates.append(end_date)
        
        # Number of payments
        num_payments = len(payment_dates)
        
        # Base loan details to include in each row
        loan_details = {
            'loan_id': loan_id,
            'amortisation_type': amortisation_type,
            'interest_rate': interest_rate,
            'starting_amount': starting_amount,
            'start_date': start_date,
            'end_date': end_date,
            'balance_type': balance_type
        }
        
        # Add the initial state (time 0)
        initial_row = loan_details.copy()
        initial_row.update({
            'payment_date': start_date,
            'principal_payment': 0,
            'interest_payment': 0,
            'total_payment': 0,
            'remaining_balance': starting_amount
        })
        all_schedules.append(initial_row)
        
        # Initialize variables
        remaining_balance = starting_amount
        previous_date = start_date
        
        # Create schedule based on amortisation type and balance type
        if balance_type.lower() == 'off_balance':
            # Off-balance only has one payment after 1 year
            payment_date = payment_dates[0]
            days_in_period = (payment_date - previous_date).days
            interest_payment = remaining_balance * (interest_rate / 100) * (days_in_period / 365)
            principal_payment = remaining_balance
            total_payment = principal_payment + interest_payment
            
            row_data = loan_details.copy()
            row_data.update({
                'payment_date': payment_date,
                'principal_payment': principal_payment,
                'interest_payment': interest_payment,
                'total_payment': total_payment,
                'remaining_balance': 0
            })
            all_schedules.append(row_data)
        
        elif amortisation_type.lower() == 'linear':
            # Linear amortization: constant principal payment
            principal_payment = starting_amount / num_payments
            
            for payment_date in payment_dates:
                # Calculate interest for this period using actual days
                days_in_period = (payment_date - previous_date).days
                interest_payment = remaining_balance * (interest_rate / 100) * (days_in_period / 365)
                total_payment = principal_payment + interest_payment
                
                # For the last payment, adjust for any rounding errors
                if payment_date == payment_dates[-1]:
                    principal_payment = remaining_balance
                    total_payment = principal_payment + interest_payment
                
                # Prepare row data
                row_data = loan_details.copy()
                row_data.update({
                    'payment_date': payment_date,
                    'principal_payment': principal_payment,
                    'interest_payment': interest_payment,
                    'total_payment': total_payment,
                    'remaining_balance': remaining_balance - principal_payment
                })
                all_schedules.append(row_data)
                
                # Update remaining balance and previous date for next iteration
                remaining_balance -= principal_payment
                previous_date = payment_date
                
        elif amortisation_type.lower() == 'bullet':
            # Bullet amortization: interest-only payments with final balloon payment
            for i, payment_date in enumerate(payment_dates):
                # Calculate interest for this period using actual days
                days_in_period = (payment_date - previous_date).days
                interest_payment = remaining_balance * (interest_rate / 100) * (days_in_period / 365)
                
                # For all payments except the last one, principal payment is 0
                if i < len(payment_dates) - 1:
                    principal_payment = 0
                    total_payment = interest_payment
                    new_balance = remaining_balance
                else:
                    # Last payment: pay off the entire remaining principal
                    principal_payment = remaining_balance
                    total_payment = principal_payment + interest_payment
                    new_balance = 0
                
                # Prepare row data
                row_data = loan_details.copy()
                row_data.update({
                    'payment_date': payment_date,
                    'principal_payment': principal_payment,
                    'interest_payment': interest_payment,
                    'total_payment': total_payment,
                    'remaining_balance': new_balance
                })
                all_schedules.append(row_data)
                
                # Update remaining balance and previous date for next iteration
                remaining_balance = new_balance
                previous_date = payment_date
        
        elif amortisation_type.lower() == 'annuity':
            # Annuity amortization: constant total payment
            
            # Calculate the periodic interest rate (monthly)
            # Use average days in month to approximate monthly rate
            monthly_rate = interest_rate / 100 / 12
            
            # Calculate fixed periodic payment using the annuity formula
            # PMT = PV * r * (1 + r)^n / ((1 + r)^n - 1)
            annuity_payment = np.nan  # Initialize to handle edge cases
            
            if monthly_rate > 0 and num_payments > 0:
                annuity_payment = starting_amount * monthly_rate * (1 + monthly_rate) ** num_payments
                annuity_payment = annuity_payment / ((1 + monthly_rate) ** num_payments - 1)
            else:
                # Fallback to simple division if interest rate is 0 or only one payment
                annuity_payment = starting_amount / num_payments
            
            for payment_date in payment_dates:
                # Calculate actual interest for this period
                days_in_period = (payment_date - previous_date).days
                interest_payment = remaining_balance * (interest_rate / 100) * (days_in_period / 365)
                
                # Calculate principal payment as the difference
                principal_payment = annuity_payment - interest_payment
                
                # Adjust for the final payment to account for rounding differences
                if payment_date == payment_dates[-1]:
                    principal_payment = remaining_balance
                    annuity_payment = principal_payment + interest_payment
                
                # Ensure principal payment doesn't exceed remaining balance
                principal_payment = min(principal_payment, remaining_balance)
                total_payment = principal_payment + interest_payment
                
                # Prepare row data
                row_data = loan_details.copy()
                row_data.update({
                    'payment_date': payment_date,
                    'principal_payment': principal_payment,
                    'interest_payment': interest_payment,
                    'total_payment': total_payment,
                    'remaining_balance': remaining_balance - principal_payment
                })
                all_schedules.append(row_data)
                
                # Update remaining balance and previous date for next iteration
                remaining_balance -= principal_payment
                previous_date = payment_date
        
        else:
            raise ValueError(f"Unsupported amortisation type: {amortisation_type}")
    
    # Create a DataFrame from all schedules
    schedule_df = pd.DataFrame(all_schedules)
    
    # Sort by loan_id and payment_date
    schedule_df = schedule_df.sort_values(['loan_id', 'payment_date']).reset_index(drop=True)
    
    # Round numerical columns to 2 decimal places for currency
    for col in ['principal_payment', 'interest_payment', 'total_payment', 'remaining_balance']:
        schedule_df[col] = schedule_df[col].round(2)
    
    return schedule_df

# Example usage
if __name__ == "__main__":
    # Sample dataset with different loan types and balance types
    loans_data = {
        'amortisation_type': ['linear', 'bullet', 'annuity', 'linear'],
        'interest_rate': [5.0, 4.5, 3.75, 4.0],  # Annual interest rates in percentage
        'starting_amount': [100000, 200000, 150000, 80000],
        'start_date': ['2023-01-15', '2023-02-01', '2023-03-10', '2023-04-01'],
        'end_date': ['2023-07-15', '2024-02-01', '2025-03-10', '2024-04-01'],
        'balance_type': ['on_balance', 'on_balance', 'on_balance', 'off_balance']
    }
    
    loans_df = pd.DataFrame(loans_data)
    schedule_df = create_amortization_schedule(loans_df)
    
    # Display results
    print("Complete Amortization Schedule:")
    print(schedule_df)
    
    # Filter for specific loan types
    linear_schedule = schedule_df[schedule_df['amortisation_type'] == 'linear']
    bullet_schedule = schedule_df[schedule_df['amortisation_type'] == 'bullet']
    annuity_schedule = schedule_df[schedule_df['amortisation_type'] == 'annuity']
    off_balance_schedule = schedule_df[schedule_df['balance_type'] == 'off_balance']
    
    print("\nLinear Loan Schedule:")
    print(linear_schedule)
    
    print("\nBullet Loan Schedule:")
    print(bullet_schedule)
    
    print("\nAnnuity Loan Schedule:")
    print(annuity_schedule)
    
    print("\nOff-Balance Schedule:")
    print(off_balance_schedule)
