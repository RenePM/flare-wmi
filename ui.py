import logging
from collections import namedtuple

from funcy.objects import cached_property
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic

from cim import CIM
from cim import Index
from objects import CIM_TYPE_SIZES
from objects import TreeNamespace
from objects import ObjectResolver
from objects import TreeClassDefinition
from common import h
from common import LoggingObject
from ui.tree import Item
from ui.tree import TreeModel
from ui.tree import ColumnDef
from ui.uicommon import StructItem
from ui.uicommon import emptyLayout
from ui.hexview import HexViewWidget
from ui.vstructui import VstructViewWidget
from vstruct.primitives import v_bytes



Context = namedtuple("Context", ["cim", "index", "object_resolver"])



class PhysicalDataPageItem(Item):
    def __init__(self, ctx, index):
        super(PhysicalDataPageItem, self).__init__()
        self._ctx = ctx
        self.index = index

    def __repr__(self):
        return "PhysicalDataPageItem(index: {:s})".format(h(self.index))

    @property
    def children(self):
        return []

    @property
    def type(self):
        return "meta.physicalDataPage"

    @property
    def name(self):
        return "{:s}".format(h(self.index))

    @property
    def data(self):
        return self._ctx.cim.logical_data_store.get_physical_page_buffer(self.index)


class PhysicalDataPagesItem(Item):
    def __init__(self, ctx):
        super(PhysicalDataPagesItem, self).__init__()
        self._ctx = ctx

    def __repr__(self):
        return "PhysicalDataPagesItem(numEntries: {:s})".format(
            h(len(self.children)))

    @cached_property
    def children(self):
        return [PhysicalDataPageItem(self._ctx, i) for i in
                    xrange(self._ctx.cim.data_mapping.header.physical_page_count)]

    @property
    def type(self):
        return "meta"

    @property
    def name(self):
        return "Physical Data Pages"


class LogicalDataPageItem(Item):
    def __init__(self, ctx, index):
        super(LogicalDataPageItem, self).__init__()
        self._ctx = ctx
        self.index = index

    def __repr__(self):
        return "LogicalDataPageItem(index: {:s})".format(h(self.index))

    @property
    def children(self):
        return []

    @property
    def type(self):
        return "meta.logicalDataPage"

    @property
    def name(self):
        return "{:s}".format(h(self.index))

    @property
    def data(self):
        return self._ctx.cim.logical_data_store.get_logical_page_buffer(self.index)

    @property
    def structs(self):
        page = self._ctx.cim.logical_data_store.get_page(self.index)
        ret = [
            StructItem(0x0, "tocs", page.tocs),
        ]
        for i, data in enumerate(page.objects):
            vbuf = v_bytes(size=len(data.buffer))
            vbuf.vsParse(data.buffer)
            ret.append(StructItem(data.offset, "Object {:s}".format(h(i)), vbuf))
        return ret


class LogicalDataPagesItem(Item):
    def __init__(self, ctx):
        super(LogicalDataPagesItem, self).__init__()
        self._ctx = ctx

    def __repr__(self):
        return "LogicalDataPagesItem(numEntries: {:s})".format(
            h(len(self.children)))

    @cached_property
    def children(self):
        return [LogicalDataPageItem(self._ctx, i) for i in
                    xrange(self._ctx.cim.data_mapping.header.mapping_entry_count)]

    @property
    def type(self):
        return "meta"

    @property
    def name(self):
        return "Logical Data Pages"


class IndexKeyItem(Item):
    def __init__(self, ctx, key):
        super(IndexKeyItem, self).__init__()
        self._ctx = ctx
        self._key = key

    def __repr__(self):
        return "IndexKeyItem(key: {:s})".format(self._key)

    @property
    def children(self):
        return []

    @property
    def type(self):
        return "meta.indexKey"

    @property
    def name(self):
        return "{:s}".format(self._key.human_format())

    @property
    def data(self):
        return self._ctx.object_resolver.get_object(self._key)

    @property
    def is_data_reference(self):
        return self._key.is_data_reference


