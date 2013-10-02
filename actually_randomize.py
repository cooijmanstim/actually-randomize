# Actually Randomize Cards
# a.k.a. Randomize Cards As Opposed To Notes
# a.k.a. Randomize Cards Without Keeping Siblings Together

# bits and pieces cobbled together from anki/sched.py, aqt/browser.py, aqt/forms/browser.py

import random
from anki.hooks import addHook
from aqt import mw
from anki.utils import ids2str, intTime
from aqt.qt import *
from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

def actuallyRandomize(cids, start=1, step=1):
    scids = ids2str(cids)
    now = intTime()
    random.shuffle(cids)
    due = {}
    for c, cid in enumerate(cids):
        due[cid] = start+c*step
    # this looks needlessly complicated, but the "due" field acquires a new meaning for non-New cards
    d = []
    for (cid,) in mw.col.db.execute("select id from cards where type = 0 and id in "+scids):
        d.append(dict(now=now, due=due[cid], usn=mw.col.usn(), cid=cid))
    mw.col.db.executemany("update cards set due=:due,mod=:now,usn=:usn where id = :cid", d)

def actionActuallyRandomize(browser):
    cards = browser.selectedCards()
    browser.model.beginReset()
    browser.mw.checkpoint(_("Reposition"))
    actuallyRandomize(cards)
    browser.onSearch(reset=False)
    browser.mw.requireReset()
    browser.model.endReset()

def setupMenus(browser):
    action = QtGui.QAction(browser)
    action.setObjectName(_fromUtf8("actionActuallyRandomize"))
    action.setText(_("Actually Randomize"))
    browser.form.menuEdit.addAction(action)
    browser.connect(action, SIGNAL("triggered()"), lambda: actionActuallyRandomize(browser))

addHook('browser.setupMenus', setupMenus)
