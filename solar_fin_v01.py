import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
import base64
import tempfile
import fpdf
from fpdf import FPDF
from PIL import Image
from forex_python.converter import CurrencyRates, CurrencyCodes
from datetime import datetime
import yfinance as yf
from fpdf.enums import XPos, YPos
import io
from io import BytesIO

# Meta description for SEO optimization
meta_description = """
    <meta name="description" content="Solar PV System Financial Calculator helps analyze energy consumption, optimize solar energy generation, and evaluate financial metrics such as NPV, IRR, and payback period. Ideal for solar engineers, renewable energy enthusiasts, and investors.">
"""
st.markdown(meta_description, unsafe_allow_html=True)

schema_markup = """
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Solar PV System Financial Calculator",
  "description": "A financial calculator for Solar PV systems to analyze energy consumption, IRR, NPV, and payback period.",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "All",
  "url": "https://your-streamlit-app-url.com"
}
</script>
"""
st.markdown(schema_markup, unsafe_allow_html=True)

meta_tag = """
<meta name="google-site-verification" content="ttk9iJxghxavRmLn7g_YdUQXxJ1YiixqxOHyGW2CukY" />
"""
st.markdown(meta_tag, unsafe_allow_html=True)

st.write(f"FPDF version: {fpdf.__version__}")

#-------Currency Converter Mini-App------#

# Sidebar section for real-time currency converter
st.sidebar.header("Real-Time Currency Converter")

# Currency selection
from_currency = st.sidebar.selectbox("From Currency", ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "AED", "OMR"])
to_currency = st.sidebar.selectbox("To Currency", ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "AED", "OMR"])

# Amount input
amount = st.sidebar.number_input("Amount to Convert", min_value=0.0, value=1.0, step=0.01)

# Conversion logic
if st.sidebar.button("Convert"):
    try:
        # Get the conversion rate using Yahoo Finance
        pair_symbol = f"{from_currency}{to_currency}=X"
        conversion_rate = yf.Ticker(pair_symbol).history(period="1d")['Close'].iloc[-1]
        
        # Perform the conversion
        converted_amount = amount * conversion_rate
        
        # Display the result
        st.sidebar.success(f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}")
    
    except Exception as e:
        st.sidebar.error(f"Error in conversion: {str(e)}")


#--------------------------#
#-----------App Header Style--------#

page_style = """
    <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .hero {
            background-image: url('https://i.imgur.com/8g1pRFY.png');
            background-size: cover;
            background-position: center;
            padding: 20px 20px;  /* Reduced padding */
            text-align: center;
            color: white;
        }
        .hero h1 {
            font-size: 48px;
            font-weight: bold;
            color: #333333; /* Dark grey color */
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4); /* Dark shadow effect */
            background-color: rgba(255, 255, 255, 0.7); /* Semi-transparent white background */
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            margin-bottom: 20px; /* Added space between header and sub-header */
        }
        .hero p {
            font-size: 24px;
            color: #333333; /* Dark grey color */
            background-color: rgba(255, 255, 255, 0.7); /* Semi-transparent white background */
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
        }
        
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
"""

# Hero section with background image
hero_section = """
<div class="hero">
    <h1>Solar PV System Financial Calculator</h1>
    <p>Analyze your energy consumption and optimize solar energy generation with ease.</p>
</div>
"""

st.markdown(page_style, unsafe_allow_html=True)
st.markdown(hero_section, unsafe_allow_html=True)
#--------------Main Code----------#
st.write('\n')
st.write('\n')
st.write('\n')


# Initialize the CurrencyCodes class
c = CurrencyCodes()

# Example usage: get the symbol for a currency code
col1,col2,col3=st.columns(3)
currency_code = col2.selectbox("Select Currency", ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "OMR"])
currency_symbol = c.get_symbol(currency_code)

col1,col2,col3=st.columns(3)
col2.write(f"Selected Currency: {currency_code} ({currency_symbol})")

# Constants from EPA
KWH_PER_HOUSEHOLD = 10800
CO2_PER_KWH = 0.82  # kg CO2 per kWh
GALLON_GAS_CO2 = 8.887  # kg CO2 per gallon of gasoline
CO2_PER_CAR = 4.2  # metric tons of CO2 per car per year
TREE_SEEDLING_CO2 = 0.039  # metric tons of CO2 per tree seedling over 10 years

