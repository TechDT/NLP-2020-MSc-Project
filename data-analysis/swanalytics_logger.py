import logging

handler = logging.FileHandler('swanalytics.log', mode='a')
formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
handler.setFormatter(formatter)

swanalytics_logger = logging.getLogger('swanalytics')
swanalytics_logger.setLevel(logging.INFO)
swanalytics_logger.addHandler(handler)

def get_sw_logger():
    return swanalytics_logger