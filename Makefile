default: build

run: 
	docker run --restart=always --name wiki-cc0-scraper -it \
		-v ${PWD}/data/:/data \
	techiaith/wiki-cc0-scraper bash

build:
	docker build --rm -t techiaith/wiki-cc0-scraper .

clean:
	docker rmi techiaith/wiki-cc0-scraper
	
stop:
	docker stop wiki-cc0-scraper
	docker rm wiki-cc0-scraper

