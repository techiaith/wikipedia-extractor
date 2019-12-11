FROM ubuntu:16.04

#
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
	curl vim locales build-essential unixodbc-dev \
	python3 python3-pip python3-setuptools python3-dev libxml2-dev \
	apt-transport-https ca-certificates && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8

#
RUN mkdir -p /opt/wiki-cc0-scraper
ADD python/* /opt/wiki-cc0-scraper/

WORKDIR /opt/wiki-cc0-scraper
RUN pip3 install -r requirements.txt
RUN python3 -m nltk.downloader punkt
 
