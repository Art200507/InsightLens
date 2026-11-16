# InsightLens web application

The shipped UI is `data_upload_app.py`, a Streamlit application. The old `vercel.json` references a missing React `package.json`; it cannot deploy this Python UI as a static Vercel site. Use a container host or Streamlit hosting instead.

`requirements-web.txt` includes the previously missing Streamlit dependency and excludes unrelated offline-training packages. Build with `docker build -f Dockerfile.web -t insightlens .`; run with `docker run --rm -p 8501:8501 insightlens`. The image copies only the application, not repository datasets. This setup is prepared but has not been deployed or browser-tested.
