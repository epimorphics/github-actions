FROM python:3.8-slim
RUN pip3 install pyyaml
COPY yml2image.py /yml2image.py 
ENTRYPOINT ["python3", "/yml2image.py | tee -a $GITHUB_OUTPUT"]