class IndexNodeItem(Item):
    def __init__(self, ctx, page_number):
        """
        pageNumber - the integer logical page number in the index file
        """
        super(IndexNodeItem, self).__init__()
        self._ctx = ctx
        self._page_number = page_number

    def __repr__(self):
        return "IndexNodeItem(pageNumber: {:s})".format(
            h(self._page_number))

    @cached_property
    def children(self):
        page = self._ctx.cim.logical_index_store.get_page(self._page_number)
        ret = []
        for i in xrange(page.key_count):
            ret.append(IndexNodeItem(self._ctx, page.get_child(i)))
            ret.append(IndexKeyItem(self._ctx, page.get_key(i)))
        ret.append(IndexNodeItem(self._ctx, page.get_child(page.key_count)))
        return ret

    @property
    def type(self):
        return "meta.indexNode"

    @property
    def name(self):
        return "Node {:s}".format(h(self._page_number))

    @property
    def data(self):
        return self._ctx.cim.logical_index_store.get_logical_page_buffer(self._page_number)


class IndexRootItem(Item):
    def __init__(self, ctx):
        super(IndexRootItem, self).__init__()
        self._ctx = ctx

    def __repr__(self):
        return "IndexRootItem()"

    @property
    def children(self):
        return [
            IndexNodeItem(self._ctx,
                self._ctx.cim.logical_index_store.root_page_number),
        ]

    @property
    def type(self):
        return "meta.index"

    @property
    def name(self):
        return "Index"


class ClassInstanceItem(Item):
    def __init__(self, ctx, *args, **kwargs):
        # TODO
        super(ClassInstanceItem, self).__init__()
        self._ctx = ctx

    def __repr__(self):
        # TODO
        return "ClassInstanceItem()"

    @cached_property
    def children(self):
        # TODO
        return []

    @property
    def type(self):
        return "objects.classInstance"

    @property
    def name(self):
        # TODO
        return ""


class ClassInstanceListItem(Item):
    def __init__(self, ctx, namespace, classname, *args, **kwargs):
        super(ClassInstanceListItem, self).__init__()
        self._ctx = ctx
        self._ns = namespace
        self._class = classname
        # TODO

    def __repr__(self):
        return "ClassInstanceListItem(namespace: {:s}, classnamename: {:s})".format(
            self._ns,
            self._class)

    @cached_property
    def children(self):
        # TODO
        return []

    @property
    def type(self):
        # TODO
        return ""

    @property
    def name(self):
        # TODO
        return "Instances"


class ClassDefinitionItem(Item):
    def __init__(self, ctx, namespace, name):
        super(ClassDefinitionItem, self).__init__()
        self._ctx = ctx
        self._ns = namespace
        self._name = name

    def __repr__(self):
        return "ClassDefinitionItem(namespace: {:s}, name: {:s})".format(
            self._ns,
            self._name)

    @cached_property
    def children(self):
        return [
            ClassInstanceListItem(self._ctx, self._ns, self._name)
        ]

    @property
    def type(self):
        return "objects.classDefinition"

    @property
    def name(self):
        return "{:s}".format(self._name)

    @cached_property
    def cd(self):
        return self._ctx.object_resolver.get_cd(self._ns, self._name)

    @cached_property
    def cl(self):
        return self._ctx.object_resolver.get_cl(self._ns, self._name)

    @property
    def data(self):
        # TODO: don't reach
        return TreeClassDefinition(self._ctx, self._ns, self._name).cd._buf

    @cached_property
    def structs(self):
        cd = self.cd
        ret = [
            # TODO: don't reach
            StructItem(0x0, "definition", cd._def),
        ]
        return ret


