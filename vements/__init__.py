#!/usr/bin/python
import os
import requests


try:
    import http.client as status
except ImportError:
    import httplib as status


class config:
    auth = os.environ.get('VEMENTS_AUTH', '')
    url = os.environ.get('VEMENTS_URL', 'https://api.vements.io')


if config.auth:
    config.auth = tuple(config.auth.split(':'))


class Client:
    timeout = (1.5, 7.5)

    def __init__(self, auth=None, url=None):
        self.auth = auth if auth else config.auth
        self.url = url if url else config.url

    def __repr__(self):
        args = self.__class__.__name__, self.url, id(self)
        return "<vements {} url='{}' at 0x{:x}>".format(*args)

    def create(self, data):
        return self.call(requests.post, data, status.CREATED)

    def read(self):
        return self.call(requests.get, None, status.OK)

    def update(self, data):
        return self.call(requests.put, data, status.RESET_CONTENT)

    def delete(self):
        return self.call(requests.delete, None, status.RESET_CONTENT)

    def call(self, reqfn, data, success):
        res = reqfn(self.url, auth=self.auth, json=data, timeout=self.timeout)
        if res.status_code == success:
            try:
                return res.json()
            except ValueError:
                # not json on a valid request
                return None
        elif 0 <= res.status_code < 400:
            return None
        elif 400 <= res.status_code < 500:
            raise ClientError(response=res)
        else:
            raise ServerError(response=res)

    def profile(self, slug):
        return Profile(self.auth, self.url+'/profile/'+slug)

    @staticmethod
    def method_pair(path, klass):
        def node(self):
            return klass(self.auth, self.url+'/'+path)
        def leaf(self, slug):
            return klass(self.auth, self.url+'/'+path+'/'+slug)
        return node, leaf


class Participant(Client):
    pass


class Achievement(Client):
    pass


class ScoreBoard(Client):
    pass


class App(Client):
    achievements, achievement = Client.method_pair('achievement', Achievement)
    participants, participant = Client.method_pair('participant', Participant)
    scoreboards, scoreboard = Client.method_pair('scoreboard', ScoreBoard)


class Namespace(Client):
    apps, app = Client.method_pair('app', App)


class Profile(Client):
    namespaces, namespace = Client.method_pair('namespace', Namespace)


class ClientError(requests.RequestException):
    pass


class ServerError(requests.RequestException):
    pass


client = Client # made to look like a function.  because.
