from geocoder.db_worker import DbWorker
from geocoder.app import server


if __name__ == '__main__':
    DbWorker.create_db()
    #server.run()
