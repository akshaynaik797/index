from waitress import serve
import inamdar_app
import logging

logging.basicConfig(filename="error.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

logger = logging.getLogger('waitress')

serve(inamdar_app.app, host='0.0.0.0', port=10000)
