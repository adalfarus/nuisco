# Global variable to hold the log function
log = None

def init(logger):
    global log
    log = logger.log
