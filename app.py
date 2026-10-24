import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Try importing anthropic safely
try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

load_dotenv()

# Define helper function at the top to clear the warning
def show_mock_audit(total, mats, vols, costs):
    st.markdown(f"""
    ### 🔍 Executive Quantity Surveyor Audit Report
    **Project Risk Rating:** 🟠 **HIGH RISK**
    - **Elements Analyzed:** {total}
    - **Missing Materials:** {mats} items require immediate property assignment.
    - **Zero Volumes:** {vols} elements have geometric modeling errors.
    - **Missing Unit Costs:** {costs} items lack baseline cost parameters.
    *Recommendation: Clean up Revit family parameters before proceeding to schematic cost estimation.*
    """)

# Set page configuration
st.set_page_config(page_title="BIM Budget Guard", page_icon="🏗️", layout="wide")

st.title("🏗️ BIM Budget Guard")
st.markdown("""
Upload an early-stage Revit schedule (CSV) to identify missing data, volume anomalies, and potential budget risks.
""")

uploaded_file = st.file_uploader("Upload Revit Schedule (CSV)", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        st.header("1. Deterministic Risk Dashboard")
        
        missing_material = df[df['Material'].isna() | (df['Material'] == '') | (df['Material'] == 'None')]
        zero_volume = df[df['Volume_m3'] == 0]
        missing_cost = df[df['Unit_Cost_USD'].isna()]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Elements", len(df))
        col2.metric("Missing Materials", len(missing_material))
        col3.metric("Zero Volume Entries", len(zero_volume))
        col4.metric("Missing Unit Costs", len(missing_cost))
        
        st.subheader("Risk Details")
        tab1, tab2, tab3, tab4 = st.tabs(["Missing Materials", "Zero Volumes", "Missing Costs", "Raw Data"])
        
        with tab1:
            st.dataframe(missing_material[['Element_ID', 'Category', 'Family_and_Type', 'Volume_m3']])
        with tab2:
            st.dataframe(zero_volume[['Element_ID', 'Category', 'Family_and_Type', 'Material']])
        with tab3:
            st.dataframe(missing_cost[['Element_ID', 'Category', 'Material', 'Volume_m3']])
        with tab4:
            st.dataframe(df)

        st.header("2. AI Agent Analysis")
        st.markdown("Run the AI Quantity Surveyor agent to generate a professional audit report based on these anomalies.")
        
        if st.button("Generate AI Risk Audit"):
            api_key = os.getenv("ANTHROPIC_API_KEY")
            
            with st.spinner("AI Quantity Surveyor is analyzing the schedule..."):
                if api_key and api_key != "your_key_here" and HAS_ANTHROPIC:
                    try:
                        client = Anthropic(api_key=api_key)
                        prompt = f"""
                        You are an expert AI Quantity Surveyor and Architect. 
                        Analyze this summary of a Revit BIM schedule and provide a short, professional risk audit.
                        
                        Total Elements: {len(df)}
                        Missing Material Entries: {len(missing_material)}
                        Zero Volume Entries: {len(zero_volume)}
                        Missing Unit Costs: {len(missing_cost)}
                        
                        Identify the top 3 architectural or budgeting risks based on these numbers. 
                        Keep it concise, professional, and actionable for a BIM manager.
                        """
                        response = client.messages.create(
                            model="claude-3-haiku-20240307",
                            max_tokens=400,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        st.success("Analysis Complete (Live Claude AI)")
                        st.write(response.content[0].text)
                    except Exception as ai_err:
                        st.warning(f"Live API call failed ({ai_err}). Displaying simulated professional audit.")
                        show_mock_audit(len(df), len(missing_material), len(zero_volume), len(missing_cost))
                else:
                    import time
                    time.sleep(1)
                    st.success("Analysis Complete (AI Agent Simulation)")
                    st.markdown(f"""
                    ### 🔍 Executive Quantity Surveyor Audit Report
                    
                    **Project Risk Rating:** 🟠 **HIGH RISK (Early-Stage Volatility)**
                    
                    Based on the preliminary schedule export containing **{len(df)} elements**, the automated AI agent has identified critical information gaps that pose immediate cost exposure risks:
                    
                    1. **Material Specification Deficit ({len(missing_material)} items affected):** A significant portion of structural and partition elements lack assigned material parameters. In early estimation, unassigned specifications typically result in fallback pricing defaults that underestimate actual material grade requirements by 15–22%.
                    2. **Zero-Volume Geometry Anomalies ({len(zero_volume)} elements):** Several elements register $0.00\text{{ m}}^3$ in volume despite active family instances. This indicates unjoined geometry or incomplete family parameter mapping in Revit, which will corrupt total bill of quantities (BoQ) aggregations.
                    3. **Cost Baseline Exposure ({len(missing_cost)} items missing unit costs):** With baseline pricing absent across key categories, cost estimation relies entirely on speculative averages. 
                    
                    **Actionable Recommendations for BIM Coordinator:**
                    * Audit family parameters prior to schematic design freeze.
                    * Enforce material property compliance filters within Revit templates.
                    * Re-run BIM Budget Guard after geometry cleanup.
                    """)

    except Exception as e:
        st.error(f"Error reading the file: {e}")
else:
    st.info("Awaiting file upload...")