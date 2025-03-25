import os
import json
import time
import base64
import io
from datetime import datetime
from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
import openai
import pandas as pd

# Settings
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Function to evaluate accuracy of responses
def evaluate_response_accuracy(results):
    """
    Evaluate the accuracy of model responses compared to correct answers.
    Returns a DataFrame with accuracy scores.
    """
    data = []
    
    for test_name, test_results in results.items():
        test_data = TEST_CASES[test_name]
        
        table_correct = 0
        chart_correct = 0
        total_questions = len(test_data["questions"])
        
        for i, question in enumerate(test_data["questions"]):
            # Get correct answer and LLM responses
            correct_answer = test_data["correct_answers"][i].lower()
            table_response = test_results["table_responses"][i].lower()
            chart_response = test_results["chart_responses"][i].lower()
            
            # Check if specific numerical values are present in the responses
            # This is a simple check - you might want more sophisticated evaluation
            if any(key_part in correct_answer for key_part in ["subjective", "looking for"]):
                # Skip subjective questions for accuracy calculation
                total_questions -= 1
                continue
                
            # For factual questions, check if the key part of answer is in response
            # Extract the numeric/factual part of the correct answer
            key_facts = []
            
            # Look for dollar amounts
            if "$" in correct_answer:
                import re
                dollar_amounts = re.findall(r'\$[\d,]+(?:\.\d+)?', correct_answer)
                key_facts.extend(dollar_amounts)
            
            # Look for percentages
            if "%" in correct_answer:
                import re
                percentages = re.findall(r'(?<!\w)(?:\d+(?:\.\d+)?%|(?:\d+(?:\.\d+)?)(?:\s+)?percent(?:age)?)', correct_answer)
                key_facts.extend(percentages)
                
            # Look for specific statements like country names
            for statement in ["usa", "china", "north", "east", "june", "stock c", "month", "age group"]:
                if statement in correct_answer:
                    key_facts.append(statement)
            
            # If we found specific facts to check
            if key_facts:
                table_match = all(fact.lower() in table_response for fact in key_facts)
                chart_match = all(fact.lower() in chart_response for fact in key_facts)
                
                if table_match:
                    table_correct += 1
                if chart_match:
                    chart_correct += 1
            else:
                # Fallback to a simple check if the first 10 chars of the answer appear
                if correct_answer[:10] in table_response:
                    table_correct += 1
                if correct_answer[:10] in chart_response:
                    chart_correct += 1
        
        # Calculate accuracy if there are non-subjective questions
        if total_questions > 0:
            table_accuracy = (table_correct / total_questions) * 100
            chart_accuracy = (chart_correct / total_questions) * 100
        else:
            table_accuracy = "N/A (subjective only)"
            chart_accuracy = "N/A (subjective only)"
        
        data.append({
            "test_case": test_name,
            "total_factual_questions": total_questions,
            "table_correct": table_correct,
            "chart_correct": chart_correct,
            "table_accuracy": table_accuracy,
            "chart_accuracy": chart_accuracy
        })
    
    return pd.DataFrame(data)# Function to evaluate accuracy of responses
def evaluate_response_accuracy(results):
    """
    Evaluate the accuracy of model responses compared to correct answers.
    Returns a DataFrame with accuracy scores.
    """
    data = []
    
    for test_name, test_results in results.items():
        test_data = TEST_CASES[test_name]
        
        table_correct = 0
        chart_correct = 0
        total_questions = len(test_data["questions"])
        
        for i, question in enumerate(test_data["questions"]):
            # Get correct answer and LLM responses
            correct_answer = test_data["correct_answers"][i].lower()
            table_response = test_results["table_responses"][i].lower()
            chart_response = test_results["chart_responses"][i].lower()
            
            # Check if specific numerical values are present in the responses
            # This is a simple check - you might want more sophisticated evaluation
            if any(key_part in correct_answer for key_part in ["subjective", "looking for"]):
                # Skip subjective questions for accuracy calculation
                total_questions -= 1
                continue
                
            # For factual questions, check if the key part of answer is in response
            # Extract the numeric/factual part of the correct answer
            key_facts = []
            
            # Look for dollar amounts
            if "$" in correct_answer:
                import re
                dollar_amounts = re.findall(r'\$[\d,]+(?:\.\d+)?', correct_answer)
                key_facts.extend(dollar_amounts)
            
            # Look for percentages
            if "%" in correct_answer:
                import re
                percentages = re.findall(r'(?<!\w)(?:\d+(?:\.\d+)?%|(?:\d+(?:\.\d+)?)(?:\s+)?percent(?:age)?)', correct_answer)
                key_facts.extend(percentages)
                
            # Look for specific statements like country names
            for statement in ["usa", "china", "north", "east", "june", "stock c", "month", "age group"]:
                if statement in correct_answer:
                    key_facts.append(statement)
            
            # If we found specific facts to check
            if key_facts:
                table_match = all(fact.lower() in table_response for fact in key_facts)
                chart_match = all(fact.lower() in chart_response for fact in key_facts)
                
                if table_match:
                    table_correct += 1
                if chart_match:
                    chart_correct += 1
            else:
                # Fallback to a simple check if the first 10 chars of the answer appear
                if correct_answer[:10] in table_response:
                    table_correct += 1
                if correct_answer[:10] in chart_response:
                    chart_correct += 1
        
        # Calculate accuracy if there are non-subjective questions
        if total_questions > 0:
            table_accuracy = (table_correct / total_questions) * 100
            chart_accuracy = (chart_correct / total_questions) * 100
        else:
            table_accuracy = "N/A (subjective only)"
            chart_accuracy = "N/A (subjective only)"
        
        data.append({
            "test_case": test_name,
            "total_factual_questions": total_questions,
            "table_correct": table_correct,
            "chart_correct": chart_correct,
            "table_accuracy": table_accuracy,
            "chart_accuracy": chart_accuracy
        })
    
    return pd.DataFrame(data)# Create pandas DataFrame with metrics for analysis
