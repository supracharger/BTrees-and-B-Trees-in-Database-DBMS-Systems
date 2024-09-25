import numpy as np 
from collections import defaultdict
class BTree:
    """
    Creates the tree from the number of unique 'values.'
    'values': values to be inputted into the tree. Does NOT need to be unique values.
    'p': "p" node size. Max size of values in each node.
    'fillFactor': (Optional) Default 2/3. The max fill size of every node in the tree.
    'startLevel': (Optional) The minimum level it starts building from. If tree is too small
                    it will add levels until it is the right size.
    RETURN: root node of tree.
    """
    @staticmethod
    def Create(values, p, fillFactor=2/3, startLevel=1):
        assert startLevel >= 1
        n = len(set(values))
        values = list(range(n))
        # values = sorted(list(set(values))) # Sort will mess up: FCC8 FCC32 FCC33
        maxlvl = startLevel
        root = Block(p=p, factor=fillFactor)
        BTree._CreateNodes(root, maxlvl)
        while True:
            try:
                BTree._TrimNodes(n, root)
                break
            except TooSmall:
                BTree._AddLayer(root, maxlvl)
                maxlvl += 1
        BTree.FillValues(values, root)
        assert BTree._ValidateIndexs(root)
        return root
    
    @staticmethod
    def _CreateNodes(block, maxlvl, lvl=0):
        while not block.IsValid():
            block.Add(-1)
        if lvl==maxlvl: return
        nodes = block.Nodes()
        nextLast = lvl+1==maxlvl
        for n in nodes:
            n._left = block.NewBlock(n, nextLast)
            BTree._CreateNodes(n._left, maxlvl, lvl+1)
        n = nodes[-1]
        n._right = block.NewBlock(n, nextLast)
        BTree._CreateNodes(n._right, maxlvl, lvl+1)

    @staticmethod
    def _AddLayer(root, prevLevel, redoLastLyr=False):
        def Grow(block, isleft):
            if redoLastLyr:
                newblk = block._parent._block.NewBlock(block._parent, False)
                if isleft:
                    block._parent._left = newblk
                else:
                    block._parent._right = newblk
                while not newblk.IsValid():
                    newblk.Add(-1)  
                block = newblk
            nodes = block.Nodes()
            nodes = nodes + [nodes[-1]]
            for i,n in enumerate(nodes):
                newblk = block.NewBlock(n, True)
                if i < len(nodes)-1:
                    n._left = newblk
                else:
                    n._right = newblk
                while not newblk.IsValid():
                    newblk.Add(-1)
        def InOrder(block, maxLvl, lvl=0, isleft=None):
            if block==None: return
            elif lvl == maxLvl:
                Grow(block, isleft)
                return
            for n in block.Nodes():
                InOrder(n._left, maxLvl, lvl+1, True)
                InOrder(n._right, maxLvl, lvl+1, False)
        # Grow Layer
        InOrder(root, prevLevel)

    @staticmethod
    def FillValues(values, root, cypher=None, strict=True):
        if cypher==None:
            cypher = lambda v: v
        values = list(sorted(set(values), key=cypher))
        transPtr = []
        for n in root.Nodes():
            Block.InOrder(n, transPtr)
        if not strict and len(transPtr) > len(values):
            values = values + [None] * (len(transPtr) - len(values))
        assert len(values) == len(transPtr)
        for v,n in zip(values, transPtr):
            n.SetValue(v)

    @staticmethod
    def _TrimNodes(n, root, plus=False):
        if not plus:
            GetCnt = lambda c: sum(c)
        else:
            GetCnt = lambda c: c[-1]
        bst = BTree._BST([[root]])
        total = GetCnt(BTree._CountLyrs(bst))
        if total < n: raise TooSmall()
        for lyr in bst[:-1]:
            while True:
                unfound = True
                blksLyr = [b for b in lyr if len(b)>1]
                for c,branch in enumerate(reversed(blksLyr)):
                    # mn = BTree._Minimum(bst[-1])
                    remcnt = GetCnt(BTree._CalcRemoveBranch(branch))
                    if remcnt > total-n:
                        break
                    BTree._RemoveBranch(branch)
                    total -= remcnt
                    if c == len(blksLyr)-1: unfound = False
                if unfound: break
        assert total >= n
        assert total - BTree._Minimum(bst[-1]) <= n
        # Remove from bottom
        bst = BTree._BST([[root]])
        loop = True
        while loop:
            for block in reversed(bst[-1]):
                if total == n: 
                    loop = False
                    break
                block._nodes[len(block)-1].SetValue(None)
                total -= 1
        assert GetCnt(BTree._CountLyrs(bst)) == n
    
    @staticmethod
    def _RemoveBranch(branch):
        assert len(branch) >= 2
        n = branch._nodes[len(branch)-1]
        n2 = branch._nodes[len(branch)-2]
        assert n._right != None
        n2._right = n._left
        cnt = 1
        que = [n._right]
        n._right = n._left = None
        n.SetValue(None)
        while len(que) > 0:
            b = que[0]
            del que[0]
            if b == None: continue
            cnt += len(b)
            for n in b.Nodes():
                que.append(n._left)
                que.append(n._right)
                n.SetValue(None)
                n._left = n._right = None
        return cnt
    
    @staticmethod
    def _CalcRemoveBranch(branch):
        n = branch._nodes[len(branch)-1]
        assert n._right != None
        cnt = [1]
        que = [(n._right, 1)]
        while len(que) > 0:
            b, lvl = que[0]
            del que[0]
            if b == None: continue
            if len(cnt) == lvl:
                cnt.append(0)
            cnt[lvl] += len(b)
            for n in b.Nodes():
                que.append((n._left, lvl+1))
                que.append((n._right, lvl+1))
        return cnt

    @staticmethod
    def _BST(layers):
        loop = True
        while loop:
            loop = False
            lyr = layers[-1]
            next = []
            layers.append(next)
            for b in lyr:
                for n in b.Nodes():
                    if n._left != None:
                        loop = True
                        next.append(n._left)
                    if n._right != None:
                        loop = True
                        next.append(n._right)
        return layers[:-1]

    @staticmethod
    def PrettyPrintTree(root, delim='    ', delimBranch='  |  '):
        lines = BTree.DisplayTree(root, delim=delim, delimBranch=delimBranch)
        for l in lines:
            print(l, end='\n\n')

    @staticmethod
    def DisplayTree(root, delim=' ', delimBranch=' | '):
        bst = BTree._BST([[root]])
        line = []
        for i,lyr in enumerate(bst):
            l = []
            nbranch, ctr, nb = 0, 0, []
            for j,b in enumerate(lyr):
                l.append('_'.join([str(n._value) for n in b.Nodes()]))
                if i >= 2:
                    ctr += 1
                    if ctr == nbranch:
                        ctr = 0
                        nb.append(j)
                    nbranch = len(b._parent._block) + 1
            if len(nb) > 0:
                del nb[-1]
                for iii in reversed(nb):
                    l[iii] += delimBranch + l[iii+1]
                    del l[iii+1]
            line.append(delim.join(l))
        return line

    @staticmethod
    def CompileTree(diagram, p, fillFactor=2/3, delim=' ', delim2=' | '):
        def ToBlocks(diagram, delim, delim2):
            ls = []
            blk = Block(p=p, factor=fillFactor)
            for lyr in diagram:
                lyr = lyr.replace(delim2, delim).split(delim)
                lyr = [[int(v) for v in l.split('_')] for l in lyr]
                blocks = []
                ls.append(blocks)
                for bv in lyr:
                    b = blk.NewBlock()
                    blocks.append(b)
                    for v in bv:
                        assert not b.IsValid()
                        b.Add(v)
            assert len(ls[0]) == 1
            return ls
        def Linker(blocks):
            assert len(blocks) >= 2
            assert len(blocks[0]) == 1
            for i in range(len(blocks)-2, -1, -1):
                lyr0 = blocks[i]
                lyr1 = blocks[i+1]
                pi = 0
                for b in lyr0:
                    for j,n in enumerate(b.Nodes()):
                        n._left = lyr1[pi]
                        childs = [n._left]
                        pi += 1
                        if j == len(b)-1:
                            n._right = lyr1[pi]
                            childs.append(n._right)
                            pi += 1
                        for blk in childs:
                            blk.SetParent(n)
                assert len(lyr1) == pi
            return blocks[0][0]
        blocks = ToBlocks(diagram, delim, delim2)
        root = Linker(blocks)
        return root

    @staticmethod
    def _CountLyrs(bst):
        ctr = []
        for lyr in bst:
            c = 0
            for b in lyr:
                c += len(b)
            ctr.append(c)
        return ctr

    @staticmethod
    def _Minimum(lyr):
        lyr = [l for l in lyr if len(l)>0]
        return sum([len(b) for b in lyr]) - len(lyr)

    @staticmethod
    def Stats(root):
        def FilledBlocks(block, ls, lvl=0):
            if block==None: return lvl-1
            ls.append(len(block) / block._p)
            for n in block.Nodes():
                FilledBlocks(n._left, ls, lvl+1)
                mxlvl = FilledBlocks(n._right, ls, lvl+1)
            return mxlvl
        filled = []
        lvl = FilledBlocks(root, filled)
        pct = np.array(filled).mean() * 100
        return pct, len(filled), lvl
    
    @staticmethod
    def _ValidateIndexs(root):
        rang = BTree._Validate_DeltaMinMax(root)
        return all([v==1 for v in rang])

    @staticmethod
    def _Validate_DeltaMinMax(root):
        def Delta(values):
            values = np.array(values)
            return values[1:] - values[:-1]
        orderNodes = []
        for n in root.Nodes():
            Block.InOrder(n, orderNodes)
        delta = Delta([n._value for n in orderNodes])
        return delta.min(), delta.max()
    
    @staticmethod
    def Find(root, value, cypher=None):
        if cypher==None:
            cypher = lambda v: v
        def Search(block, value):
            if block==None: raise KeyError()
            for n in block.Nodes():
                if value == cypher(n._value):
                    return 1
                elif value < cypher(n._value):
                    return 1 + Search(n._left, value)
            return 1 + Search(n._right, value)
        i = cypher(value)
        try:
            blkaccs = Search(root, i) + 1
        except KeyError: 
                return '%s: NOT FOUND!' % (str(value))
        return 'Found %s: %d Block Access(es).' % (str(value), blkaccs)
    
