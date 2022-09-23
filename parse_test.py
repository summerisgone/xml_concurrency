import os
import stat
import unittest

from parse import main, read_archive, ArchiveResult


class FileSystemTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.levels_test_csv = 'levels_test.csv'
        f = open(self.levels_test_csv, 'w')
        f.close()
        f = open('sample.zip', 'w')
        f.close()

    def tearDown(self) -> None:
        os.remove(self.levels_test_csv)
        os.remove('sample.zip')

    def test_open_error(self):
        os.chmod(self.levels_test_csv, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        code, msg = main('.', None, self.levels_test_csv, 'objects_test.csv')
        self.assertEqual(1, code)
        self.assertEqual("[Errno 13] Permission denied: 'levels_test.csv'", msg)


class FixturesTestCase(unittest.TestCase):

    def test_100_files_archive(self):
        arch_result = read_archive('./fixtures/archive_100_xml.zip')
        self.assertEqual(100, len(arch_result.xml_results))
        self.assertEqual(ArchiveResult.STATUS_SUCCESS, arch_result.status)

    def test_bad_xml(self):
        arch_result = read_archive('fixtures/archive_bad_xml.zip')
        self.assertEqual(2, len(arch_result.xml_results))
        self.assertEqual(ArchiveResult.STATUS_PARTIAL, arch_result.status)

    def test_bad_zip(self):
        arch_result = read_archive('fixtures/archive_0bytes.zip')
        self.assertEqual(ArchiveResult.STATUS_ERROR, arch_result.status)


if __name__ == '__main__':
    unittest.main()
