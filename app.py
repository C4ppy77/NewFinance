from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)

# Define global variables for criteria
profit_margin_threshold = 20
cost_of_parts_threshold = 50
revenue_opportunity_quantile = 0.75
labour_cost_threat_quantile = 0.75

# Function to perform SWOT analysis
def perform_swot_analysis(df):
    df.fillna(0, inplace=True)

    # Required columns check
    required_columns = ['Revenue', 'Cost_of_Parts', 'Cost_of_Toner', 'Labour_Cost', 'Other_Spend']
    if not all(col in df.columns for col in required_columns):
        return None, f"Missing required columns: {', '.join(set(required_columns) - set(df.columns))}"

    # Calculate metrics
    df['Total_Cost'] = df['Cost_of_Parts'] + df['Cost_of_Toner'] + df['Labour_Cost'] + df['Other_Spend']
    df['Profit'] = df['Revenue'] - df['Total_Cost']
    df['Profit_Margin'] = df['Profit'] / df['Revenue'] * 100

    # SWOT analysis
    swot = {'Strengths': [], 'Weaknesses': [], 'Opportunities': [], 'Threats': []}

    if df['Profit_Margin'].mean() > profit_margin_threshold:
        swot['Strengths'].append(f'High Profit Margins (>{profit_margin_threshold}%)')

    if df['Cost_of_Parts'].mean() > cost_of_parts_threshold:
        swot['Weaknesses'].append(f'High Cost of Parts (>{cost_of_parts_threshold})')

    if df['Revenue'].mean() > df['Revenue'].quantile(revenue_opportunity_quantile):
        swot['Opportunities'].append('Revenue Growth Potential')

    if df['Labour_Cost'].mean() > df['Labour_Cost'].quantile(labour_cost_threat_quantile):
        swot['Threats'].append('Rising Labour Costs')

    return swot, None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)
            swot_results, error = perform_swot_analysis(df)
            if error:
                return render_template('index.html', error=error)
            return render_template('results.html', swot=swot_results)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
