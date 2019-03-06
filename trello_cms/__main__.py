from jinja2 import Environment, FileSystemLoader, select_autoescape

import pathlib
import json
from argparse import ArgumentParser
from .core import load_board, TBoard

env = Environment(
    loader=FileSystemLoader("./templates"),
    autoescape=select_autoescape(['html', 'xml'])
)

if __name__ == '__main__':

    parser = ArgumentParser(description="Load and render Trello site")
    parser.add_argument('--local', action='store_true', help='Load data from local ./data/ folder')
    parser.add_argument('--store', action='store_true', help='Store response from Trello in ./data/')
    args = parser.parse_args()

    index = env.get_template("index.html")

    data_dir = pathlib.Path('./data/')

    config = json.loads(pathlib.Path('./config.json').read_bytes())

    boards = {}
    if args.local:
        for board_id, board_config in config.get('boards', {}).items():

            path = data_dir.joinpath(f'{board_id}.json')
            if not path.exists():
                print(f"[warning] Board {board_id} not found in {data_dir}, skipping.")
                continue
            board_data = json.loads(path.read_bytes())
            board_data['config'] = board_config
            boards[board_id] = TBoard(board_data)

    else:
        for board_id in config.get('boards', {}).keys():

            data = load_board(board_id)
            boards[board_id] = TBoard(data)
            if args.store:
                data_dir.joinpath(f'{board_id}.json').write_text(json.dumps(data))

    dist = pathlib.Path('./dist/')
    dist.mkdir(exist_ok=True)

    html = index.render(boards=boards)
    dist.joinpath('index.html').write_text(html)

    for board_id, board_config in config.get('boards', {}).items():

        template_list = board_config.get('template_list')
        template_single = board_config.get('template_single')

        slug = board_config.get('slug')

        if slug is None:
            print(f"Not processing board {board_id}: slug is None")
            continue

        board_dir = dist.joinpath(slug)
        board_dir.mkdir(exist_ok=True)

        if template_list:
            path = board_dir.joinpath('index.html')
            html = env.get_template(template_list).render()
            path.write_text(html)

        if template_single:

            template = env.get_template(template_single)

            for card in boards[board_id].cards:

                html = template.render(card=card)
                path = board_dir.joinpath(f'{card.id}.html')
                path.write_text(html)
