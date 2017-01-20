FROM debian:jessie-slim
MAINTAINER Niranjan Rajendran <niranjan94@yahoo.com>

RUN apt-get clean -y && apt-get update -y
RUN apt-get install -y curl apt-transport-https
RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk-jessie main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update -y && apt-get install -y google-cloud-sdk && apt-get autoremove -y
RUN apt-get clean -y

CMD gcloud info
