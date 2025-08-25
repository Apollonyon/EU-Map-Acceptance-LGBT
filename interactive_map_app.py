import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

# Page Configuration (applied from config.toml) to give the good look woop woop
st.set_page_config(
    page_title="EU Acceptance Map",
    page_icon="🗺️",
    layout="wide"
)

# Data Loading and Preparation (Cached)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('EU_Acceptance_QB15_Combined_from_XLSX.csv')
    except FileNotFoundError:
        return None

    # hardcoded the question titles because for love of god I couldnt get them out of the xlsx at all >.<
    question_mapping = {
        "Question from sheet 'QB15_1'": "Equal rights for gay, lesbian, and bisexual people",
        "Question from sheet 'QB15_2'": "Acceptance of same-sex relationships",
        "Question from sheet 'QB15_3'": "Allowance of same-sex marriage throughout Europe",
        "Question from sheet 'QB15_4'": "Adoption rights for same-sex couples"
    }
    df['question'] = df['question'].replace(question_mapping)
    
    def get_country_name(code):
        try:
            return pycountry.countries.get(alpha_2=code).name
        except AttributeError:
            return code # Return the original code if not found

    df['country_name'] = df['code'].apply(get_country_name)

    # Map 2-letter to 3-letter country codes so Plotly can map them correctly
    code_mapping = {
        'BE': 'BEL', 'BG': 'BGR', 'CZ': 'CZE', 'DK': 'DNK', 'DE': 'DEU',
        'EE': 'EST', 'IE': 'IRL', 'GR': 'GRC', 'ES': 'ESP', 'FR': 'FRA',
        'HR': 'HRV', 'IT': 'ITA', 'CY': 'CYP', 'LV': 'LVA', 'LT': 'LTU',
        'LU': 'LUX', 'HU': 'HUN', 'MT': 'MLT', 'NL': 'NLD', 'AT': 'AUT',
        'PL': 'POL', 'PT': 'PRT', 'RO': 'ROU', 'SI': 'SVN', 'SK': 'SVK',
        'FI': 'FIN', 'SE': 'SWE'
    }
    df['iso_alpha'] = df['code'].map(code_mapping)
    return df

df = load_data()

# --- App Layout and Typography ---
# Use markdown with unsafe_allow_html for custom styling
st.markdown("<h1 style='text-align: center;'>EU Acceptance on LGBT Rights</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #BDBDBD;'>Select a question to visualize the 2023 Eurobarometer survey results on the map.</p>", unsafe_allow_html=True)
st.divider()

if df is None:
    st.error("Could not load the data file: 'EU_Acceptance_QB15_Combined_from_XLSX.csv'. Please make sure it's in the same folder.")
else:
    #ain Layout Controls
    question_options = df['question'].unique()
    
    selected_question = st.radio(
        "**Select a question to display:**",
        question_options,
        horizontal=True,
    )

    # Data Based on Selection
    df_filtered = df[df['question'] == selected_question]

    # Create the Choropleth Map (for once learning the names in Data Visualisation class is useful lole)
    fig = px.choropleth(
        df_filtered,
        locations="iso_alpha",
        color="acceptance",
        hover_name="country_name",
        custom_data="country_name",
        hover_data={'iso_alpha': False, 'acceptance': ':.1f%'},
        scope="europe",
        color_continuous_scale="ice",
        range_color=[0, 100]
    )

    fig.update_layout(
        # adds a dynamic title based on the question u selected
        title=dict(text=f"<b>{selected_question}</b>", x=0.4575, y=0.95, xanchor='center', yanchor='top'),
        margin=dict(l=0, r=0, t=40, b=0),
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            showcountries=True, 
            countrycolor="#3C3F4A",
            lakecolor= '#1C1F2B'
        ),
        font_color="#FAFAFA",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_colorbar=dict(
        title="Acceptance (%)",   # Sets the title of the legend
        thicknessmode="pixels", thickness=15, # Sets the thickness in pixels
        lenmode="pixels", len=300,           # Sets the length in pixels
        yanchor="middle", y=0.5              # Vertically centers the legend
        )
    )
    
    fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Acceptance: %{z:.1f}%<extra></extra>')
    
    fig.update_geos(
            center={"lat": 54, "lon": 15},
            projection_scale=4
    )

    # Display the Map and Data and my stuff
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Data Table for this Topic"):
        df_display = df_filtered[['country_name', 'acceptance']].rename(
            columns={'country_name': 'Country', 'acceptance': 'Acceptance (%)'}
        ).sort_values('Acceptance (%)', ascending=False)
        
        # --- THIS IS THE NEW PART ---
        # Convert the number to a string and manually add the '%' sign.
        df_display['Acceptance (%)'] = df_display['Acceptance (%)'].astype(str) + '%'
        # --- END OF NEW PART ---

        # Display the dataframe, now without the column_config
        st.dataframe(
            df_display,
            use_container_width=True
        )
    st.divider()
    st.markdown(
    """
    ### About this visualization
    This interactive map was created to show the acceptance of LGBT rights across EU countries based on the 2023 Eurobarometer survey.  
    https://data.europa.eu/data/datasets/s2972_99_2_sp535_eng?locale=en You can find the original dataset here.  
    I used Volume A, which covers social topics including discrimination and acceptance of LGBT individuals. I extracted the relevant sheets (QB15_1 to QB15_4) that focus on acceptance of same-sex relationships. Then I cleaned and processed the data and put totally agree and tend to agree together to get the acceptance rate of each country.  
    The data I processed with Python and Pandas and I visualised it with Plotly and Streamlit.  `
    This visualisation was made by @ApollonyEos on Twitter. If you have any questions or feedback, feel free to reach out!
    """
    )
    st.caption("Created on August 25, 2025")