# CSS & HTML
def styled_text_block(text, font_size='24px', color='#000000', background_color='#DBEAFE'):
    html_code = f"""
    <style>
    .styled-text {{
        font-size: {font_size};
        font-weight: bold;
        color: {color};
        background-color: {background_color};
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
    }}
    </style>
    <div class="styled-text">
        {text}
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)
    
def render_centered_text_block(title, main_text, title_tag='h3', main_text_tag='h2', width='400px', background_color='#ffffff', fa_icon=None, icon_color=None):
    # Enhanced CSS for the centered text block with reduced width and hover effect
    centered_text_style = f"""
        <style>
        .centered-text-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            text-align: center;
            background-color: {background_color} !important;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: {width}; /* Adjust the width as needed */
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .centered-text-container:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }}
        .centered-text-container {title_tag} {{
            margin: 0;
            font-size: 24px;
            color: #555;
        }}
        .centered-text-container {main_text_tag} {{
            margin: 10px 0 0;
            font-size: 32px;
            font-weight: bold;
            color: #000;
        }}
        .fa-icon {{
            color: {icon_color};
            margin-bottom: 10px;
            font-size: 48px;
        }}
        </style>
    """
    
    # HTML for centered text block with optional Font Awesome icon
    icon_html = f'<i class="{fa_icon} fa-icon"></i>' if fa_icon else ''
    centered_text_html = f"""
        <div class="centered-text-container">
            {icon_html}
            <{title_tag}>{title}</{title_tag}>
            <{main_text_tag}>{main_text}</{main_text_tag}>
        </div>
    """
    
    # Render CSS and HTML in Streamlit
    st.markdown(centered_text_style, unsafe_allow_html=True)
    st.markdown(centered_text_html, unsafe_allow_html=True)

# Font Awesome CSS link
st.markdown('<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">', unsafe_allow_html=True)

# Input form
# Form Sections for User Inputs
# Inject custom CSS to style input fields and background
st.markdown("""
    <style>
    /* Styling for the form background and elements */
    .form-container {
        background-color: #edfae2;  /* Light gray background color */
        padding: 0px;  /* Add padding around the form */
        border-radius: 10px;  /* Rounded corners for the form */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);  /* Subtle shadow for depth */
        margin-top: 0px;
    }

    /* Styling for individual input fields */
    input, textarea, select {
        background-color: #edfae2 !important;  /* White background for inputs */
        color: #464a43 !important;  /* Text color */
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        border: 1px solid #cccccc;
    }

    /* Styling for form title */
    .form-container h3 {
        color: #333333;
        margin-bottom: 20px;
    }
    
    /* Styling for the submit button container */
    .submit-container {
        text-align: center;  /* Center the button */
        margin-top: 20px;  /* Add margin above the button */
    }

    /* Styling for the submit button */
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
        align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Begin form container div
st.markdown('<div class="form-container">', unsafe_allow_html=True)

# Input form
with st.form(key='solar_form'):
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Client Details")
        client_name = st.text_input("Client Name")
        client_address = st.text_input("Client Address")
        client_email = st.text_input("Client Email")
    with col2:
        st.write("### Company Details")
        company_name = st.text_input("Company Name")
        company_prepared_by = st.text_input("Prepared by")
        company_email = st.text_input("Company Email")
    
    st.write('_____')
    st.write("## Solar PV System & Financial Details")
    
    col1, col2 = st.columns(2)
    with col1:
        initial_investment = st.number_input(f"Initial Investment ({currency_symbol}/Wp)", min_value=0.0, value=1.0, step=0.01)
        project_capacity = st.number_input("Project Capacity (kWp)", min_value=0.0, value=1.0, step=0.1)
        o_and_m_cost = st.number_input(f"O&M Cost ({currency_symbol}/kWp per year)", min_value=0.0, value=10.0, step=0.1)
        electricity_cost = st.number_input(f"Cost of Electricity ({currency_symbol}/kWh)", min_value=0.0, value=0.1, step=0.01)
        project_life = st.number_input("Project Life (years)", min_value=1, value=25, step=1)
        energy_generation_first_year = st.number_input("Energy Generation for First Year (kWh)", min_value=0.0, value=1500.0, step=1.0)
    with col2:
        yearly_degradation = st.number_input("Yearly Degradation in Generation (%)", min_value=0.0, value=0.5, step=0.01)
        o_and_m_escalation = st.number_input("O&M Cost Escalation (%)", min_value=0.0, value=2.0, step=0.1)
        electricity_tariff_escalation = st.number_input("Electricity Tariff Escalation (%)", min_value=0.0, value=2.0, step=0.1)
        escalation_years = st.number_input("Escalation Period (years)", min_value=1, value=1, step=1)
        discount_rate = st.number_input("Discount Rate (%)", min_value=0.0, value=5.0, step=0.1) / 100
        project_name = st.text_input('Name of the Project')
    
    submit_button = st.form_submit_button(label='Calculate')

# End the form container div
st.markdown('</div>', unsafe_allow_html=True)



# Upload the company logo
logo_file = st.file_uploader("Choose a company logo (PNG/JPEG)", type=["png", "jpeg", "jpg"])

