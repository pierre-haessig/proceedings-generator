# Proceedings generator
# PH june 2014
PROC_FOLDER = SGE2014_proceedings
CHAIR_FOLDER = chairman\ package

### TODO: add compilation directives

### Upload webpages to remote server
push:
	rsync -avd $(PROC_FOLDER)/ eole:www/SGE2014
	rsync -avd $(CHAIR_FOLDER)/ eole:www/SGE2014/chair
