import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import time

# Page configuration with custom theme
st.set_page_config(
    page_title="DataCleaner Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1rem;
    }
    .info-box {
        padding: 1rem;
        background-color: #E3F2FD;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for app navigation
with st.sidebar:
    st.image("icon.png", width=80)
    st.markdown("<h2 style='text-align: center;'>DataCleaner Pro</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Navigation")
    app_mode = st.radio("", ["File Upload", "About"])
    
    st.markdown("---")
    st.markdown("### Help")
    with st.expander("How to use"):
        st.write("""
        1. Upload CSV or Excel files
        2. Preview your data
        3. Clean and transform as needed
        4. Export to your desired format
        """)
    
    st.markdown("---")
    st.caption("© 2025 DataCleaner Pro | v1.0.0")

# Main content
if app_mode == "About":
    st.markdown("<h1 class='main-header'>About DataCleaner Pro</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
    <p>DataCleaner Pro is a powerful tool for data cleaning, transformation, and format conversion. 
    Quickly clean messy datasets and convert between CSV and Excel formats with a professional interface.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Key Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- ✅ Handle multiple file uploads")
        st.markdown("- ✅ Preview data instantly")
        st.markdown("- ✅ Smart missing value handling")
    with col2:
        st.markdown("- ✅ Column selection and filtering")
        st.markdown("- ✅ Data visualization")
        st.markdown("- ✅ Format conversion (CSV/Excel)")

else:  # File Upload mode
    st.markdown("<h1 class='main-header'>File Converter & Data Cleaner</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
    Upload your CSV and Excel files to clean data and convert formats efficiently.
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader with clear instructions
    files = st.file_uploader(
        "Drag and drop files here or click to browse",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        help="Upload CSV or Excel files to begin processing"
    )

    if not files:
        # Show placeholder when no files are uploaded
        st.info("Please upload one or more CSV or Excel files to get started")
        
        # Display sample data for demonstration
        with st.expander("See example data"):
            sample_data = pd.DataFrame({
                'Name': ['John', 'Anna', 'Peter', 'Linda'],
                'Age': [28, 34, np.nan, 32],
                'City': ['New York', 'Paris', 'Berlin', np.nan],
                'Salary': [75000, 82000, 67000, np.nan]
            })
            st.dataframe(sample_data, use_container_width=True)
    else:
        # Process each uploaded file
        for file in files:
            # Create a container for each file to improve organization
            with st.container():
                st.markdown(f"<h2 class='sub-header'>📄 {file.name}</h2>", unsafe_allow_html=True)
                
                # File type detection with progress indicator
                with st.spinner("Reading file..."):
                    ext = file.name.split(".")[-1].lower()
                    try:
                        if ext == "csv":
                            df = pd.read_csv(file)
                        elif ext == "xlsx":
                            df = pd.read_excel(file)
                        else:
                            st.error(f"Unsupported file format: {ext}")
                            continue
                    except Exception as e:
                        st.error(f"Error reading file: {str(e)}")
                        continue
                
                # File stats
                col1, col2, col3 = st.columns(3)
                col1.metric("Rows", f"{df.shape[0]:,}")
                col2.metric("Columns", f"{df.shape[1]:,}")
                col3.metric("Missing Values", f"{df.isna().sum().sum():,}")
                
                # Data preview tab
                tab1, tab2, tab3 = st.tabs(["📊 Preview", "🧹 Clean & Transform", "💾 Export"])
                
                with tab1:
                    st.dataframe(df.head(10), use_container_width=True)
                    with st.expander("Data Summary"):
                        st.write("#### Numeric Columns")
                        st.dataframe(df.describe(), use_container_width=True)
                        
                        st.write("#### Non-numeric Columns")
                        if not df.select_dtypes(exclude="number").empty:
                            st.dataframe(df.describe(include=["object"]), use_container_width=True)
                        else:
                            st.info("No non-numeric columns found")
                
                with tab2:
                    st.subheader("Data Cleaning Options")
                    
                    # Column selection with better UI
                    with st.expander("Select Columns", expanded=True):
                        all_cols = st.checkbox("Select All Columns", value=True)
                        if all_cols:
                            selected_columns = df.columns.tolist()
                        else:
                            selected_columns = st.multiselect(
                                "Choose specific columns to keep",
                                options=df.columns.tolist(),
                                default=df.columns.tolist()
                            )
                        
                        if selected_columns:
                            df = df[selected_columns]
                            st.success(f"Selected {len(selected_columns)} columns")
                    
                    # Missing values handling with multiple options
                    with st.expander("Handle Missing Values"):
                        missing_option = st.radio(
                            "Choose method:",
                            ["No change", "Fill with mean/mode", "Fill with specific value", "Drop rows with missing values"]
                        )
                        
                        if missing_option == "Fill with mean/mode":
                            if st.button("Apply Mean/Mode Fill"):
                                with st.spinner("Filling missing values..."):
                                    # Fill numeric with mean, categorical with mode
                                    for col in df.columns:
                                        if pd.api.types.is_numeric_dtype(df[col]):
                                            df[col].fillna(df[col].mean(), inplace=True)
                                        else:
                                            df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "", inplace=True)
                                    st.success("Missing values filled with mean/mode")
                                    
                        elif missing_option == "Fill with specific value":
                            fill_value = st.text_input("Value to fill missing data with:", "0")
                            if st.button("Apply Fill"):
                                with st.spinner("Filling missing values..."):
                                    df.fillna(fill_value, inplace=True)
                                    st.success(f"Missing values filled with '{fill_value}'")
                                    
                        elif missing_option == "Drop rows with missing values":
                            if st.button("Drop Missing"):
                                original_count = len(df)
                                df.dropna(inplace=True)
                                st.success(f"Dropped {original_count - len(df)} rows with missing values")
                    
                    # Additional data transformations
                    with st.expander("Additional Transformations"):
                        # Remove duplicates
                        if st.checkbox("Remove duplicate rows"):
                            original_count = len(df)
                            df.drop_duplicates(inplace=True)
                            st.success(f"Removed {original_count - len(df)} duplicate rows")
                        
                        # Handle outliers in numeric columns
                        if st.checkbox("Handle outliers (numeric columns)"):
                            outlier_cols = st.multiselect(
                                "Select columns for outlier handling",
                                options=df.select_dtypes(include="number").columns.tolist()
                            )
                            if outlier_cols and st.button("Remove Outliers"):
                                with st.spinner("Processing outliers..."):
                                    for col in outlier_cols:
                                        Q1 = df[col].quantile(0.25)
                                        Q3 = df[col].quantile(0.75)
                                        IQR = Q3 - Q1
                                        lower_bound = Q1 - 1.5 * IQR
                                        upper_bound = Q3 + 1.5 * IQR
                                        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                                    st.success(f"Outliers removed. Remaining rows: {len(df)}")
                        
                        # Data type conversion
                        if st.checkbox("Convert column types"):
                            col_to_convert = st.selectbox("Select column to convert", df.columns.tolist())
                            new_type = st.selectbox("Convert to", ["string", "float", "integer", "datetime"])
                            
                            if st.button("Convert Type"):
                                with st.spinner(f"Converting {col_to_convert} to {new_type}..."):
                                    try:
                                        if new_type == "string":
                                            df[col_to_convert] = df[col_to_convert].astype(str)
                                        elif new_type == "float":
                                            df[col_to_convert] = pd.to_numeric(df[col_to_convert], errors='coerce')
                                        elif new_type == "integer":
                                            df[col_to_convert] = pd.to_numeric(df[col_to_convert], errors='coerce').astype('Int64')
                                        elif new_type == "datetime":
                                            df[col_to_convert] = pd.to_datetime(df[col_to_convert], errors='coerce')
                                        st.success(f"Converted {col_to_convert} to {new_type}")
                                    except Exception as e:
                                        st.error(f"Conversion failed: {str(e)}")
                    
                    # Preview of cleaned data
                    st.subheader("Preview of Cleaned Data")
                    st.dataframe(df.head(10), use_container_width=True)
                
                # Export options
                with tab3:
                    st.subheader("Visualization")
                    if not df.select_dtypes(include="number").empty:
                        chart_type = st.radio("Chart Type", ["Bar", "Line", "Area"], horizontal=True)
                        num_cols = df.select_dtypes(include="number").columns.tolist()
                        if len(num_cols) >= 2:
                            x_axis = st.selectbox("X-axis", num_cols)
                            y_axis = st.selectbox("Y-axis", [col for col in num_cols if col != x_axis])
                            
                            chart_data = df.head(50)
                            if chart_type == "Bar":
                                st.bar_chart(chart_data, x=x_axis, y=y_axis)
                            elif chart_type == "Line":
                                st.line_chart(chart_data, x=x_axis, y=y_axis)
                            else:
                                st.area_chart(chart_data, x=x_axis, y=y_axis)
                        else:
                            st.warning("Need at least 2 numeric columns for visualization")
                    else:
                        st.warning("No numeric columns available for visualization")
                    
                    st.subheader("Export Options")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        format_choice = st.radio("Export Format:", ["CSV", "Excel"], horizontal=True)
                        include_index = st.checkbox("Include row index", value=False)
                        
                    with col2:
                        new_filename = st.text_input(
                            "Output filename (without extension):",
                            value=file.name.split(".")[0] + "_cleaned"
                        )
                    
                    if st.button("⬇️ Export File", type="primary"):
                        with st.spinner("Preparing file for download..."):
                            try:
                                output = BytesIO()
                                if format_choice == "CSV":
                                    df.to_csv(output, index=include_index)
                                    mime = "text/csv"
                                    file_ext = "csv"
                                else:
                                    df.to_excel(output, index=include_index)
                                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    file_ext = "xlsx"
                                
                                output.seek(0)
                                download_name = f"{new_filename}.{file_ext}"
                                
                                st.download_button(
                                    label=f"📥 Download {download_name}",
                                    data=output,
                                    file_name=download_name,
                                    mime=mime,
                                    key=f"download_{file.name}",
                                )
                                st.success("File ready for download!")
                            except Exception as e:
                                st.error(f"Export failed: {str(e)}")
                
                st.markdown("---")