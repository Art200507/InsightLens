#!/bin/bash

echo "🚀 Starting InsightLens Web App..."
echo "======================================"
echo ""
echo "📊 Features:"
echo "  • Upload any CSV file"
echo "  • Smart column detection"
echo "  • Automatic analysis"
echo "  • Interactive visualizations"
echo "  • Download results"
echo ""
echo "🌐 Web app will open in your browser automatically"
echo "📱 Access from: http://localhost:8501"
echo ""
echo "💡 To stop the app: Press Ctrl+C"
echo ""

# Activate virtual environment and run Streamlit
source insightlens_env/bin/activate
streamlit run data_upload_app.py --server.port 8501 --browser.gatherUsageStats false