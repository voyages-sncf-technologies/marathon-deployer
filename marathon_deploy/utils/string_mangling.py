from typing import Tuple


def split_image_name(image: str) -> Tuple[str, str]:
    name_parts = image.split("/")
    # https://github.com/moby/moby/blob/b075cd2d78c1bafcded7d12ddb2e7c215e2e5117/registry/service.go#L151
    if len(name_parts) == 1 or ('.' not in name_parts[0] and ':' not in name_parts[0]) and name_parts[0] != 'localhost':
        # Imagen hosteada en Docker Hub
        reg = ''
        img = name_parts[0]
    else:
        reg = name_parts[0]
        img = name_parts[1]
    return reg, img


def split_image_tag(image: str) -> Tuple[str, str]:
    parts = image.split(':')
    if len(parts) == 1:
        return image, 'latest'
    return parts[0], parts[1]


def rebuild_image_name(registry: str, image: str, tag: str) -> str:
    full = ''
    if registry != '' and registry is not None:
        full += registry + '/'
    full += image + ':'
    if tag != '' and tag is not None:
        full += tag
    else:
        full += 'latest'
    return full


def appid_to_filename(appid: str, append_extension: bool = False) -> str:
    if appid.startswith('/'):
        appid = appid[1:]
    appid = appid.replace('/', '_').replace('.', '')
    return appid + '.json' if append_extension else appid
