# Proceedings generator
# PH june 2014
PROC_FOLDER = SGE2014_proceedings
CHAIR_FOLDER = chairman\ package

### TODO: add compilation directives

### Upload webpages to remote server
push:
	rsync -avd $(PROC_FOLDER)/ sgeconf:www/actes/2014
#	rsync -avd $(CHAIR_FOLDER)/ sgeconf:www/actes/2014/chair