class ClassDefinitionListItem(Item):
    def __init__(self, ctx, namespace):
        super(ClassDefinitionListItem, self).__init__()
        self._ctx = ctx
        self._name = namespace

    def __repr__(self):
        return "ClassDefinitionListItem(namespace: {:s})".format(
            self._name)

    @cached_property
    def children(self):
        ret = []
        ns = TreeNamespace(self._ctx, self._name)
        for cd in ns.classes:
            ret.append(ClassDefinitionItem(self._ctx, cd.ns, cd.name))
        return ret

    @property
    def type(self):
        return ""

    @property
    def name(self):
        return "Class Defintions"


class NamespaceItem(Item):
    def __init__(self, ctx, name):
        super(NamespaceItem, self).__init__()
        self._ctx = ctx
        self._name = name

    def __repr__(self):
        return "NamespaceItem(namespace: {:s})".format(self._name)

    @cached_property
    def children(self):
        ret = [
            NamespaceListItem(self._ctx, self._name),
            ClassDefinitionListItem(self._ctx, self._name),
        ]
        return ret

    @property
    def type(self):
        return "objects.namespace"

    @property
    def name(self):
        return "{:s}".format(self._name)


class NamespaceListItem(Item):
    def __init__(self, ctx, name):
        super(NamespaceListItem, self).__init__()
        self._ctx = ctx
        self._name = name

    def __repr__(self):
        return "NamespaceListItem(namespace: {:s})".format(self._name)

    @cached_property
    def children(self):
        ret = []
        ns = TreeNamespace(self._ctx, self._name)
        for namespace in ns.namespaces:
            ret.append(NamespaceItem(self._ctx, namespace.name))
        return ret

    @property
    def type(self):
        return ""

    @property
    def name(self):
        return "Namespaces"


class ObjectsRootItem(Item):
    def __init__(self, ctx):
        super(ObjectsRootItem, self).__init__()
        self._ctx = ctx

    def __repr__(self):
        return "ObjectsRootItem()"

    @property
    def children(self):
        return [
            NamespaceItem(self._ctx, "root")
        ]

    @property
    def type(self):
        return "objects.root"

    @property
    def name(self):
        return "Objects"


class CimRootItem(Item):
    def __init__(self, ctx):
        super(CimRootItem, self).__init__()
        self._ctx = ctx

    def __repr__(self):
        return "CimRootItem()"

    @property
    def children(self):
        return [
            PhysicalDataPagesItem(self._ctx),
            LogicalDataPagesItem(self._ctx),
            IndexRootItem(self._ctx),
            ObjectsRootItem(self._ctx),
        ]

    @property
    def type(self):
        return "meta"

    @property
    def name(self):
        return "CIM"


class IndexKeyItemView(QTabWidget, LoggingObject):
    def __init__(self, key_item, parent=None):
        super(IndexKeyItemView, self).__init__(parent)
        self._key_item = key_item
        if self._key_item.is_data_reference:
            hv = HexViewWidget(self._key_item.data)
            self.addTab(hv, "Target hex view")


class DataPageView(QTabWidget, LoggingObject):
    def __init__(self, page_item, parent=None):
        super(DataPageView, self).__init__(parent)
        self._page_item = page_item
        hv = HexViewWidget(self._page_item.data)
        self.addTab(hv, "Hex view")


class LogicalDataPageItemView(QTabWidget, LoggingObject):
    def __init__(self, page_item, parent=None):
        super(LogicalDataPageItemView, self).__init__(parent)
        self._page_item = page_item

        vv = VstructViewWidget(self._page_item.structs, self._page_item.data)
        self.addTab(vv, "Structures")

        hv = HexViewWidget(self._page_item.data)
        self.addTab(hv, "Hex view")


