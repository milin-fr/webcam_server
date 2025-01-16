FROM python:3.11

WORKDIR /work_dir

ADD . /work_dir

RUN pip install -r requirements.txt -U

ENTRYPOINT ["sh", "start_scripts.sh"]