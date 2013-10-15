from django.db import connection, transaction


def execute(query):
    cursor = connection.cursor()

    cursor.execute(query)
    transaction.commit_unless_managed()


def newest_files(query):
    sql = """
        SELECT
            id,
            name,
            revision_id,
            mimetype,
            change_type,
            copy_of_id
        FROM (
            SELECT
                id,
                name,
                revision_id,
                mimetype,
                change_type,
                copy_of_id,
                group_concat(change_type, '') AS change_history
            FROM
                ( %s )
            WHERE
                change_type IS NOT NULL GROUP BY name
        ) WHERE
            change_history NOT LIKE 'D%%'
    """ % query

    return sql.replace("%", "%%")

def mimetype_count(files):
    return """
        SELECT
            id,
            name,
            revision_id,
            mimetype,
            change_type,
            copy_of_id,
            COUNT(mimetype) AS count
        FROM
            ( %s )
        WHERE
            mimetype IS NOT NULL
        GROUP BY
            mimetype
    """ % files

def count_entries(query):
    return """
        SELECT
            id,
            COUNT(*) AS count
        FROM
            ( %s )
    """ % query

def delete(cls, query):
    return """
        DELETE FROM %s WHERE id IN ( %s )
    """ % (cls._meta.db_table, query)
