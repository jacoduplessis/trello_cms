import markdown
import json
from urllib.request import urlopen
from .utils import cached_property


class TLabel:
    def __init__(self, board, data):
        self.board = board
        self.name = data.get('name')
        self.id = data.get('id')
        self.uses = data.get('uses')
        self.color = data.get('color')

    @cached_property
    def cards(self):
        result = []
        for card in self.board.cards:
            for label in card._labels:
                if label.get('id') == self.id:
                    result.append(card)

        return result


class TList:
    def __init__(self, board, payload):
        self.board = board
        self.name = payload.get('name')
        self.id = payload.get('id')

    @cached_property
    def cards(self):
        result = []
        for card in self.board.cards:
            if card.list_id == self.id:
                result.append(card)

        return result


def slugify(s):
    return '_'.join(s.split()).lower()


class TCardMeta:

    def __init__(self, data, board):
        self.name_index = {}
        self.slug_index = {}
        self.id_index = {}

        for item in data:
            cf_id = item.get('idCustomField')
            name = board.custom_fields.get(cf_id, {}).get('name', '')
            slug = slugify(name)
            self.id_index[cf_id] = item
            self.name_index[name] = item
            self.slug_index[slug] = item

    def __getattr__(self, key):
        item = self.slug_index.get(key)
        if item is None:
            return None
        return self.get_value(item)

    @staticmethod
    def get_value(item):
        value = item.get('value')
        if 'text' in value:
            return value['text']

        # TODO: check and return other custom field types
        return ''

    def by_name(self, name):
        item = self.name_index.get(name)
        if item is None:
            return None
        return self.get_value(item)

    def by_id(self, id_):
        item = self.id_index.get(id_)
        if item is None:
            return None
        return self.get_value(item)


class TCard:
    def __init__(self, board, data):
        self.id = data.get('id')
        self.board = board
        self._labels = data.get('labels')
        self.list_id = data.get('idList')
        self.name = data.get('name')
        self.desc = data.get('desc')
        self.previews = [TPreview(preview) for attachment in data.get('attachments') for preview in
                         attachment.get('previews')]

        try:
            self.src = data['attachments'][0]['url']
        except Exception:
            self.src = ''

        self.meta = TCardMeta(data.get('customFieldItems', {}), board)

    @cached_property
    def url(self):
        slug = self.board.config.get('slug')
        if slug is None:
            return ''

        return f'/{slug}/{self.id}.html'

    @cached_property
    def description_html(self):
        return markdown.markdown(self.desc)

    @cached_property
    def list(self):
        for _list in self.board.lists:
            if _list.id == self.list_id:
                return _list

    @cached_property
    def labels(self):
        result = []
        label_ids = [l['id'] for l in self._labels]
        for label in self.board.labels:
            if label.id in label_ids:
                result.append(label)

        return result


class TBoard:
    def __init__(self, data):
        _labels = data.get('labels')
        _cards = data.get('cards')
        _lists = data.get('lists')

        self.name = data.get('name')
        self.desc = data.get('desc')
        self.id = data.get('id')
        self.config = data.get('config')

        # must load this before other objects
        self.custom_fields = {x['id']: x for x in data.get('customFields')}

        self.cards = [TCard(self, card) for card in _cards]
        self.labels = [TLabel(self, label) for label in _labels if label.get('name')]
        self.lists = [TList(self, _list) for _list in _lists if not _list.get("closed")]

    def label_by_id(self, id_):
        for label in self.labels:
            if label.id == id_:
                return label
        return None

    def list_by_id(self, id_):
        for lst in self.lists:
            if lst.id == id_:
                return lst
        return None

    def list_by_name(self, name):
        for lst in self.lists:
            if lst.name == name:
                return lst
            if slugify(lst.name) == name:
                return lst
        return None


class TPreview:
    def __init__(self, data):
        self.bytes = data.get("bytes")
        self.url = data.get("url")
        self.width = data.get("width")
        self.height = data.get("height")
        self.scaled = data.get("scaled")


def load_board(board_id):
    resp = urlopen('https://trello.com/b/{}.json'.format(board_id))
    data = json.load(resp)
    return data
