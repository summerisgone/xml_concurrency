import argparse
import io
import random
from uuid import uuid4
from zipfile import ZipFile


def generate_files(zip_count: int, xml_count: int) -> None:
    for i in range(zip_count):
        with ZipFile(f'archive_{i}.zip', 'w') as archive:
            for j in range(xml_count):
                with archive.open(f'xml_{j}.xml', 'w') as xml_file:
                    xml_file.write(generate_xml())


def generate_xml() -> bytes:
    """
    <root>
    <var name="id" value="<случайное уникальное строковое значение>"/>
    <var name="level" value="<случайное число от 1 до 100>"/>
    <objects>
        <object name="<случайное строковое значение>"/>
        <object name="<случайное строковое значение>"/>
    </objects>
    </root>
    :return:
    """
    output = io.StringIO()
    data = dict(id=str(uuid4()), level=random.randint(1, 100), objects=[str(uuid4()) for _ in range(1, 10)])
    output.write(f'''<root><var name="id" value="{data['id']}"/><var name="level" value="{data['level']}"/>
    <objects>
    ''')
    for item in data['objects']:  # type: ignore
        output.write(f'<object name="{item}"/>\n')
    output.write("</objects></root>")
    return output.getvalue().encode('utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate zip archives with xml files.')
    parser.add_argument('--zip', type=int, default=50, help='Amount of Zip archives')
    parser.add_argument('--xml', type=int, default=100, help='Amount of XML files in the archive')
    args = parser.parse_args()
    generate_files(args.zip, args.xml)
