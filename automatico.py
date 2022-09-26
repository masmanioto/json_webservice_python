import argparse
import json
import os
import pathlib
import re
import requests

CURRENT_DIR = pathlib.Path().absolute()
PROCESSED_FILES_MARK = 'processado'

HOST = 'http://localhost:5000'
ENDPOINT = '/api/fardo'
TOKEN = 'testedesistema'
HTTP_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


def get_json_files_from_folder(folder_path):
    json_files = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if len(re.compile('.json$', re.IGNORECASE).findall(file)) > 0
    ]
    return json_files


def mark_file_as_processed(file_path, mark=PROCESSED_FILES_MARK):
    os.rename(file_path, f'{file_path}.{mark}')


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as json_file:
        data = json.load(json_file)
        json_file.close()
    return data


def send_to_api(file_path):
    json_data = read_json(file_path)
    total = len(json_data)

    print(f'Sending {len(json_data)} entries - {file}')

    for i, item in enumerate(json_data):
        print(f'Sending {i + 1}/{total}')

        progress = f'{i + 1}/{total}'
        name = item.get('id', item.get('cod_barras', progress))
        percent = round((((i + 1) * 100) / total), 2)

        print(f'Sending {name} {progress} ({percent}%) - {file}')

        res = requests.post(
            data=json.dumps(item),
            headers={
                **HTTP_HEADERS,
                'Authorization': f'Bearer {TOKEN}'
            },
            url=f'{HOST}/{ENDPOINT}'
        )

        print(f'Res => [{progress}] {name}: {res.status_code}')
        try:
            print(json.dumps(res.json(), indent=4))
        except:
            pass


def is_pointing_to_current_folder(raw_path):
    if raw_path == '.':
        return True
    if raw_path == './':
        return True
    if raw_path == '':
        return True


def sanitize_raw_path(raw_path):
    return raw_path.replace('./', '')


parser = argparse.ArgumentParser()
parser.add_argument('--endpoint', default='/api/fardo')
parser.add_argument('--files', default='.')
parser.add_argument('--host', default='http://localhost:5000')
parser.add_argument('--token', default='testedesistema')

if __name__ == '__main__':
    args = parser.parse_args()

    ENDPOINT = args.endpoint
    HOST = args.host
    TOKEN = args.token

    raw_folder_path = args.files

    folder_path = ''
    if is_pointing_to_current_folder(raw_folder_path):
        folder_path = ''
    else:
        folder_path = sanitize_raw_path(raw_folder_path)

    files_folder_path = os.path.join(CURRENT_DIR, folder_path)
    files = get_json_files_from_folder(files_folder_path)

    for i, file in enumerate(files):
        print(f'\nFile {i + 1} of {len(files)} ...START!')
        send_to_api(file)
        mark_file_as_processed(file)
        print(f'File {i + 1} of {len(files)} ...DONE\n')
