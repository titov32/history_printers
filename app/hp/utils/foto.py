import exifread
from geopy.geocoders import Nominatim
from exif import Image

def format_lati_long(data):  # list2float
    list_tmp = str(data).replace('[', '').replace(']', '').split(',')
    list_ = [ele.strip() for ele in list_tmp]
    data_sec = int(list_[-1].split('/')[0]) / (
            int(list_[-1].split('/')[1]) * 3600)  # Значение секунд
    data_minute = int(list_[1]) / 60
    data_degree = int(list_[0])
    result = data_degree + data_minute + data_sec
    return result


def get_address(foto: str) -> dict:
    img = exifread.process_file(open(foto, 'rb'))
    latitude = format_lati_long(str(img['GPS GPSLatitude']))
    longitude = format_lati_long(str(img['GPS GPSLongitude']))
    try:
        geolocator = Nominatim(user_agent="Printers")
        location = geolocator.reverse(f'{latitude}, {longitude}')
        return {'address': location.address,
                'latitude':latitude,
                'longitude':longitude}
    except Exception as e:
        print(f'Exception while exctraxt foto {e}')
        return {'latitude':latitude,
                'longitude':longitude}

if __name__ == '__main__':
    with open('gps.jpg', 'rb') as img:
        image = Image(img)


    print(f'has_exif {image.has_exif}')
    print(f'exif ver {image.exif_version}')
    print(dir(image))

