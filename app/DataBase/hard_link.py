import binascii
import os.path
import sqlite3
import threading
import xml.etree.ElementTree as ET

from app.log import log

lock = threading.Lock()
DB = None
cursor = None
db_path = "./app/Database/Msg/HardLinkImage.db"
root_path = 'FileStorage/MsgAttach/'
if os.path.exists(db_path):
    DB = sqlite3.connect(db_path, check_same_thread=False)
    # '''创建游标'''
    cursor = DB.cursor()


def init_database():
    global DB
    global cursor
    if not DB:
        if os.path.exists(db_path):
            DB = sqlite3.connect(db_path, check_same_thread=False)
            # '''创建游标'''
            cursor = DB.cursor()


def get_image_by_md5(md5: bytes):
    sql = '''
        select Md5Hash,MD5,FileName,HardLinkImageID.Dir as DirName1,HardLinkImageID2.Dir as DirName2
        from HardLinkImageAttribute
        join HardLinkImageID on HardLinkImageAttribute.DirID1 = HardLinkImageID.DirID
        join HardLinkImageID as HardLinkImageID2 on HardLinkImageAttribute.DirID2 = HardLinkImageID2.DirID
        where MD5 = ?;
        '''
    try:
        lock.acquire(True)
        try:
            cursor.execute(sql, [md5])
        except AttributeError:
            init_database()
        finally:
            cursor.execute(sql, [md5])
        result = cursor.fetchone()
        return result
    finally:
        lock.release()


def get_md5_from_xml(content):
    # 解析XML
    root = ET.fromstring(content)
    # 提取md5的值
    md5_value = root.find(".//img").get("md5")
    # print(md5_value)
    return md5_value


@log
def get_image(content, thumb=False):
    md5 = get_md5_from_xml(content)
    result = get_image_by_md5(binascii.unhexlify(md5))
    if result:
        # print(result)
        dir1 = result[3]
        dir2 = result[4]
        data_image = result[2]
        dir0 = 'Thumb' if thumb else 'Image'
        dat_image = os.path.join(root_path, dir1, dir0, dir2, data_image)
        return dat_image


def close():
    if DB:
        DB.close()


# 6b02292eecea118f06be3a5b20075afc_t

if __name__ == '__main__':
    msg_root_path = './Msg/'
    db_path = "./Msg/HardLinkImage.db"
    init_database()
    content = '''<?xml version="1.0"?><msg>\n\t<img aeskey="bc37a58c32cb203ee9ac587b068e5853" encryver="1" cdnthumbaeskey="bc37a58c32cb203ee9ac587b068e5853" cdnthumburl="3057020100044b30490201000204d181705002032f5405020428a7b4de02046537869d042462313532363539632d663930622d343463302d616636662d333837646434633061626534020401150a020201000405004c4c6d00" cdnthumblength="3097" cdnthumbheight="120" cdnthumbwidth="68" cdnmidheight="0" cdnmidwidth="0" cdnhdheight="0" cdnhdwidth="0" cdnmidimgurl="3057020100044b30490201000204d181705002032f5405020428a7b4de02046537869d042462313532363539632d663930622d343463302d616636662d333837646434633061626534020401150a020201000405004c4c6d00" length="57667" md5="6844b812d5d514eb6878657e0bf4cdbb" originsourcemd5="1dfdfa24922270ea1cb5daba103f45ca" />\n\t<platform_signature></platform_signature>\n\t<imgdatahash></imgdatahash>\n</msg>\n'''
    print(get_image(content))
    print(get_image(content, thumb=False))
    result = get_md5_from_xml(content)
    print(result)
