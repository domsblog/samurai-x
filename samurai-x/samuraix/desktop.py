from pyglet.window.xlib import xlib 
import pyglet

import weakref
import functools

import samuraix
from samuraix.focus import FocusStack

import logging
log = logging.getLogger(__name__)


class Desktop(pyglet.event.EventDispatcher):

    def __init__(self, screen, name):
        self.screen = screen
        self.name = name

        log.info('created new desktop %s' % self)

        self.clients = []
        self.focus_stack = FocusStack()

    def __str__(self):
        return "<Desktop '%s' on %s>" % (self.name, self.screen)

    def add_client(self, client):
        log.debug('adding client %s to desktop %s' % (client, self))
        self.clients.append(weakref.ref(client))
        client.desktop = self
        client.push_handlers(
            on_removed=functools.partial(self._client_removed, client),
            on_focus=functools.partial(self._client_focused, client),
        )
        if client.desktop is self:
            client.unban()
            self.focus_client(client)
        else:
            client.ban()

    def _client_removed(self, client):
        log.debug("desktop %s removing %s" % (self, client))
        for client in self.clients:
            if client() == client:
                self.clients.remove(client)
                break

    def _client_focused(self, client):
        log.debug('_client_focused %s' % client)
        self.focus_stack.focus(client)       

    def focus_client(self, client):
        # if config['focus_new'] .. etc
        client.focus()

    def remove_client(self, client):
        assert client.desktop is self
        log.debug('removing client %s from desktop %s' % (client, self))
        client.desktop = None

    def on_show(self):
        log.info('showing desktop %s' % self)
        for client in self.clients:
            c = client()
            if c is not None:
                c.unban()
        
    def on_hide(self):
        log.info('hiding desktop %s' % self)
        for client in self.clients:
            c = client()
            if c is not None:
                c.ban()
    

Desktop.register_event_type('on_show')
Desktop.register_event_type('on_hide')

