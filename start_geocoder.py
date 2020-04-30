from final_project.app import server
from final_project.db_utils.db_worker import DbWorker


if __name__ == '__main__':
    DbWorker.create_db()
    server.run()
