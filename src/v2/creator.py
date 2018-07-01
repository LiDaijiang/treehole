import MySQLdb
import os


def main(event):
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT")
    user = os.environ.get("DB_USER")
    passwd = os.environ.get("DB_PASSWD")
    db = os.environ.get("DB")
    conn = MySQLdb.connect(host=host, port=int(port), user=user, passwd=passwd, db=db)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE `secret_record` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
`msg_file_id` varchar(128) NOT NULL DEFAULT '' COMMENT '录音未见id',
`xiaomi_id` int(11) unsigned NOT NULL DEFAULT 0 COMMENT '小米id',
`session_id` varchar(128) NOT NULL DEFAULT '' COMMENT '会话id',
PRIMARY KEY (`id`))
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;""")
    conn.commit()
    cursor.close()
    conn.close()