from modict import modict


class Props(modict):
    key: str = modict.field(required="always")
    children: list = modict.factory(list)
