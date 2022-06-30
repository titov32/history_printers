import qrcode
from config import DOMAIN_NAME


def make_qr_code_by_path(path, name):
    text = f'{DOMAIN_NAME}{path}'
    img = qrcode.make(text)

    img.save(f'static/{name}.png')