def create_metrics_dataframe(results):
    data = []
    
    for test_name, test_results in results.items():
        token_diff = ((test_results["tokens_chart"] - test_results["tokens_table"]) / test_results["tokens_table"]) * 100 if test_results["tokens_table"] > 0 else 0
        time_diff = ((test_results["time_chart"] - test_results["time_table"]) / test_results["time_table"]) * 100 if test_results["time_table"] > 0 else 0
        
        data.append({
            "test_case": test_name,
            "table_tokens": test_results["tokens_table"],
            "chart_tokens": test_results["tokens_chart"],
            "token_diff_pct": token_diff,
            "table_time": test_results["time_table"],
            "chart_time": test_results["time_chart"],
            "time_diff_pct": time_diff
        })
    
    return pd.DataFrame(data)
    

# Define test cases
TEST_CASES = {
    "monthly_revenue": {
        "table": """
| Month    | Revenue ($) | Expenses ($) | Profit ($) |
|----------|-------------|--------------|------------|
| January  | 120,000     | 85,000       | 35,000     |
| February | 135,000     | 95,000       | 40,000     |
| March    | 150,000     | 100,000      | 50,000     |
| April    | 140,000     | 105,000      | 35,000     |
| May      | 160,000     | 110,000      | 50,000     |
| June     | 180,000     | 115,000      | 65,000     |
""",
        "questions": [
            "What was the revenue in March?",
            "What was the average monthly profit over the first quarter (Jan-Mar)?",
            "In which month was the gap between revenue and expenses the largest?",
            "Describe the overall trend in revenue from January to June.",
            "What business insights can you derive from this financial data?"
        ],
        "correct_answers": [
            "$150,000",
            "$41,667 (calculated as (35,000 + 40,000 + 50,000) / 3)",
            "June (the gap was $65,000)",
            "Overall upward trend with a slight dip in April",
            "Subjective - looking for analysis of revenue growth, profit margin trends, etc."
        ]
    },
    "regional_sales": {
        "table": """
| Region    | Sales ($M) | Growth (%) | Market Share (%) | Customer Satisfaction |
|-----------|------------|------------|------------------|------------------------|
| North     | 5.2        | 12         | 28               | 4.2                    |
| South     | 3.8        | 7          | 21               | 3.8                    |
| East      | 4.5        | 15         | 24               | 4.5                    |
| West      | 5.0        | 9          | 27               | 4.0                    |
""",
        "questions": [
            "Which region has the highest sales?",
            "How much larger is the market share of North compared to South?",
            "Is there a relationship between customer satisfaction and sales growth?",
            "Rank the regions from best to worst based on overall performance.",
            "If you were the marketing director, which region would you focus more resources on and why?"
        ],
        "correct_answers": [
            "North ($5.2M)",
            "7 percentage points (28% - 21%)",
            "Yes, regions with higher customer satisfaction tend to have higher growth rates (East has highest of both, South lowest of both)",
            "Subjective - depends on weighting criteria, but East performs well in growth and satisfaction",
            "Subjective - looking for strategic reasoning"
        ]
    },
    "product_matrix": {
        "table": """
| Product | Units Sold | Price ($) | Profit Margin (%) | Customer Rating | Reorder Rate (%) |
|---------|------------|-----------|-------------------|-----------------|------------------|
| A       | 2,450      | 39.99     | 45                | 4.7             | 68               |
| B       | 1,850      | 59.99     | 55                | 4.2             | 45               |
| C       | 3,200      | 24.99     | 35                | 4.5             | 72               |
| D       | 1,100      | 89.99     | 60                | 3.9             | 38               |
| E       | 1,600      | 44.99     | 50                | 4.1             | 52               |
""",
        "questions": [
            "What is the profit margin of Product C?",
            "What is the total revenue generated by Product A?",
            "Which product has the best combination of profit margin and reorder rate?",
            "Is there a correlation between price and customer rating?",
            "Which product would you consider discontinuing and why?"
        ],
        "correct_answers": [
            "35%",
            "$97,975.50 (calculated as 2,450 × $39.99)",
            "Product A (high profit margin at 45% and high reorder rate at 68%)",
            "No clear correlation. Product A has highest rating and mid-range price. Product D has highest price but lowest rating.",
            "Subjective - likely Product D due to low units sold, low reorder rate, and low customer rating despite high price and margin"
        ]
    },
    "age_income": {
        "table": """
| Age Group | Average Income ($) | Population (%) | Spending ($) | Savings Rate (%) |
|-----------|---------------------|----------------|--------------|------------------|
| 18-24     | 32,000              | 12             | 28,800       | 10               |
| 25-34     | 48,000              | 18             | 41,000       | 15               |
| 35-44     | 65,000              | 20             | 52,000       | 20               |
| 45-54     | 75,000              | 17             | 56,000       | 25               |
| 55-64     | 72,000              | 15             | 48,000       | 33               |
| 65+       | 42,000              | 18             | 32,000       | 24               |
""",
        "questions": [
            "What is the average income of the 35-44 age group?",
            "What percentage of the population earns $65,000 or more on average?",
            "What is the weighted average income across all age groups?",
            "Describe the relationship between age and savings rate.",
            "Based on this data, which age group would be the most valuable target market for luxury goods?"
        ],
        "correct_answers": [
            "$65,000",
            "52% (age groups 35-44, 45-54, and 55-64, which is 20% + 17% + 15%)",
            "$55,640 (calculated by weighting each income by population percentage)",
            "Savings rate generally increases with age until 55-64, then slightly decreases for 65+",
            "Subjective - likely 45-54 or 55-64 due to high income and high savings rate"
        ]
    },
    "stock_performance": {
        "table": """
| Date       | Stock A | Stock B | Stock C | Market Index |
|------------|---------|---------|---------|--------------|
| 2023-01-04 | 185.24  | 94.50   | 45.30   | 4,700.58     |
| 2023-02-01 | 191.05  | 90.22   | 47.85   | 4,752.75     |
| 2023-03-01 | 202.37  | 87.15   | 50.66   | 4,801.92     |
| 2023-04-05 | 198.44  | 95.30   | 49.40   | 4,785.65     |
| 2023-05-03 | 184.92  | 98.55   | 52.10   | 4,825.30     |
| 2023-06-07 | 193.25  | 101.45  | 54.75   | 4,910.45     |
""",
        "questions": [
            "What was the value of Stock B on March 1st, 2023?",
            "What was the percentage change in Stock A from January to June?",
            "Which stock outperformed the market index over the 6-month period?",
            "Which stock showed the most price volatility?",
            "Based on the 6-month trend, which stock would you recommend for a conservative investor and why?"
        ],
        "correct_answers": [
            "$87.15",
            "4.32% (calculated as (193.25 - 185.24) / 185.24 × 100)",
            "Stock C with 20.86% growth vs. market index growth of 4.47%",
            "Stock A (shows largest swings in price relative to its value)",
            "Subjective - likely Stock C due to consistent upward trend with relatively low volatility"
        ]
    },
    "geographic_sales": {
        "table": """
| Country   | Sales ($M) | Market Share (%) | Growth Rate (%) | Profit Margin (%) |
|-----------|------------|------------------|-----------------|-------------------|
| USA       | 245.3      | 35               | 7.2             | 18.5              |
| China     | 189.7      | 27               | 15.3            | 14.2              |
| Germany   | 87.4       | 12               | 4.5             | 19.8              |
| Japan     | 76.8       | 11               | 2.1             | 17.3              |
| Brazil    | 52.6       | 8                | 9.8             | 12.4              |
| India     | 48.2       | 7                | 22.5            | 10.8              |
""",
        "questions": [
            "Which country has the highest sales?",
            "What percentage of global market share comes from Asian countries?",
            "If current growth rates continue, which country will show the largest absolute increase in sales next year?",
            "Is there a relationship between profit margin and growth rate across countries?",
            "Which two countries should be prioritized for expansion, and why?"
        ],
        "correct_answers": [
            "USA ($245.3M)",
            "45% (China 27% + Japan 11% + India 7%)",
            "USA ($17.66M increase, calculated as $245.3M × 7.2%)",
            "Inverse relationship - countries with higher growth rates tend to have lower profit margins",
            "Subjective - likely China (high sales, high growth) and India (highest growth rate)"
        ]
    }
}

