FROM python:3.8-slim
RUN pip3 install pyyaml
COPY entrypoint.sh yml2image.py /
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh
