""" This module provides model for QTreeView widget that is created out of 
    dictionary data. """

from python_qt_binding import QtCore

class DictionaryTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None, dic={}):
        super(DictionaryTreeModel, self).__init__(parent)
        self.dic = dic
        self.rootItem = TreeItem(('tree','root'), None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()

    def setupModelData(self):
        items = self.dic.items()
        items.sort()
        for item in items:
            newparent = TreeItem(item, self.rootItem)
            self.rootItem.appendChild(newparent)

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return 1

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            if item:
                return item.data(0)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()
        
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()
    
        
class TreeItem(object):
    """
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    """
    def __init__(self, dicItem, parentItem):
        key,value = dicItem
        self.itemDataKey = key
        self.itemDataValue = value
        self.parentItem = parentItem
        self.childItems = []
        if isinstance(value,dict):
            self.itemData = key
            items = value.items()
            items.sort()
            for item in items:
                self.appendChild(TreeItem(item,self))
        #TODO: solve infinite recursion problem 
        #elif hasattr(value,'get_dic'):
        #    self.itemData = key
        #    items = value.get_dic().items()
        #    items.sort()
        #    for item in items:
        #        self.appendChild(TreeItem(item,self))
        else:
            self.itemData = ': '.join([key.__str__(),value.__str__()])

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 1
    
    def data(self, column):
        return self.itemData

    def parent(self):
        return self.parentItem
    
    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0
    
    def toString(self,indentation=''):
        """
        Return string that represents all data in this item and all children.
        """
        str = self.itemData
        for child in self.childItems:
            str += '\n'+indentation+child.toString(indentation+'    ')
        return str