# Helper function to parse table data from markdown tables
def parse_markdown_table(markdown_table):
    """Parse a markdown table into a list of dictionaries."""
    lines = [line.strip() for line in markdown_table.strip().split('\n') if line.strip()]
    headers = [h.strip() for h in lines[0].strip('|').split('|')]
    data = []
    
    for line in lines[2:]:  # Skip header and separator lines
        if '|' not in line:
            continue
        values = [val.strip() for val in line.strip('|').split('|')]
        row = {headers[i]: values[i] for i in range(len(headers))}
        data.append(row)
    
    return data, headers

# Chart creation functions that use the TEST_CASES data
def create_monthly_revenue_chart():
    # Parse the table from TEST_CASES
    table_data, _ = parse_markdown_table(TEST_CASES["monthly_revenue"]["table"])
    
    # Extract data
    months = [row['Month'] for row in table_data]
    revenue = [int(row['Revenue ($)'].replace(',', '')) for row in table_data]
    expenses = [int(row['Expenses ($)'].replace(',', '')) for row in table_data]
    profit = [int(row['Profit ($)'].replace(',', '')) for row in table_data]
    
    x = np.arange(len(months))
    width = 0.25
    
    plt.bar(x - width, revenue, width, label='Revenue ($)')
    plt.bar(x, expenses, width, label='Expenses ($)')
    plt.bar(x + width, profit, width, label='Profit ($)')
    
    plt.xlabel('Month')
    plt.ylabel('Amount ($)')
    plt.title('Monthly Revenue, Expenses, and Profit (Jan-Jun 2023)')
    plt.xticks(x, months, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate(revenue):
        plt.text(i - width, v + 5000, f"{v/1000:.0f}k", ha='center')
    
    for i, v in enumerate(expenses):
        plt.text(i, v + 5000, f"{v/1000:.0f}k", ha='center')
    
    for i, v in enumerate(profit):
        plt.text(i + width, v + 5000, f"{v/1000:.0f}k", ha='center')

def create_regional_sales_chart():
    # Parse the table from TEST_CASES
    table_data, _ = parse_markdown_table(TEST_CASES["regional_sales"]["table"])
    
    # Extract data
    regions = [row['Region'] for row in table_data]
    sales = [float(row['Sales ($M)']) for row in table_data]
    growth = [float(row['Growth (%)']) for row in table_data]
    market_share = [float(row['Market Share (%)']) for row in table_data]
    satisfaction = [float(row['Customer Satisfaction']) for row in table_data]
    
    x = np.arange(len(regions))
    width = 0.2
    
    plt.bar(x - 1.5*width, sales, width, label='Sales ($M)')
    plt.bar(x - 0.5*width, growth, width, label='Growth (%)')
    plt.bar(x + 0.5*width, market_share, width, label='Market Share (%)')
    plt.bar(x + 1.5*width, satisfaction, width, label='Customer Satisfaction')
    
    plt.xlabel('Region')
    plt.ylabel('Value')
    plt.title('Regional Sales Performance')
    plt.xticks(x, regions)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(sales):
        plt.text(i - 1.5*width, v + 0.1, f"{v}", ha='center')
    
    for i, v in enumerate(growth):
        plt.text(i - 0.5*width, v + 0.5, f"{v}%", ha='center')
    
    for i, v in enumerate(market_share):
        plt.text(i + 0.5*width, v + 1, f"{v}%", ha='center')
    
    for i, v in enumerate(satisfaction):
        plt.text(i + 1.5*width, v + 0.1, f"{v}", ha='center')

def create_product_matrix_chart():
    # Parse the table from TEST_CASES
    table_data, _ = parse_markdown_table(TEST_CASES["product_matrix"]["table"])
    
    # Extract data
    products = [row['Product'] for row in table_data]
    units_sold = [int(row['Units Sold'].replace(',', '')) for row in table_data]
    price = [float(row['Price ($)']) for row in table_data]
    profit_margin = [float(row['Profit Margin (%)']) for row in table_data]
    customer_rating = [float(row['Customer Rating']) for row in table_data]
    reorder_rate = [float(row['Reorder Rate (%)']) for row in table_data]
    
    # Create a radar chart
    categories = ['Units Sold', 'Price', 'Profit Margin', 'Customer Rating', 'Reorder Rate']
    N = len(categories)
    
    # Create angle for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop
    
    # Normalize data for radar chart
    def normalize(data):
        return [(x - min(data)) / (max(data) - min(data)) for x in data]
    
    units_norm = normalize(units_sold)
    price_norm = normalize(price)
    margin_norm = normalize(profit_margin)
    rating_norm = normalize(customer_rating)
    reorder_norm = normalize(reorder_rate)
    
    # Set up plot
    ax = plt.subplot(111, polar=True)
    
    # Draw one axis per variable and add labels
    plt.xticks(angles[:-1], categories)
    
    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([0.25, 0.5, 0.75], ["25%", "50%", "75%"], color="grey", size=8)
    plt.ylim(0, 1)
    
    # Plot data
    colors = ['b', 'g', 'r', 'c', 'm']
    for i, product in enumerate(products):
        values = [units_norm[i], price_norm[i], margin_norm[i], rating_norm[i], reorder_norm[i]]
        values += values[:1]  # Close the loop
        
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=f"Product {product}", color=colors[i])
        ax.fill(angles, values, alpha=0.1, color=colors[i])
    
    plt.legend(loc='upper right')
    plt.title('Product Performance Matrix')
    
    # Add text with actual values
    plt.figtext(0.5, 0.01, "Note: Chart shows normalized values. See product data table for actual values.", ha='center', fontsize=8)

