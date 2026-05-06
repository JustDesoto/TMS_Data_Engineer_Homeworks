#  docker run -d --name clickhouse-server `                                                            
# >>   --restart unless-stopped `
# >>   -p 8123:8123 `
# >>   -p 9000:9000 `
# >>   -e CLICKHOUSE_USER=default `
# >>   -e CLICKHOUSE_PASSWORD= `
# >>   -e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1 `
# >>   clickhouse/clickhouse-server:latest



# Библиотека: clickhouse-connect

import clickhouse_connect


client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='',
    database='default'
)

query = "SELECT name, database, engine FROM system.tables LIMIT 10"

result = client.query(query)

print("Result:")
for row in result.result_rows:
    print(row)
