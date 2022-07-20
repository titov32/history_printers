import qrcode
from config import DOMAIN_NAME


def make_qr_code_by_path(path_to_printer_in_qr, name):
    text = f'{DOMAIN_NAME}{path_to_printer_in_qr}'
    img = qrcode.make(text)
    file_name = f'static/qr/{name}.png'
    img.save(file_name)
    url = f'http://{DOMAIN_NAME}/{file_name}'
    return url
