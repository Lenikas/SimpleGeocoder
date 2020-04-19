from geocoder.db_worker import DbWorker
from geocoder.app import server


def run_server():
    server.run(debug=True)


if __name__ == '__main__':
    #DbWorker.create_db()
    run_server()