class PreMadeBTree:
    @staticmethod
    def PreMadeBest(n=37, p=4, factor=2/3):
        """
        blocks = PreMadeBTree.Make(37, 4)
        blocks = [
            '1_1_1',
            '1_1_1 1_1 1_1 1_1',
            '1_1 1_1 1_1 1_1 | 1_1 1_1 1_1 | 1_1 1_1 1_1 | 1_1 1_1 1'
        ]
        """
        blocks = [
            '1_1',
            '1_1_1 1_1 1_1',
            '1_1_1 1_1_1 1_1_1 1_1_1 | 1_1_1 1_1_1 1_1_1 | 1_1_1 1_1 1_1'
        ]
        return PreMadeBTree.Compile(n, blocks, p, factor)
    
    @staticmethod
    def PreMade2(n=37, p=4, factor=2/3):
        """
        blocks = PreMadeBTree.Make(37, 4)
        blocks = [
            '1_1_1',
            '1_1_1 1_1 1_1 1_1',
            '1_1 1_1 1_1 1_1 | 1_1 1_1 1_1 | 1_1 1_1 1_1 | 1_1 1_1 1'
        ]
        """
        blocks = [
            '1_1_1',
            '1_1_1 1_1 1_1 1',
            '1_1_1 1_1_1 1_1 1_1 | 1_1 1_1 1_1 | 1_1 1_1 1_1 | 1_1 1_1'
        ]
        return PreMadeBTree.Compile(n, blocks, p, factor)
        
    @staticmethod
    def Compile(n, blocks, p, fillFactor):
        root = BTree.CompileTree(blocks, p=p, fillFactor=fillFactor)
        BTree.FillValues(list(range(n)), root)
        return root
    
    @staticmethod
    def Make(n, p, fillFactor=2/3):
        root = BTree.Create(list(range(n)), p=p, fillFactor=fillFactor)
        BTree.FillValues([1] * n, root)
        diagram = BTree.DisplayTree(root)
        return diagram