def create_age_income_chart():
    # Parse the table from TEST_CASES
    table_data, _ = parse_markdown_table(TEST_CASES["age_income"]["table"])
    
    # Extract data
    age_groups = [row['Age Group'] for row in table_data]
    income = [int(row['Average Income ($)'].replace(',', '')) for row in table_data]
    population = [float(row['Population (%)']) for row in table_data]
    savings_rate = [float(row['Savings Rate (%)']) for row in table_data]
    
    # Create a colormap
    colors = plt.cm.viridis(np.array(population) / max(population))
    
    # Plot
    for i in range(len(age_groups)):
        plt.scatter(age_groups[i], income[i], s=savings_rate[i]*20, c=[colors[i]], alpha=0.7)
    
    plt.xlabel('Age Group')
    plt.ylabel('Average Income ($)')
    plt.title('Age-Income Distribution with Savings Rate and Population %')
    plt.grid(True, alpha=0.3)
    
    # Add annotations
    for i, age in enumerate(age_groups):
        plt.annotate(f"Income: ${income[i]:,}\nPop: {population[i]}%\nSaving: {savings_rate[i]}%", 
                    (age, income[i]), xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # Add legend for bubble size
    plt.figtext(0.5, 0.01, "Note: Bubble size represents savings rate percentage\nColor intensity represents population percentage", 
               ha='center', fontsize=8)

def create_stock_performance_chart():
    # Parse the table from TEST_CASES
    table_data, _ = parse_markdown_table(TEST_CASES["stock_performance"]["table"])
    
    # Extract data
    dates = [row['Date'].split('-')[-1] for row in table_data]  # Just use day part for display
    stock_a = [float(row['Stock A']) for row in table_data]
    stock_b = [float(row['Stock B']) for row in table_data]
    stock_c = [float(row['Stock C']) for row in table_data]
    market_index = [float(row['Market Index'].replace(',', '')) for row in table_data]
    
    # Normalize index to match scale of stocks for better visual comparison
    index_norm = [(x / market_index[0]) * 100 for x in market_index]
    stock_a_norm = [(x / stock_a[0]) * 100 for x in stock_a]
    stock_b_norm = [(x / stock_b[0]) * 100 for x in stock_b]
    stock_c_norm = [(x / stock_c[0]) * 100 for x in stock_c]
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, stock_a_norm, 'b-', label='Stock A', marker='o')
    plt.plot(dates, stock_b_norm, 'g-', label='Stock B', marker='s')
    plt.plot(dates, stock_c_norm, 'r-', label='Stock C', marker='^')
    plt.plot(dates, index_norm, 'k--', label='Market Index', marker='x')
    
    plt.xlabel('Date')
    plt.ylabel('Normalized Value (Jan 4 = 100)')
    plt.title('Stock Performance Over 6-Month Period')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add annotations for absolute values
    for i, date in enumerate(dates):
        if i % 2 == 0:  # Add values for clarity but avoid overcrowding
            plt.annotate(f"${stock_a[i]}", (date, stock_a_norm[i]), xytext=(0, 7),
                        textcoords='offset points', fontsize=8, color='blue')
            plt.annotate(f"${stock_b[i]}", (date, stock_b_norm[i]), xytext=(0, -15),
                        textcoords='offset points', fontsize=8, color='green')
            plt.annotate(f"${stock_c[i]}", (date, stock_c_norm[i]), xytext=(0, 7),
                        textcoords='offset points', fontsize=8, color='red')

