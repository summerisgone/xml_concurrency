import typing
import xml.etree.ElementTree as ET
from glob import glob
from os.path import join

from zipfile import ZipFile


def write_stats(level_stats: typing.IO, object_stats: typing.IO, file_id: str, file_level: str, object_ids: list[str]):
    level_stats.write(f'{file_id};{file_level}\n')
    for object_id in object_ids:
        object_stats.write(f'{file_id};{object_id}\n')


def read_archives(pathname: str = '.'):
    for zip_filename in glob(join(pathname, '*.zip')):
        with ZipFile(zip_filename, 'r') as archive:
            for filename in archive.namelist():
                with archive.open(filename) as xml_file:
                    root = ET.fromstring(xml_file.read())
                    file_id = root.find(".//var[@name='id']").get('value')
                    file_level = root.find(".//var[@name='level']").get('value')
                    object_ids = [o.get("name") for o in root.iterfind(".//object")]
                    yield file_id, file_level, object_ids


if __name__ == '__main__':
    with open('levels.csv', 'w') as level_stats, open('objects.csv', 'w') as object_stats:
        for file_id, file_level, object_ids in read_archives():
            write_stats(level_stats, object_stats, file_id, file_level, object_ids)