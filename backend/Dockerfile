FROM python:3.11-slim

# Install system libraries required by opencv-python-headless and mediapipe.
# libgl1            → provides libGL.so.1 (fixes: ImportError: libGL.so.1: cannot open shared object file)
# libglib2.0-0      → provides libgthread/glib runtime used by OpenCV internals
# libgomp1          → OpenMP runtime required by mediapipe and numpy native extensions
# libsm6 libxext6   → minimal X11/ICE stubs that some OpenCV codecs expect even in headless mode
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
        libsm6 \
        libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