def create_geographic_sales_chart():
    # Parse the table from TEST_CASES
    table_data, _ = parse_markdown_table(TEST_CASES["geographic_sales"]["table"])
    
    # Extract data
    countries = [row['Country'] for row in table_data]
    sales = [float(row['Sales ($M)']) for row in table_data]
    growth = [float(row['Growth Rate (%)']) for row in table_data]
    
    # Sort by sales
    sorted_indices = np.argsort(sales)[::-1]
    countries = [countries[i] for i in sorted_indices]
    sales = [sales[i] for i in sorted_indices]
    growth = [growth[i] for i in sorted_indices]
    
    # Create color map based on growth rate
    colors = plt.cm.RdYlGn(np.array(growth) / max(growth))
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(countries, sales, color=colors)
    
    plt.xlabel('Sales ($M)')
    plt.ylabel('Country')
    plt.title('Global Sales Distribution')
    plt.grid(True, alpha=0.3)
    
    # Add annotations
    for i, bar in enumerate(bars):
        plt.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, 
                f"${sales[i]}M | Growth: {growth[i]}%", va='center')
    
    # Add a colorbar legend
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, norm=plt.Normalize(min(growth), max(growth)))
    sm.set_array([])
    cbar = plt.colorbar(sm)
    cbar.set_label('Growth Rate (%)')