class Block:
    def __init__(self, p, parent=None, factor=None, fill=None):
        assert (factor==None) != (fill==None)
        self._fill = round(p * factor) if factor!=None else fill
        assert self._fill < p 
        self._p = p
        self._parent = parent
        self._nodes = []

    def NewBlock(self, parent=None, isLastLyr=False):
        return Block(p=self._p, parent=parent, fill=self._fill)

    @staticmethod
    def _TransLeft(block, ls):
        if block==None: return
        ls.append(str(block))
        nodes = block.Nodes()
        if len(nodes) == 0: return
        n = nodes[0]
        Block._TransLeft(n._left, ls)
        Block._TransLeft(n._right, ls)

    def Add(self, value):
        assert len(self) < self._p
        assert value!=None
        n = Node(value, self, self._parent)
        self._nodes.append(n)

    def SetParent(self, parent):
        self._parent = parent
        for n in self.Nodes():
            n._parent = parent

    def __len__(self):
        return len(self._nodes)
    
    def Nodes(self):
        return self._nodes
    
    def Minimize(self):
        self._nodes = [n for n in self._nodes if n._value!=None]


    @staticmethod
    def InOrder(node, transptr):
        if node._left != None:
            for n in node._left.Nodes():
                Block.InOrder(n, transptr)
        transptr.append(node)
        if node._right != None:
            for n in node._right.Nodes():
                Block.InOrder(n, transptr)
    
    def IsValid(self):
        return len(self) == self._fill
    
    def __repr__(self):
        s = [str(n._value) for n in self._nodes]
        s += ['-' for _ in range(len(self._nodes), self._p)]
        return '[' + ' '.join(s) + ']'

