# Introduction to the Regulatory Bot

Welcome to our Regulatory Bot. Depending on the bot's mode, it serves different purposes. Here are the available modes:

## 1. **Regulatory expert**
### Role:
- Regulatory assistant providing answers given questions and requirements.
- Uses bullet structure if possible.
- Provides article numbers and source as a separate last line.

### Intro:
- Focused on regulatory questions based on the EBA and ECB regulations.

---

## 2. **Default mode**
### Role:
- Regulatory assistant providing answers given questions and requirements.

### Intro:
- Focused on regulatory questions related to risk.

---

## 3. **Figure search**
### Role:
- Coding assistant providing answers given questions and relevant materials.

### Intro:
- Contains code snippets related specifically to credit risk modelling.

---

## 4. **Risk Data Warehouse**
### Role:
- Returns one of the provided functions. 
- If not enough arguments are provided, it will ask for more information.

### Intro:
- Contains data related to realised and estimated PDs and LGD in EU.
- You can ask questions related to this data.

### Data Structure:
- The table contains the following columns and unique values:
    - **Country**: [List of countries]
    - **Type**: Corporates, Retail
    - **Subtype**: [List of subtypes]
    - **Risk Metrics**: Default Rate, Loss Rate, PD -adjusted, LGD
    - **Reporting Date**: ['2021 Q4', '2020 Q4', '2019 Q4', '2018 Q4']

### Functions:
1. **compare_risk_metrics_of_countries**:
    - Description: Get two or more risk metrics and compare a single country.
    - Parameters: 
        - Country: (e.g. Germany or Poland)
        - Risk Metric: (One of the following: PD, LGD, loss rate or default rate)

2. **plot_metric_in_time_for_countries**:
    - Description: Plot a single metric in time for one or more countries.
    - Parameters:
        - Countries: (e.g. Germany or Poland)
        - Risk Metric: (One of the following: PD, LGD, loss rate or default rate)
        - Start Year: Start year of the period
        - End Year: End year of the period

---

Thank you for using our bot. Feel free to ask any questions!