# Function to encode chart as base64 for API
def get_chart_as_base64(create_chart_func):
    plt.figure(figsize=(12, 8))
    create_chart_func()
    plt.tight_layout()
    
    # Save to in-memory buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    buffer.seek(0)
    
    # Encode to base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return image_base64

# Display a chart in the notebook
def display_chart(create_chart_func):
    plt.figure(figsize=(12, 8))
    create_chart_func()
    plt.tight_layout()
    plt.show()

# Main test function for notebooks
def run_test(model="gpt-4o", max_tokens=1000, test_cases=None):
    # openai.api_key = api_key
    
    if test_cases is None:
        # Use all test cases by default
        test_cases = TEST_CASES.keys()
    elif isinstance(test_cases, str):
        # If a single test case name is provided as string
        test_cases = [test_cases]
    
    # Create output directory for results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"chart_table_test_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    chart_functions = {
        "monthly_revenue": create_monthly_revenue_chart,
        "regional_sales": create_regional_sales_chart,
        "product_matrix": create_product_matrix_chart,
        "age_income": create_age_income_chart,
        "stock_performance": create_stock_performance_chart,
        "geographic_sales": create_geographic_sales_chart
    }
    
    results = {}
    test_stats = {
        "total_tokens_table": 0,
        "total_tokens_chart": 0,
        "total_time_table": 0,
        "total_time_chart": 0
    }
    
    # For each selected test case
    for test_name in test_cases:
        if test_name not in TEST_CASES:
            print(f"Warning: Test case '{test_name}' not found. Skipping.")
            continue
            
        test_data = TEST_CASES[test_name]
        print(f"Running test: {test_name}")
        results[test_name] = {
            "table_responses": [],
            "chart_responses": [],
            "questions": test_data["questions"],
            "tokens_table": 0,
            "tokens_chart": 0,
            "time_table": 0,
            "time_chart": 0
        }
        
        # Display chart for reference in notebook
        print(f"\nPreview of chart for {test_name}:")
        display_chart(chart_functions[test_name])
        
        # Get chart as base64
        chart_base64 = get_chart_as_base64(chart_functions[test_name])
        
        # Save chart for reference
        img = Image.open(io.BytesIO(base64.b64decode(chart_base64)))
        img.save(f"{output_dir}/{test_name}_chart.png")
        
        # Save table for reference
        with open(f"{output_dir}/{test_name}_table.txt", "w") as f:
            f.write(test_data["table"])
            
        print(f"\nTable format:")
        print(test_data["table"])
        
        # Test with table
        print(f"\nTesting with table...")
        table_start_time = time.time()
        table_responses = []
        
        for i, question in enumerate(test_data["questions"]):
            try:
                # Create prompt with table and question
                prompt = f"Here is a data table:\n\n{test_data['table']}\n\nQuestion: {question}\n\nPlease provide a detailed answer."
                
                response = openai.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a data analysis assistant. Analyze the data carefully and provide accurate answers."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens
                )
                
                # Extract response and token info
                answer = response.choices[0].message.content
                table_responses.append(answer)
                
                # Update token counts
                results[test_name]["tokens_table"] += response.usage.total_tokens
                
                print(f"    Question {i+1} complete: {question}")
                
            except Exception as e:
                error_msg = f"Error processing table question {i+1}: {str(e)}"
                print(f"    Error: {error_msg}")
                table_responses.append(error_msg)
        
        table_time = time.time() - table_start_time
        results[test_name]["time_table"] = table_time
        results[test_name]["table_responses"] = table_responses
        
        # Test with chart
        print(f"\nTesting with chart...")
        chart_start_time = time.time()
        chart_responses = []
        
        for i, question in enumerate(test_data["questions"]):
            try:
                # Create prompt with chart image and question
                response = openai.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a data analysis assistant. Analyze the data visualizations carefully and provide accurate answers."},
                        {"role": "user", "content": [
                            {"type": "text", "text": f"Here is a data visualization chart:\n\nQuestion: {question}\n\nPlease provide a detailed answer."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{chart_base64}"}}
                        ]}
                    ],
                    max_tokens=max_tokens
                )
                
                # Extract response and token info
                answer = response.choices[0].message.content
                chart_responses.append(answer)
                
                # Update token counts
                results[test_name]["tokens_chart"] += response.usage.total_tokens
                
                print(f"    Question {i+1} complete: {question}")
                
            except Exception as e:
                error_msg = f"Error processing chart question {i+1}: {str(e)}"
                print(f"    Error: {error_msg}")
                chart_responses.append(error_msg)
        
        chart_time = time.time() - chart_start_time
        results[test_name]["time_chart"] = chart_time
        results[test_name]["chart_responses"] = chart_responses
        
        # Display comparison of first question and answer as example
        print("\nSample comparison for first question:")
        print(f"Question: {test_data['questions'][0]}")
        print(f"\nTable response:")
        print(table_responses[0][:500] + "..." if len(table_responses[0]) > 500 else table_responses[0])
        print(f"\nChart response:")
        print(chart_responses[0][:500] + "..." if len(chart_responses[0]) > 500 else chart_responses[0])
        
        # Update overall stats
        test_stats["total_tokens_table"] += results[test_name]["tokens_table"]
        test_stats["total_tokens_chart"] += results[test_name]["tokens_chart"]
        test_stats["total_time_table"] += results[test_name]["time_table"]
        test_stats["total_time_chart"] += results[test_name]["time_chart"]
        
        print(f"\nCompleted test: {test_name}")
        print(f"    Table tokens: {results[test_name]['tokens_table']}, time: {results[test_name]['time_table']:.2f}s")
        print(f"    Chart tokens: {results[test_name]['tokens_chart']}, time: {results[test_name]['time_chart']:.2f}s")
        print()
    
    # Generate summary report
    generate_summary_report(results, test_stats, output_dir)
    
    print(f"\nTest suite completed. Results saved to {output_dir}/")
    return results, output_dir