class Node:
    def __init__(self, value, block, parent=None):
        self._value = value
        self._parent = parent
        self._block = block
        self._left = self._right = None

    def SetValue(self, value):
        assert self._value!=None
        self._value = value
        if value==None: self._block.Minimize()

    def __repr__(self):
        if self._value == None:
            return 'Node -'
        return 'Node %d' % self._value
    
class TooSmall(Exception):
    def __init__(self):
        super(TooSmall, self).__init__()

""" Without this sort, it would sort a string character by character, giving: "... A39 A4 A41 ..."
With this Cypher() you get the correct sort: "... A4 A39 A41 ..."""
class SpecialStrSort:
    def Cypher(self, value):
        enc = self._d[value]
        if enc != None:
            return enc
        enc = self._Cypher(value)
        self._d[value] = enc
        return enc

    @staticmethod
    def _Cypher(value):
        sp = len(value)
        for i,c in enumerate(value):
            try:
                int(c)
                sp = i
                break
            except ValueError: pass
        if sp == len(value):
            return (value, -1)
        return value[:sp], int(value[sp:])
    
    def __init__(self):
        self._d = defaultdict(lambda: None)

"""
Displays Tree Indexs & 'values' used. Also, finds the values in 'find.'
'root': The root of the B-Tree.
'values': The values to input into the tree.
'find': A list of values to find in the tree to get the number of block accesses.
'title': The title of the group to display.
'cypher': (Optional) Comparer of the 'values' in the tree to properly find the values. Not needed
            if the values don't need a extra comparer.
"""
def Display(root, values, find, title, cypher=None):
    if cypher is None:
        cypher = lambda v: v
    line = '.............................................................'
    print('%s: %s' % (title, line[len(title):]))
    pct, nNodes, lvls = BTree.Stats(root)
    print('Filled %.0f%%, Nodes#: %d, Levels: %d' % (pct, nNodes, lvls))
    print('Tree Indexes:')
    BTree.PrettyPrintTree(root)
    BTree.FillValues(values, root, cypher)
    for f in find:
        print(BTree.Find(root, f, cypher))
    print()
    print('Tree Values:')
    BTree.PrettyPrintTree(root)
    print('\n\n')

if __name__ == '__main__':
    jobId = ('CD29 CD32 CD42 CD44 CD46 CD48 FCC8 FCC16 FCC32 FCC33 ' +
            'FCC37 FCC44 FCC50 FCC51 LE3 LE8 LE11 LE13 LE14 LE19 ' + 
            'LE28 LE33 LE36 LE42 LE44 LE51 TT4 TT7 TT17 TT20 ' + 
            'TT23 TT27 TT28 TT29 TT33 TT40 TT48').split()
    cypher = SpecialStrSort().Cypher
    find = ['LE3', 'FCC33']

    print()

    root = BTree.Create(jobId, p=4)
    Display(root, jobId, find, "ALGORITHM", cypher)

    root2 = PreMadeBTree.PreMadeBest()
    Display(root2, jobId, find, "PRE-MADE BEST", cypher)

    root3 = PreMadeBTree.PreMade2()
    Display(root3, jobId, find, "PRE-MADE 2", cypher)

    print()