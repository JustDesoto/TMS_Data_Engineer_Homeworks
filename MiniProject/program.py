from database_service.database_connector import database_connect
from database_service.database_export import database_export
from analytic_service.run_tasks import run_all_tasks
from logger_service.logger import safe
import config

@safe
def main():
    connection = database_connect(config.DB_PATH) # Получаем connection к базе
    database_export(connection, config.DATA_EXPORT_FOLDER) # Делаем экспорт данных
    run_all_tasks(connection, config.TASK_EXPORT_FOLDER, config.DATA_EXPORT_FOLDER) # Запускаем все аналитические таски


if __name__ == "__main__":
    main()