def generate_summary_report(results, test_stats, output_dir):
    # Save raw results
    with open(f"{output_dir}/raw_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Create summary report
    summary = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_cases": len(results),
        "total_questions": sum(len(TEST_CASES[test_name]["questions"]) for test_name in results.keys()),
        "token_usage": {
            "table_total": test_stats["total_tokens_table"],
            "chart_total": test_stats["total_tokens_chart"],
            "difference_percent": ((test_stats["total_tokens_chart"] - test_stats["total_tokens_table"]) / test_stats["total_tokens_table"]) * 100 if test_stats["total_tokens_table"] > 0 else 0
        },
        "processing_time": {
            "table_total": test_stats["total_time_table"],
            "chart_total": test_stats["total_time_chart"],
            "difference_percent": ((test_stats["total_time_chart"] - test_stats["total_time_table"]) / test_stats["total_time_table"]) * 100 if test_stats["total_time_table"] > 0 else 0
        },
        "test_summaries": {}
    }
    
    # Create summary markdown
    with open(f"{output_dir}/summary_report.md", "w") as f:
        f.write("# Chart vs Table Understanding Test Results\n\n")
        f.write(f"**Date:** {summary['timestamp']}\n\n")
        f.write(f"**Total Test Cases:** {summary['test_cases']}\n")
        f.write(f"**Total Questions:** {summary['total_questions']}\n\n")
        
        f.write("## Overall Statistics\n\n")
        f.write("### Token Usage\n")
        f.write(f"- **Table Format:** {summary['token_usage']['table_total']} tokens\n")
        f.write(f"- **Chart Format:** {summary['token_usage']['chart_total']} tokens\n")
        f.write(f"- **Difference:** {summary['token_usage']['difference_percent']:.2f}%\n\n")
        
        f.write("### Processing Time\n")
        f.write(f"- **Table Format:** {summary['processing_time']['table_total']:.2f} seconds\n")
        f.write(f"- **Chart Format:** {summary['processing_time']['chart_total']:.2f} seconds\n")
        f.write(f"- **Difference:** {summary['processing_time']['difference_percent']:.2f}%\n\n")
        
        f.write("## Test Case Summaries\n\n")
        
        # For each test case
        for test_name, test_results in results.items():
            summary["test_summaries"][test_name] = {
                "tokens_table": test_results["tokens_table"],
                "tokens_chart": test_results["tokens_chart"],
                "time_table": test_results["time_table"],
                "time_chart": test_results["time_chart"]
            }
            
            f.write(f"### {test_name.replace('_', ' ').title()}\n\n")
            f.write(f"- **Tokens (Table):** {test_results['tokens_table']}\n")
            f.write(f"- **Tokens (Chart):** {test_results['tokens_chart']}\n")
            f.write(f"- **Time (Table):** {test_results['time_table']:.2f}s\n")
            f.write(f"- **Time (Chart):** {test_results['time_chart']:.2f}s\n\n")
            
            # Write individual test case report
            with open(f"{output_dir}/{test_name}_comparison.md", "w") as case_file:
                case_file.write(f"# {test_name.replace('_', ' ').title()} Test Case Comparison\n\n")
                
                for i, question in enumerate(test_results["questions"]):
                    case_file.write(f"## Question {i+1}: {question}\n\n")
                    case_file.write("### Table Response\n\n")
                    case_file.write(f"{test_results['table_responses'][i]}\n\n")
                    case_file.write("### Chart Response\n\n")
                    case_file.write(f"{test_results['chart_responses'][i]}\n\n")
                    case_file.write("---\n\n")
            
            # Reference in main summary
            f.write(f"[Detailed comparison](./{test_name}_comparison.md)\n\n")
    
    # Write a CSV for easy comparison
    with open(f"{output_dir}/metrics_comparison.csv", "w") as f:
        f.write("Test Case,Table Tokens,Chart Tokens,Token Difference %,Table Time (s),Chart Time (s),Time Difference %\n")
        
        for test_name, test_results in results.items():
            token_diff = ((test_results["tokens_chart"] - test_results["tokens_table"]) / test_results["tokens_table"]) * 100 if test_results["tokens_table"] > 0 else 0
            time_diff = ((test_results["time_chart"] - test_results["time_table"]) / test_results["time_table"]) * 100 if test_results["time_table"] > 0 else 0
            
            f.write(f"{test_name},{test_results['tokens_table']},{test_results['tokens_chart']},{token_diff:.2f}%,")
            f.write(f"{test_results['time_table']:.2f},{test_results['time_chart']:.2f},{time_diff:.2f}%\n")

    return summary

