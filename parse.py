import argparse
import sys
import xml.etree.ElementTree as ET
from concurrent.futures.process import ProcessPoolExecutor, BrokenProcessPool
from glob import glob
from os.path import join
from typing import IO, Optional, List, Tuple
from xml.etree.ElementTree import ParseError
from zipfile import ZipFile, BadZipFile
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())


class ArchiveResult:
    STATUS_ERROR = 'error'
    STATUS_PARTIAL = 'partial'
    STATUS_SUCCESS = 'success'

    def __init__(self, filename, status=None):
        self.filename = filename
        self.status = status
        self.xml_results = []
        self.errors = []


class XMLResult:
    object_ids: List[str]

    def __init__(self, filename: str):
        self.filename = filename
        self.file_id = None
        self.file_level = None
        self.object_ids = []

    @property
    def is_valid(self):
        return all((self.file_id, self.file_level, self.object_ids))


def write_stats(level_stats: IO, object_stats: IO, file_id: str, file_level: str, object_ids: List[str]):
    level_stats.write(f'{file_id};{file_level}\n')
    for object_id in object_ids:
        object_stats.write(f'{file_id};{object_id}\n')


def read_dir(pathname: str, cpu: Optional[int] = None):
    with ProcessPoolExecutor(max_workers=cpu) as executor:
        yield from executor.map(read_archive, glob(join(pathname, '*.zip')))


def read_archive(zip_filename: str):
    try:
        archive = ZipFile(zip_filename, 'r')
    except PermissionError as e:
        ar = ArchiveResult(zip_filename, status=ArchiveResult.STATUS_ERROR)
        ar.errors.append(str(e))
        return ar
    except BadZipFile as e:
        ar = ArchiveResult(zip_filename, status=ArchiveResult.STATUS_ERROR)
        ar.errors.append(str(e))
        return ar
    else:
        archive_result = ArchiveResult(zip_filename, status=ArchiveResult.STATUS_SUCCESS)
        for filename in archive.namelist():
            xml_file_result = XMLResult(filename)
            with archive.open(filename) as xml_file:
                try:
                    root = ET.fromstring(xml_file.read())
                    xml_file_result.file_id = root.find(".//var[@name='id']").get('value')  # type: ignore
                    xml_file_result.file_level = root.find(".//var[@name='level']").get('value')  # type: ignore
                    xml_file_result.object_ids = [o.get("name") for o in root.iterfind(".//object")]  # type: ignore
                except ParseError:
                    archive_result.status = ArchiveResult.STATUS_PARTIAL
                    archive_result.errors.append(
                        f'XML Parse error at {archive_result.filename}/{xml_file_result.filename}')
                else:
                    if xml_file_result.is_valid:
                        archive_result.xml_results.append(xml_file_result)
                    else:
                        archive_result.errors.append(
                            f'Unexpected XML file at {archive_result.filename}/{xml_file_result.filename}')
        return archive_result


def main(work_dir, cpu_count=None, levels_filename='levels.csv', objects_filename='objects.csv') -> Tuple[int, str]:
    archives_list = glob(join(work_dir, '*.zip'))
    if not len(archives_list):
        return 1, 'No archives found'
    logger.debug("%s archives found", len(archives_list))
    try:
        errors = []
        with open(levels_filename, 'w') as level_stats, open(objects_filename, 'w') as object_stats:
            try:
                for archive_result in read_dir(work_dir, cpu_count):
                    if archive_result.status == ArchiveResult.STATUS_SUCCESS:
                        logger.debug("Reading %s: OK", archive_result.filename)
                    if archive_result.status != ArchiveResult.STATUS_SUCCESS:
                        logger.debug("Reading %s: has errors", archive_result.filename)
                        errors += archive_result.errors
                    for xml_file_result in archive_result.xml_results:
                        write_stats(
                            level_stats,
                            object_stats,
                            xml_file_result.file_id,
                            xml_file_result.file_level,
                            xml_file_result.object_ids,
                        )
                logger.debug('Level stats written to %s', levels_filename)
                logger.debug('Object stats written to %s', objects_filename)
            except BrokenProcessPool as e:
                return 1, f'Runtime error: {str(e)}'
        return 0, '\n'.join(errors)
    except OSError as e:
        return 1, str(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate zip archives with xml files.')
    parser.add_argument('path', type=str, nargs='?', default='.', help='Where to look archives')
    parser.add_argument('--cpu', type=int, default=None, help='Number of CPU cores to run on')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbose logging')
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    ret_code, message = main(args.path, args.cpu)
    if ret_code != 0:
        sys.stderr.write(message)
        sys.exit(ret_code)
    elif message:
        sys.stderr.write('Errors during parsing:\n')
        sys.stderr.write(message)