class ClassDefinitionItemView(QTabWidget, LoggingObject):
    def __init__(self, cd_item, parent=None):
        super(ClassDefinitionItemView, self).__init__(parent)
        self._cd_item = cd_item

        te = QTextEdit()
        te.setReadOnly(True)
        f = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        td = QTextDocument()
        td.setDefaultFont(f)
        td.setPlainText(self._classDescription)
        te.setDocument(td)

        self.addTab(te, "Class details")

        vv = VstructViewWidget(self._cd_item.structs, self._cd_item.data)
        self.addTab(vv, "Structures")

        hv = HexViewWidget(self._cd_item.data)
        self.addTab(hv, "Hex view")


    @property
    def _classDescription(self):
        cd = self._cd_item.cd
        cl = self._cd_item.cl

        ret = []
        ret.append("classname: %s" % cd.class_name)
        ret.append("super: %s" % cd.super_class_name)
        ret.append("ts: %s" % cd.timestamp.isoformat("T"))
        ret.append("qualifiers:")
        for k, v in cd.qualifiers.iteritems():
            ret.append("  %s: %s" % (k, str(v)))
        ret.append("properties:")
        for propname, prop in cd.properties.iteritems():
            ret.append("  name: %s" % prop.name)
            ret.append("    type: %s" % prop.type)
            ret.append("    order: %s" % prop.entry_number)
            ret.append("    qualifiers:")
            for k, v in prop.qualifiers.iteritems():
                ret.append("      %s: %s" % (k, str(v)))
        ret.append("layout:")
        off = 0
        for prop in cl.properties:
            # TODO: refactor and merge with other impl
            ret.append("  (%s)   %s %s" % (h(off), prop.type, prop.name))
            if prop.type.is_array:
                off += 0x4
            else:
                off += CIM_TYPE_SIZES[prop.type.type]
        return "\n".join(ret)


class Form(QWidget, LoggingObject):
    def __init__(self, ctx, parent=None):
        super(Form, self).__init__(parent)
        self._ctx = ctx
        self._tree_model = TreeModel(
                CimRootItem(ctx),
                [
                    ColumnDef("Name", "name"),
                    ColumnDef("Type", "type"),
                ])

        # TODO: maybe subclass the loaded .ui and use that instance directly
        self._ui = uic.loadUi("ui/ui.ui")
        emptyLayout(self._ui.browseDetailsLayout)

        tv = self._ui.browseTreeView
        tv.setModel(self._tree_model)
        tv.header().setSectionResizeMode(QHeaderView.Interactive)
        tv.header().resizeSection(0, 250)  # chosen empirically
        tv.activated.connect(self._handleBrowseItemActivated)

        mainLayout = QGridLayout()
        mainLayout.addWidget(self._ui, 0, 0)

        self.setLayout(mainLayout)
        self.setWindowTitle("cim - ui")

    def _handleBrowseItemActivated(self, itemIndex):
        item = self._tree_model.getIndexData(itemIndex)
        details = self._ui.browseDetails
        details_layout = self._ui.browseDetailsLayout
        emptyLayout(details_layout)

        if isinstance(item, PhysicalDataPageItem):
            v = DataPageView(item, details)
            details_layout.addWidget(v)

        elif isinstance(item, LogicalDataPageItem):
            v = LogicalDataPageItemView(item, details)
            details_layout.addWidget(v)

        elif isinstance(item, IndexNodeItem):
            v = DataPageView(item, details)
            details_layout.addWidget(v)

        elif isinstance(item, IndexKeyItem):
            v = IndexKeyItemView(item, details)
            details_layout.addWidget(v)

        elif isinstance(item, ClassDefinitionItem):
            v = ClassDefinitionItemView(item, details)
            details_layout.addWidget(v)


def main(type_, path):
    logging.basicConfig(level=logging.INFO)
    if type_ not in ("xp", "win7"):
        raise RuntimeError("Invalid mapping type: {:s}".format(type_))

    c = CIM(type_, path)

    index = Index(c.cim_type, c.logical_index_store)
    object_resolver = ObjectResolver(c, index)
    ctx = Context(c, index, object_resolver)

    app = QApplication(sys.argv)
    screen = Form(ctx)
    screen.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