# Create comparison dataframe with correct answers
def create_comparison_dataframe(results):
    """
    Create a pandas DataFrame comparing correct answers with LLM responses
    for both table and chart formats.
    """
    rows = []
    
    for test_name, test_results in results.items():
        test_data = TEST_CASES[test_name]
        
        for i, question in enumerate(test_data["questions"]):
            correct_answer = test_data["correct_answers"][i]
            table_response = test_results["table_responses"][i]
            chart_response = test_results["chart_responses"][i]
            
            # Truncate responses if they're too long for display
            if len(table_response) > 500:
                table_response = table_response[:500] + "..."
            if len(chart_response) > 500:
                chart_response = chart_response[:500] + "..."
            
            row = {
                "Test Case": test_name.replace("_", " ").title(),
                "Question": question,
                "Correct Answer": correct_answer,
                "Table Response": table_response,
                "Chart Response": chart_response
            }
            rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    return df

# Example usage in notebook
# Uncomment and modify the following to run the test

# Run a single test case with the current GPT-4 model with vision capabilities
results, output_dir = run_test(model="gpt-4o", test_cases="monthly_revenue")

# Run multiple test cases
# results, output_dir = run_test(model="gpt-4o", test_cases=["monthly_revenue", "regional_sales"])

# Run all test cases
# results, output_dir = run_test(model="gpt-4o")

# Create a DataFrame with metrics for analysis
df_metrics = create_metrics_dataframe(results)
display(df_metrics)

# Create a DataFrame comparing correct answers with model responses
df_comparison = create_comparison_dataframe(results)
display(df_comparison)

# Evaluate accuracy of model responses
df_accuracy = evaluate_response_accuracy(results)
display(df_accuracy)

# Visualize token usage comparison
plt.figure(figsize=(10, 6))
plt.bar(df_metrics["test_case"], df_metrics["table_tokens"], label="Table Tokens")
plt.bar(df_metrics["test_case"], df_metrics["chart_tokens"], label="Chart Tokens", alpha=0.7)
plt.xlabel("Test Case")
plt.ylabel("Token Usage")
plt.title("Token Usage: Table vs Chart")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Visualize accuracy comparison (if applicable)
if not isinstance(df_accuracy["table_accuracy"].iloc[0], str):  # Check if we have numeric accuracy values
    plt.figure(figsize=(10, 6))
    plt.bar(df_accuracy["test_case"], df_accuracy["table_accuracy"], label="Table Accuracy")
    plt.bar(df_accuracy["test_case"], df_accuracy["chart_accuracy"], label="Chart Accuracy", alpha=0.7)
    plt.xlabel("Test Case")
    plt.ylabel("Accuracy (%)")
    plt.title("Accuracy: Table vs Chart")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
