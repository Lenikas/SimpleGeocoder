from final_project.db_worker import DbWorker
from final_project.app import server


if __name__ == '__main__':
    DbWorker.create_db()
    #server.run()
