import pathlib


CSS_PATH = (pathlib.Path(__file__).resolve().parent /
            'static' / 'frontend' / 'built' / 'style' / 'email.min.css')


def get():
    return CSS_PATH.read_text(encoding='utf-8')