# Calculations
if submit_button:
    initial_investment_total = initial_investment * project_capacity * 1000  # Convert kWp to Wp
    yearly_generation = energy_generation_first_year
    total_revenue = 0
    total_o_and_m_cost = 0
    cash_flows = [-initial_investment_total]
    yearly_generations = []
    yearly_degradations = []
    yearly_gross_revenues = []
    yearly_o_and_m_expenses = []
    cumulative_net_revenues = []
    cumulative_net_revenue = -initial_investment_total
    annual_rois = []

    for year in range(1, project_life + 1):
        annual_revenue = yearly_generation * electricity_cost
        annual_o_and_m_cost = o_and_m_cost * project_capacity

        if year % escalation_years == 0 and year != 1:
            o_and_m_cost *= (1 + o_and_m_escalation / 100)
            electricity_cost *= (1 + electricity_tariff_escalation / 100)

        cash_flow = annual_revenue - annual_o_and_m_cost
        cash_flows.append(cash_flow)

        cumulative_net_revenue += cash_flow
        cumulative_net_revenues.append(cumulative_net_revenue)

        yearly_generations.append(yearly_generation)
        yearly_degradations.append(yearly_generation * yearly_degradation / 100)
        yearly_gross_revenues.append(annual_revenue)
        yearly_o_and_m_expenses.append(annual_o_and_m_cost)

        total_revenue += annual_revenue
        total_o_and_m_cost += annual_o_and_m_cost
        yearly_generation *= (1 - yearly_degradation / 100)

        # Calculate ROI for the year
        annual_roi = (cash_flow / initial_investment_total) * 100
        annual_rois.append(annual_roi)

    # NPV calculation
    npv = npf.npv(discount_rate, cash_flows)
    
    # IRR calculation
    irr = npf.irr(cash_flows) * 100

    # Simple payback period calculation
    cumulative_cash_flow = np.cumsum(cash_flows)
    payback_period_years = np.argmax(cumulative_cash_flow > 0)
    
    if payback_period_years == 0:
        payback_period_months = 0
    else:
        previous_year_cash_flow = cumulative_cash_flow[payback_period_years - 1]
        year_cash_flow = cumulative_cash_flow[payback_period_years]
        additional_months_fraction = (previous_year_cash_flow) / (previous_year_cash_flow - year_cash_flow)
        additional_months = int(additional_months_fraction * 12)
        payback_period_years -= 1

    # Calculate annual average ROI
    annual_average_roi = np.mean(annual_rois)
    
    # LCoE calculation
    total_costs = initial_investment_total + sum(yearly_o_and_m_expenses[i] / (1 + discount_rate) ** (i + 1) for i in range(project_life))
    total_generation = sum(yearly_generations[i] / (1 + discount_rate) ** (i + 1) for i in range(project_life))
    lcoe = total_costs / total_generation

    st.subheader("Results")
    #st.write(f"Total Gross Revenue: {currency_symbol}{total_revenue:,.2f}")
    #st.write(f"Total O&M Cost: {currency_symbol}{total_o_and_m_cost:,.2f}")
    #st.write(f"Total Net Revenue: {currency_symbol}{cumulative_net_revenue:,.2f}")
    #st.write(f"NPV: {currency_symbol}{npv:,.2f}")
    #st.write(f"IRR: {irr:.2f}%")
    #st.write(f"Simple Payback Period: {payback_period_years} years and {additional_months} months")
    #st.write(f"Annual Average ROI: {annual_average_roi:.2f}%")
    #st.write(f"LCoE: {currency_symbol}{lcoe:.4f}/kWh")

    # Key Metrics Display
    render_centered_text_block("Levelized Cost of Energy", f"{currency_symbol}{lcoe:.4f}/kWh", width='800px', fa_icon='fas fa-balance-scale', icon_color='darkblue')
    col1, col2 = st.columns(2)
    with col1:
        render_centered_text_block("Total Gross Revenue", f"{currency_symbol}{total_revenue:,.2f}", background_color='#DBD46D', fa_icon='fas fa-dollar-sign', icon_color='green')
    with col2:
        render_centered_text_block("Total O&M Cost", f"{currency_symbol}{total_o_and_m_cost:,.2f}", background_color='#DBEAFE', fa_icon='fas fa-tools', icon_color='red')
    render_centered_text_block("Total Net Revenue", f"{currency_symbol}{cumulative_net_revenue:,.2f}", background_color='#DBEAFE', fa_icon='fas fa-chart-line', icon_color='blue')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_centered_text_block("NPV", f"{currency_symbol}{npv:,.2f}", background_color='#DBD46D', fa_icon='fas fa-money-bill-wave', icon_color='orange')
    with col2:
        render_centered_text_block("IRR", f"{irr:.2f}%", background_color='#DBEAFE', fa_icon='fas fa-percentage', icon_color='purple')
    with col3:
        render_centered_text_block("Annual Avg ROI", f"{annual_average_roi:.2f}%", background_color='#DBEAFE', fa_icon='fas fa-chart-pie', icon_color='darkgreen')
    render_centered_text_block("Simple Payback Period", f"{payback_period_years} years and {additional_months} months", background_color='#DBEAFE', fa_icon='fas fa-hourglass-half', icon_color='brown')

    # Data for plots
    # Calculating % Yearly Degradation
    percentage_yearly_degradation = [((initial_gen - current_gen) / initial_gen) * 100 
                                     for initial_gen, current_gen in zip([energy_generation_first_year]*project_life, yearly_generations)]
    
    # Constructing the DataFrame with an additional column for % Yearly Degradation
    df_cash_flows = pd.DataFrame({
        'Year': range(1, project_life + 1),
        'Energy Yield (kWh)': yearly_generations,
        'Yearly Degradation (kWh)': yearly_degradations,
        '% Yearly Degradation': percentage_yearly_degradation,
        f'Gross Revenue ({currency_symbol})': yearly_gross_revenues,
        f'O&M Expense ({currency_symbol})': yearly_o_and_m_expenses,
        f'Cash Flow ({currency_symbol})': cash_flows[1:],
        f'Cumulative Net Revenue ({currency_symbol})': cumulative_net_revenues
    })
    
    # Create a figure and axis with a specified figure size
    fig1, ax1 = plt.subplots()  # Set a reasonable size for the figure
    
    # Bar chart for Yearly Generation (Energy Yield)
    bars = ax1.bar(df_cash_flows['Year'], df_cash_flows['Energy Yield (kWh)'], color='#1E90FF', label='Energy Yield (kWh)')
    
    # Create a second y-axis for the line chart of Yearly Degradation (%)
    ax2 = ax1.twinx()
    
    # Line chart for Yearly Degradation (%)
    ax2.plot(df_cash_flows['Year'], df_cash_flows['% Yearly Degradation'], color='orange', linewidth=2.5, marker='o', label='% Yearly Degradation')
    
    # Set axis labels and title
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Energy Yield (kWh)', color='#1E90FF')
    ax2.set_ylabel('% Yearly Degradation', color='orange')
    plt.title('Year-On-Year Degradation Analysis – For 25 Years', fontsize=14)
    
    # Set the limits for the y-axes
    ax1.set_ylim(df_cash_flows['Energy Yield (kWh)'].min() * 0.5, df_cash_flows['Energy Yield (kWh)'].max() * 1.05)  # Dynamic limits based on data
    ax2.set_ylim(0, df_cash_flows['% Yearly Degradation'].max() * 1.1)  # Adjust the limits for Yearly Degradation (%)
    
    # Set the ticks for the x-axis to show all the years
    ax1.set_xticks(df_cash_flows['Year'])
    
    # Add integer data labels inside the bars at the top edge
    for bar in bars:
        yval = int(bar.get_height())  # Convert to integer
        ax1.text(bar.get_x() + bar.get_width() / 2, yval - 5, f'{yval}', ha='center', va='top', fontsize=9, color='white', rotation=90, fontweight='bold')
    
    # Legends for both the bar chart and the line chart
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    
    # Save and display the chart
    plt.savefig('yearly_generation_degradation.png')
    st.pyplot(fig1)
    plt.close(fig1)
    
    # Cumulative Cash Flow and Break-even
    fig33, ax3 = plt.subplots()
    ax3.plot(df_cash_flows['Year'], cumulative_cash_flow[1:], marker='o', label='Cumulative Cash Flow')
    ax3.axhline(0, color='red', linestyle='--')
    ax3.annotate(f'Simple Payback in: {payback_period_years} years and {additional_months} months',
                 xy=(payback_period_years, 0), xytext=(payback_period_years, -0.1 * max(cumulative_cash_flow)),
                 arrowprops=dict(facecolor='black', arrowstyle='->'))
    ax3.set_xlabel('Year')
    ax3.set_ylabel(f'Cumulative Cash Flow ({currency_symbol})')
    ax3.set_title('Cumulative Cash Flow and Break-even')
    ax3.legend()
    
    # Save the chart as an image
    plt.savefig('cumulative_cash_flow.png')
    
    # Yearly Gross Revenue and O&M Expense
    fig44, ax4 = plt.subplots()
    width = 0.35  # Width of the bars
    ax4.bar(df_cash_flows['Year'] - width/2, df_cash_flows[f'Gross Revenue ({currency_symbol})'], width, label='Yearly Gross Revenue')
    ax4.bar(df_cash_flows['Year'] + width/2, df_cash_flows[f'O&M Expense ({currency_symbol})'], width, label='Yearly O&M Expense', color='red')
    ax4.set_xlabel('Year')
    ax4.set_ylabel(f'Amount ({currency_symbol})')
    ax4.set_title('Yearly Gross Revenue and O&M Expense')
    ax4.legend()
    
    # Save the chart as an image
    plt.savefig('yearly_gross_revenue_om_expense.png')
    
    # Display the charts in Streamlit
    st.pyplot(fig33)
    st.pyplot(fig44)


    # Table display
    styled_df = df_cash_flows.style.format({
        'Year': '{:.0f}',
        'Energy Yield (kWh)': '{:.2f}',
        'Yearly Degradation (kWh)': '{:.2f}',
        '% Yearly Degradation':'{:.2f}',
        f'Gross Revenue ({currency_symbol})': '{:.2f}',
        f'O&M Expense ({currency_symbol})': '{:.2f}',
        f'Cash Flow ({currency_symbol})': '{:.2f}',
        f'Cumulative Net Revenue ({currency_symbol})': '{:.2f}'
    }).set_table_styles(
        [{'selector': 'td', 'props': [('text-align', 'center')]},
         {'selector': 'th', 'props': [('text-align', 'center')]}]
    )

    html_cash_flows_df = styled_df.to_html(index=False)
    styled_text_block("Lifetime Energy Yield (kWh) and Cash Flows", color='#333333', background_color='#FFFFE0')

    # Center the table using HTML and CSS
    centered_table = f"""
    <div style="display: flex; justify-content: center;text-align: center;">
        {html_cash_flows_df}</div>
    """

    st.markdown(centered_table, unsafe_allow_html=True)

    # Environmental Benefits
    houses_energized = yearly_generation / KWH_PER_HOUSEHOLD
    co2_saved_kg = yearly_generation * CO2_PER_KWH
    gallons_gas_saved = co2_saved_kg / GALLON_GAS_CO2
    co2_saved_tonnes = co2_saved_kg / 1000
    cars_taken_off_road = co2_saved_tonnes / CO2_PER_CAR
    tree_seedlings = co2_saved_tonnes / TREE_SEEDLING_CO2

    st.write('\n')
    st.write('\n')
    st.write('\n')


    st.markdown(f"""
        <div style="text-align: center;">
            <h2>Environmental Benefits</h2>
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                <div style="margin: 20px;">
                    <i class="fas fa-home fa-3x" style="color: orange;"></i>
                    <h3>{houses_energized:.2f}</h3>
                    <p>Houses Energized per Year</p>
                </div>
                <div style="margin: 20px;">
                    <i class="fas fa-gas-pump fa-3x" style="color: skyblue;"></i>
                    <h3>{gallons_gas_saved:.2f}</h3>
                    <p>Gallons of Gas Saved per Year</p>
                </div>
                <div style="margin: 20px;">
                    <i class="fas fa-car fa-3x" style="color: blue;"></i>
                    <h3>{cars_taken_off_road:.2f}</h3>
                    <p>Cars Taken Off Road per Year</p>
                </div>
                <div style="margin: 20px;">
                    <i class="fas fa-tree fa-3x" style="color: green;"></i>
                    <h3>{tree_seedlings:.2f}</h3>
                    <p>Tree Seedlings Grown for 10 Years</p>
                </div>
                <div style="margin: 20px;">
                    <i class="fas fa-cloud fa-3x" style="color: gray;"></i>
                    <h3>{co2_saved_tonnes:.2f}</h3>
                    <p>Tonnes of CO2 Emissions Saved per Year</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    df_cash_flows_pdf = pd.DataFrame({
        'Year': range(1, project_life + 1),
        f'Gross Revenue ({currency_symbol})': yearly_gross_revenues,
        f'O&M Expense ({currency_symbol})': yearly_o_and_m_expenses,
        f'Cash Flow ({currency_symbol})': cash_flows[1:],
        f'Cumulative Net Revenue ({currency_symbol})': cumulative_net_revenues
    })
    
    df_cash_flows_pdf = df_cash_flows_pdf.round({
        'Year': 0,
    f'Gross Revenue ({currency_symbol})': 2,
    f'O&M Expense ({currency_symbol})': 2,
    f'Cash Flow ({currency_symbol})': 2,
    f'Cumulative Net Revenue ({currency_symbol})': 2
    })

    # Enhanced PDF Class with Improved Table Format and Centered Table
    class PDF(FPDF):
        def __init__(self, logo_path=None):
            super().__init__()
            self.logo_path = logo_path
    
            
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 5, f'Page {self.page_no()}', 0, 1, 'C')
            self.set_y(-10)  # Adjust position for the link
            self.cell(0, 5, 'App link: https://solarfinc-v01.streamlit.app/', 0, 0, 'C', link='https://energy-eda-v01.streamlit.app/')

        def cover_page(self, client_name, client_address, project_name, company_name, prepared_by, company_email):
            self.add_page()
        
            # Background color (optional - this will be a colored rectangle)
            self.set_fill_color(230, 240, 255)  # Light blue color
            self.rect(0, 0, 210, 297, 'F')  # Cover the entire page (A4 dimensions)
    
            # Add the logo centered on the cover page
            if self.logo_path:
                self.image(self.logo_path, x=75, y=20, w=60)
    
            self.ln(45)  # Move below the logo
            # Title
            self.set_font('Arial', 'B', 24)
            self.set_text_color(0, 51, 102)  # Dark blue color
            self.cell(0, 10, 'Solar PV System Financial Report', 0, 1, 'C')
            self.ln(10)
            # Decorative Line below title
            self.set_line_width(0.5)
            self.set_draw_color(0, 51, 102)  # Dark blue color
            self.line(60, self.get_y(), 150, self.get_y())
            self.ln(5)
            self.set_font('Arial', 'I', 16)
            self.cell(0, 10, 'Generated by Energy Data Updater and Analytics App', 0, 1, 'C')
            self.ln(10)
            
            
            # Client Details Table
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Client Details', 0, 1, 'C')
            
            # Calculate x position for centering the table
            table_width = 150  # Define the width of the table
            x_position = (self.w - table_width) / 2
            
            # Draw the Client Details table
            self.set_x(x_position)
            self.set_font('Arial', '', 12)
            self.cell(45, 10, 'Client Name:', 1, 0, 'C')
            self.cell(105, 10, client_name, 1, 1, 'C')
        
            self.set_x(x_position)
            self.cell(45, 10, 'Client Address:', 1, 0, 'C')
            self.cell(105, 10, client_address, 1, 1, 'C')
            
            self.set_x(x_position)
            self.cell(45, 10, 'Project Details:', 1, 0, 'C')
            self.cell(105, 10, project_name, 1, 1, 'C')
            
            self.ln(10)
        
            # Company Details Table
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Company Details', 0, 1, 'C')
            
            # Draw the Company Details table
            self.set_x(x_position)
            self.set_font('Arial', '', 12)
            self.cell(45, 10, 'Company Name:', 1, 0, 'C')
            self.cell(105, 10, company_name, 1, 1, 'C')
        
            self.set_x(x_position)
            self.cell(45, 10, 'Prepared By:', 1, 0, 'C')
            self.cell(105, 10, prepared_by, 1, 1, 'C')
            
            self.set_x(x_position)
            self.cell(45, 10, 'Company Email:', 1, 0, 'C')
            self.cell(105, 10, company_email, 1, 1, 'C')
        
            self.ln(30)
            
            # Report Generated Date
            self.set_font('Arial', 'I', 12)
            self.cell(0, 10, f'Report Generated: {pd.Timestamp.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
            self.ln(10)
    
    
        def header(self):
            if self.logo_path:
                self.image(self.logo_path, 10, 6, 33)  # Adjust y-position to 6
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Solar PV System Financial Report', 0, 1, 'C')
            self.set_font('Arial', 'I', 10)
            self.cell(0, 10, 'Generated by Energy Data Updater and Analytics App', 0, 1, 'C')
            self.ln(5)
            self.set_line_width(0.5)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)
            
    
        def chapter_title(self, title):
            self.set_font('Arial', 'B', 18)
            self.set_fill_color(216, 248, 171)
            self.set_text_color(0, 102, 204)
            self.cell(0, 10, title, 0, 1, 'C', fill=True)
            self.ln(5)
    
        def chapter_subtitle(self, subtitle):
            self.set_font('Arial', 'B', 14)
            self.set_fill_color(230, 230, 250)
            self.set_text_color(0, 0, 0)
            self.cell(0, 10, subtitle, 0, 1, 'C', fill=True)
            self.ln(5)
    
        def add_form_inputs(self, form_data):
            # Title for Inputs
            self.set_font('Arial', 'B', 16)
            self.set_fill_color(230, 230, 250)
            self.cell(0, 10, 'Project and Financial Inputs', 0, 1, 'C', fill=True)
            self.ln(7)
            
            # Styling for Form Data Display in colorful tabular format
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(255, 228, 225)
            self.cell(90, 7, 'Input Parameter', 1, 0, 'C', fill=True)
            self.cell(0, 7, 'Value', 1, 1, 'C', fill=True)
    
            for title, value in form_data.items():
                self.set_font('Arial', 'B', 12)
                self.set_fill_color(255, 255, 240)
                self.cell(90, 8, f'{title}:', 1, 0, 'L', fill=True)
                self.set_font('Arial', '', 12)
                self.set_fill_color(240, 248, 255)
                self.cell(0, 8, f'{value}', 1, 1, 'R', fill=True)
            self.ln(7)
            
            
        def card(self, title, value, fill_color):
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(*fill_color)
            self.set_text_color(0, 0, 255)
            self.cell(90, 10, f"{title}", 0, 0, 'L', fill=True)
            self.cell(0, 10, f"{value}", 0, 1, 'R', fill=True)
            self.ln(5)
    
        def metric_table(self, metrics, bg_color):
            icon_size = 10
            col_widths = [20, 25, 105]  # Adjusted column widths for better alignment
            row_height = 15  # Adjusted row height
            
            # Calculate total table width
            table_width = sum(col_widths)
            
            # Calculate the center position for the table
            page_width = self.w - 2 * self.l_margin
            x_offset = (page_width - table_width) / 2 + self.l_margin  # Center the table on the page
            
            for metric in metrics:
                self.set_x(x_offset)
                
                # Icon column
                self.set_fill_color(*bg_color)
                self.cell(col_widths[0], row_height, "", border=0, align='C', fill=True)
                self.image(metric['image'], x=self.get_x() - col_widths[0] + icon_size / 2, y=self.get_y() + 2.5, w=icon_size, h=icon_size)
                
                # Value column
                self.cell(col_widths[1], row_height, metric['value'], border=0, align='R', fill=True)
                
                # Description column
                self.cell(col_widths[2], row_height, metric['description'], border=0, align='L', fill=True)
                
                # Move to the next line for the next metric
                self.ln(row_height)
            
            # Space after the table
            self.ln(5)

    
        def add_metric_table(self, title, value, bg_color, x_offset, y_start, width=60):
            self.set_fill_color(*bg_color)
            self.set_text_color(255, 255, 255)
    
            self.set_xy(x_offset, y_start)
            self.cell(width, 10, title, border=1, align='C', fill=True)
            self.ln(10)
    
            self.set_x(x_offset)
            self.set_fill_color(255, 255, 255)
            self.set_text_color(0, 0, 0)
            self.cell(width, 10, value, border=1, align='C', fill=True)
    
        def add_two_column_metrics(self, metrics, column_spacing=10, row_spacing=10):
            page_width = self.w - 2 * self.l_margin
            column_width = (page_width - column_spacing) / 2
            x_offset1 = self.l_margin
            x_offset2 = x_offset1 + column_width + column_spacing
    
            max_rows = len(metrics) // 2 + len(metrics) % 2
            y_start = self.get_y()
    
            for row in range(max_rows):
                y_position = y_start + row * (15 + row_spacing)
                title1, value1, bg_color1 = metrics[row * 2]
                self.add_metric_table(title1, value1, bg_color1, x_offset1, y_position, column_width)
                if row * 2 + 1 < len(metrics):
                    title2, value2, bg_color2 = metrics[row * 2 + 1]
                    self.add_metric_table(title2, value2, bg_color2, x_offset2, y_position, column_width)

        def add_cash_flow_table(self, df_cash_flows_pdf, currency_symbol):
            self.add_page()
            self.chapter_title('Cash Flow Analysis')
        
            # Setting up the table headers with a line break in the 'Cumulative Net Revenue' header
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(240, 240, 240)
            col_widths = [15, 40, 40, 40, 40]  # Adjust column widths as needed
            table_width = sum(col_widths)  # Total width of the table
            # Calculate the starting x position to center the table
            page_width = self.w - 2 * self.l_margin  # Page width minus margins
            x_start_T = (page_width - table_width) / 2 + self.l_margin
            
            # Set the position for the table
            self.set_x(x_start_T)
            
            
            # Regular header for 'Year'
            self.cell(col_widths[0], 20, 'Year', border=1, align='C', fill=True)
            x_start = self.get_x()
        
            # Multi-cell headers for the other columns with a line break before the currency symbol
            self.multi_cell(col_widths[1], 10, f'Gross Revenue\n({currency_symbol})', border=1, align='C', fill=True)
            self.set_xy(x_start + col_widths[1], self.get_y() - 20)  # Reset the position for the next cell in the same row
            self.multi_cell(col_widths[2], 10, f'O&M Expense\n({currency_symbol})', border=1, align='C', fill=True)
            self.set_xy(x_start + col_widths[1] + col_widths[2], self.get_y() - 20)  # Reset the position for the next cell in the same row
            self.multi_cell(col_widths[3], 10, f'Cash Flow\n({currency_symbol})', border=1, align='C', fill=True)
            self.set_xy(x_start + col_widths[1] + col_widths[2] + col_widths[3], self.get_y() - 20)  # Reset the position for the next cell in the same row
            self.multi_cell(col_widths[4], 6.667, f'Cumulative\nNet Revenue\n({currency_symbol})', border=1, align='C', fill=True)

            self.ln(1)
        
            # Filling in the table rows with reduced row height and currency symbols in the values
            self.set_font('Arial', '', 10)
            for index, row in df_cash_flows_pdf.iterrows():
                self.set_x(x_start_T)
                self.cell(col_widths[0], 7, str(int(row['Year'])), border=1, align='C')
                self.cell(col_widths[1], 7, f"{row[f'Gross Revenue ({currency_symbol})']:.0f}", border=1, align='C')
                self.cell(col_widths[2], 7, f"{row[f'O&M Expense ({currency_symbol})']:.0f}", border=1, align='C')
                self.cell(col_widths[3], 7, f"{row[f'Cash Flow ({currency_symbol})']:.0f}", border=1, align='C')
                self.cell(col_widths[4], 7, f"{row[f'Cumulative Net Revenue ({currency_symbol})']:.0f}", border=1, align='C')
                self.ln()

        

        def add_energy_table(self, df_cash_flows):
            self.add_page()
            self.chapter_title('25 Years Energy Yield Data Analysis')
        
            # Set the table column widths
            col_widths = [15, 60, 60]  # Adjust column widths as needed
            table_width = sum(col_widths)  # Total width of the table
            
            # Calculate the starting x position to center the table
            page_width = self.w - 2 * self.l_margin  # Page width minus margins
            x_start = (page_width - table_width) / 2 + self.l_margin
            
            # Set the position for the table
            self.set_x(x_start)
            
            # Set the font for the table headers
            self.set_font('Arial', 'B', 12)
            self.set_fill_color(240, 240, 240)
        
            # Regular headers (single-line headers)
            self.cell(col_widths[0], 10, 'Year', border=1, align='C', fill=True)
            self.cell(col_widths[1], 10, f'Energy Yield (kWh)', border=1, align='C', fill=True)
            self.cell(col_widths[2], 10, f'% Yearly Degradation', border=1, align='C', fill=True)
            self.ln()  # Move to the next line after the headers
        
            # Filling in the table rows with reduced row height
            self.set_font('Arial', '', 10)
            for index, row in df_cash_flows.iterrows():
                self.set_x(x_start)  # Set x position to center the rows
                self.cell(col_widths[0], 7, str(int(row['Year'])), border=1, align='C')
                self.cell(col_widths[1], 7, f"{row[f'Energy Yield (kWh)']:.0f}", border=1, align='C')
                self.cell(col_widths[2], 7, f"{row[f'% Yearly Degradation']:.2f}", border=1, align='C')
                self.ln()  # Move to the next line after each row




    def generate_pdf_report(
        logo_file,
        initial_investment,
        initial_investment_total,
        project_capacity,
        o_and_m_cost,
        electricity_cost,
        project_life,
        energy_generation_first_year,
        yearly_degradation,
        o_and_m_escalation,
        electricity_tariff_escalation,
        discount_rate,
        total_revenue,
        total_o_and_m_cost,
        cumulative_net_revenue,
        npv,
        irr,
        payback_period_years,
        additional_months,
        annual_average_roi,
        lcoe,
        houses_energized,
        gallons_gas_saved,
        cars_taken_off_road,
        tree_seedlings,
        co2_saved_tonnes,
        df_cash_flows_pdf,
        df_cash_flows
    ):

        #pdf = PDF()
        # Save the logo file temporarily if provided
        logo_path = None
        if logo_file is not None:
            logo = Image.open(logo_file)
            logo_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
            logo.save(logo_path)
    
        pdf = PDF(logo_path=logo_path)
        pdf.cover_page(client_name, client_address, company_name, company_prepared_by, company_email, project_name)
        pdf.add_page()
    
        # Title and Subtitle
        pdf.set_font('Arial', 'BI', 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, 'Comprehensive analysis of financial and environmental benefits', 0, 1, 'C')
        #pdf.set_font('Arial', 'I', 16)
        #pdf.set_text_color(105, 105, 105)
        #pdf.cell(0, 10, 'Comprehensive analysis of financial and environmental benefits', 0, 1, 'C')
        pdf.ln(10)
        
        # Connect Form Data to Input Data
        form_data = {
            f"Total Initial Investment ({currency_symbol})": f"{currency_symbol}{initial_investment_total:.2f}",
            "Project Capacity (kWp)": f"{project_capacity} kWp",
            f"O&M Cost ({currency_symbol}/kWp per year)": f"{currency_symbol}{o_and_m_cost:.2f}",
            f"Cost of Electricity ({currency_symbol}/kWh)": f"{currency_symbol}{electricity_cost:.2f}",
            "Project Life (years)": f"{project_life} years",
            "Energy Generation for First Year (kWh)": f"{energy_generation_first_year:.2f} kWh",
            "Yearly Degradation (%)": f"{yearly_degradation:.2f}%",
            "O&M Cost Escalation (%)": f"{o_and_m_escalation:.2f}%",
            "Electricity Tariff Escalation (%)": f"{electricity_tariff_escalation:.2f}%",
            "Discount Rate (%)": f"{discount_rate:.2f}%",
        }
    
        
    
        # Add Form Inputs to the Report
        pdf.add_form_inputs(form_data)
        
        # Center the image in the PDF
        pdf_width = pdf.w - 2 * pdf.l_margin  # The effective width of the PDF (excluding margins)
        image_width = 120  # Set the desired image width
        
        # Calculate the x position to center the image
        x_position = (pdf_width - image_width) / 2 + pdf.l_margin

        # Yearly Generation and Degradation
        pdf.chapter_subtitle('Yearly Generation and Degradation')
        pdf.image('yearly_generation_degradation.png', x=x_position, y=None, w=image_width, h=90)  # Set width (w) and height (h)
        
        pdf.add_page()
    
        # Financial Metrics Section
        pdf.chapter_subtitle('Financial Metrics')
        financial_metrics = [
            ("Total Gross Revenue", f"{currency_symbol}{total_revenue:,.2f}", (0, 102, 204)),
            ("Total O&M Cost", f"{currency_symbol}{total_o_and_m_cost:,.2f}", (255, 165, 0)),
            ("Total Net Revenue", f"{currency_symbol}{cumulative_net_revenue:,.2f}", (34, 139, 34)),
            ("NPV", f"{currency_symbol}{npv:,.2f}", (255, 69, 0)),
            ("IRR", f"{irr:.2f}%", (75, 0, 130)),
            ("Simple Payback Period", f"{payback_period_years} years and {additional_months} months", (255, 215, 0)),
            ("Annual Average ROI", f"{annual_average_roi:.2f}%", (30, 144, 255)),
            ("LCoE", f"{currency_symbol}{lcoe:.4f}/kWh", (220, 20, 60)),
        ]
        pdf.add_two_column_metrics(financial_metrics)
    
        pdf.ln(20)
    
        # Environmental Benefits Section
        pdf.chapter_subtitle('Environmental Benefits')
        
        bg_color = (230, 240, 255)  # Light blue background color
        metrics = [
            {"image": "house.png", "value": f"{houses_energized:.2f}", "description": "Houses\nEnergized per Year"},
            {"image": "petrol-pump.png", "value": f"{gallons_gas_saved:.2f}", "description": "Gallons of Gas\nSaved per Year"},
            {"image": "car-wash.png", "value": f"{cars_taken_off_road:.2f}", "description": "Cars Taken Off\nRoad per Year"},
            {"image": "forest.png", "value": f"{tree_seedlings:.2f}", "description": "Tree Seedlings\nGrown for 10 Years"},
            {"image": "co2.png", "value": f"{co2_saved_tonnes:.2f}", "description": "Tonnes of CO2\nEmissions Saved per Year"},
        ]
        
        pdf.metric_table(metrics, bg_color)
    
        pdf.ln(20)
    
        # Charts Section
        pdf.chapter_title('Charts')
        
        
        
        # Yearly Gross Revenue and O&M Expense
        pdf.chapter_subtitle('Yearly Gross Revenue and O&M Expense')
        pdf.image('yearly_gross_revenue_om_expense.png', x=x_position, y=None, w=image_width, h=90)  # Set width (w) and height (h)

        # Cumulative Cash Flow and Break-even
        pdf.chapter_subtitle('Cumulative Cash Flow and Break-even')
        pdf.image('cumulative_cash_flow.png', x=x_position, y=None, w=image_width, h=90)  # Set width (w) and height (h)
        #pdf.add_page()

        
        
        # Adding the Energy Flow & Cash Flow table on the last page
        pdf.add_energy_table(df_cash_flows)
        pdf.add_cash_flow_table(df_cash_flows_pdf, currency_symbol)
        

        # Create a BytesIO buffer to store the PDF content
        pdf_output = pdf.output(dest='S')  # Get PDF as string
        pdf_buffer = BytesIO(pdf_output)
        pdf_buffer.seek(0)

    
        return pdf_buffer
    
    def provide_pdf_download_link(pdf_buffer, file_name):
        # Encode the PDF content as base64
        b64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')  # Read and encode the binary PDF content
        
        # HTML for the download button with center alignment
        href = f'''
        <div style="display: flex; justify-content: center; align-items: center; margin-top: 20px;">
            <a href="data:application/octet-stream;base64,{b64}" download="{file_name}">
                <button style="padding:10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; font-size: 16px;">
                    Download PDF Report
                </button>
            </a>
        </div>
        '''
        
        # Render the button in Streamlit
        st.markdown(href, unsafe_allow_html=True)
    
    
    
    pdf_buffer = generate_pdf_report(
        logo_file,
        initial_investment=initial_investment,
        initial_investment_total=initial_investment_total,
        project_capacity=project_capacity,
        o_and_m_cost=o_and_m_cost,
        electricity_cost=electricity_cost,
        project_life=project_life,
        energy_generation_first_year=energy_generation_first_year,
        yearly_degradation=yearly_degradation,
        o_and_m_escalation=o_and_m_escalation,
        electricity_tariff_escalation=electricity_tariff_escalation,
        discount_rate=discount_rate,
        total_revenue=total_revenue,
        total_o_and_m_cost=total_o_and_m_cost,
        cumulative_net_revenue=cumulative_net_revenue,
        npv=npv,
        irr=irr,
        payback_period_years=payback_period_years,
        additional_months=additional_months,
        annual_average_roi=annual_average_roi,
        lcoe=lcoe,
        houses_energized=houses_energized,
        gallons_gas_saved=gallons_gas_saved,
        cars_taken_off_road=cars_taken_off_road,
        tree_seedlings=tree_seedlings,
        co2_saved_tonnes=co2_saved_tonnes,
        df_cash_flows_pdf=df_cash_flows_pdf,
        df_cash_flows=df_cash_flows
    )
    
    

    # Provide download link as HTML button
    provide_pdf_download_link(pdf_buffer, "solar_pv_system_financial_report.pdf")
    # Generate a new PDF buffer for the sidebar to avoid data corruption issues
    pdf_buffer_sidebar = generate_pdf_report(
        logo_file,
        df_cash_flows_pdf=df_cash_flows_pdf,
        df_cash_flows=df_cash_flows,
        initial_investment=initial_investment,
        initial_investment_total=initial_investment_total,
        project_capacity=project_capacity,
        o_and_m_cost=o_and_m_cost,
        electricity_cost=electricity_cost,
        project_life=project_life,
        energy_generation_first_year=energy_generation_first_year,
        yearly_degradation=yearly_degradation,
        o_and_m_escalation=o_and_m_escalation,
        electricity_tariff_escalation=electricity_tariff_escalation,
        discount_rate=discount_rate,
        total_revenue=total_revenue,
        total_o_and_m_cost=total_o_and_m_cost,
        cumulative_net_revenue=cumulative_net_revenue,
        npv=npv,
        irr=irr,
        payback_period_years=payback_period_years,
        additional_months=additional_months,
        annual_average_roi=annual_average_roi,
        lcoe=lcoe,
        houses_energized=houses_energized,
        gallons_gas_saved=gallons_gas_saved,
        cars_taken_off_road=cars_taken_off_road,
        tree_seedlings=tree_seedlings,
        co2_saved_tonnes=co2_saved_tonnes
    )
    
    # Provide download link in the sidebar
    with st.sidebar:
        st.write('_________')
        provide_pdf_download_link(pdf_buffer_sidebar, "solar_pv_system_financial_report.pdf")
    
    
    
        
