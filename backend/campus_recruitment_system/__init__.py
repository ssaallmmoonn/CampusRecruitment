import pymysql
pymysql.install_as_MySQLdb()

# Monkey patch to satisfy Django's mysqlclient version check
import MySQLdb
if not hasattr(MySQLdb, 'version_info') or MySQLdb.version_info < (2, 2, 1):
    MySQLdb.version_info = (2, 2, 1, 'final', 0)
