import pymysql.cursors

config = {
    'host': '10.161.100.11',
    'user': 'bct_write',
    'password': 'bcwriter22',
    'database': 'better_call_test',
    'charset': 'utf8',
}

try:
    connection = pymysql.connect(**config, cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        sql = """
            SELECT
                SUM(pdp_total_horas) AS totalproducaohora
            FROM
                planos_de_producao
            WHERE
                DAY(pdp_data) = DAY(NOW())
                AND MONTH(pdp_data) = MONTH(NOW())
                AND YEAR(pdp_data) = YEAR(NOW());
        """
        cursor.execute(sql)

        result = cursor.fetchone()

        print("Total de hora de produção:", result['totalproducaohora'])

finally:
    connection.close()
