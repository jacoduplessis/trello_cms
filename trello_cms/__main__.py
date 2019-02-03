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
        for board_id in config.get('boards', {}).keys():

            path = data_dir.joinpath(f'{board_id}.json')
            if not path.exists():
                print(f"[warning] Board {board_id} not found in {data_dir}, skipping.")
                continue
            board_data = json.loads(path.read_bytes())
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
