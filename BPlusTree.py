from BTree import BTree, Block, TooSmall, SpecialStrSort

class BPlusTree:
    """
    Creates the tree from the number of unique 'values.'
    'values': values to be inputted into the tree. Does NOT need to be unique values.
    'p': "p" internal node size. Max size of values in each internal node.
    'p2': "p" leaf node size. Max size of the values in each leaf node.
    'factor': (Optional) Default 50%. The max fill percent of every node in the tree.
    RETURN: root node of tree.
    """
    @staticmethod
    def Create(values, p, p2, factor=0.50):
        n = len(set(values))
        maxlvl = 1
        while True:
            # try: Not the most efficient solution, but for the sake of time, it works.
            try:
                root = PlusBlock(p, p2, factor)
                BTree._CreateNodes(root, maxlvl)
                BTree._TrimNodes(n, root, plus=True)
                break
            except TooSmall:
                maxlvl += 1
        BPlusTree._IndexValues(n, root)
        assert BPlusTree._ValidateIndexs(root)
        return root

    @staticmethod
    def _IndexValues(n, root):
        def FillLeaves(leaves, values):
            pi = 0
            for block in leaves:
                for n in block.Nodes():
                    n.SetValue(values[pi])
                    pi += 1
            assert len(values) == pi
            # Link Leafs
            for i,block in enumerate(leaves):
                if i > 0:
                    block._leafPrev = leaves[i-1]
                if i < len(leaves)-1:
                    block._leafNext = leaves[i+1]
        bst = BTree._BST([[root]])
        values = list(range(n))
        FillLeaves(bst[-1], values)
        mx = [[float('-inf') for b in lyr] for lyr in bst]
        for i,lyr in enumerate(reversed(bst[:-1])):
            back = len(bst)-i-2
            x0, x1 = mx[back], mx[back+1]
            p0 = p1 = 0
            for block in lyr:
                for n in block.Nodes():
                    setTo = n._left.Nodes()[-1]._value
                    setTo = max(setTo, x1[p1])
                    p1 += 1
                    vals = [x0[p0], setTo]
                    if n._right!=None:
                        vals.extend([n._right.Nodes()[-1]._value, x1[p1]])
                        p1 += 1
                    x0[p0] = max(vals)
                    assert n._value < 0
                    assert setTo >= 0
                    n.SetValue(setTo)
                p0 += 1
            assert len(x0)==p0
            assert len(x1)==p1

    @staticmethod
    def FillValues(values, root, cypher=None):
        def InOrder(node, ptr, levels, lvl=0):
            if node._left!=None:
                for n in node._left.Nodes():
                    InOrder(n, ptr, levels, lvl+1)
            ptr.append(node)
            levels.append(lvl)
            if node._right!=None:
                for n in node._right.Nodes():
                    InOrder(n, ptr, levels, lvl+1)
        if cypher==None:
            cypher = lambda v: v
        values = list(sorted(set(values), key=cypher))
        found = [False] * len(values)
        ptr, levels = [], []
        for n in root.Nodes():
            InOrder(n, ptr, levels)
        maxlvl = max(levels)
        for n,lvl in zip(ptr, levels):
            v = n._value
            val = values[v]
            if lvl == maxlvl:
                assert not found[v]
                found[v] = True
            n.SetValue(val)
        assert all(found)

    @staticmethod
    def _ValidateIndexs(root):
        mn, mx = BTree._Validate_DeltaMinMax(root)
        return mn==0 and mx==1
    
    @staticmethod
    def Find(root, values, cypher=None, leafLinkSearchMax=3):
        if not (isinstance(values, list) or isinstance(values, tuple)):
            values = [values]
        if cypher==None:
            cypher = lambda v: v
        def Search(block, value):
            if block==None: raise KeyError()
            for n in block.Nodes():
                if value == cypher(n._value) and n._left==None and n._right==None:
                    return block, 1
                elif value <= cypher(n._value):
                    blk,cnt = Search(n._left, value)
                    return blk, cnt+1
            blk,cnt = Search(n._right, value)
            return blk, cnt+1
        def SearchLeafs(block, value, mxlen, ln=0):
            if block==None or ln>mxlen: raise KeyError()
            if value > cypher(block.Nodes()[-1]._value):
                blk,cnt = SearchLeafs(block._leafNext, value, mxlen, ln+1)
                return blk, cnt+1
            for n in block.Nodes():
                if value == cypher(n._value):
                    return block, 0
            blk,cnt = SearchLeafs(block._leafPrev, value, mxlen, ln+1)
            return blk, cnt+1
        def TraceBack(out, i, ls):
            if i == None: return
            blkaccs,v,prev = out[i]
            ls.append(str(v))
            TraceBack(out, prev, ls)
        values = list(sorted(set(values), key=cypher))
        out = []
        prev = None
        for ref,v in zip([cypher(v) for v in values], values):
            # Search By Leafs .....................................................
            if prev!=None:
                try:
                    block, blkaccess = SearchLeafs(prev[0], ref, leafLinkSearchMax)
                    out.append((blkaccess+1, v, prev[1]))
                    prev = block, len(out)-1
                    continue
                except KeyError: pass
            # Full Tree Search ....................................................
            try: 
                block, blkaccess = Search(root, ref)
                out.append((blkaccess+1, v, None))
                prev = block, len(out)-1
            except KeyError: 
                out.append((-1, v, None))
        out2 = []
        for blkaccs,v,prev in out:
            if blkaccs < 0:
                out2.append('%s: NOT FOUND!' % (str(v)))
                continue
            o = 'Found! %s: %d Block Access(es).' % (str(v), blkaccs)
            if prev != None:
                ls = []
                TraceBack(out, prev, ls)
                o += ' Using Linked Leaf(s)!!: %s.' % (', '.join(reversed(ls)))
            out2.append(o)
        return out2

class PlusBlock(Block):
    def __init__(self, p, p2, factor, parent=None):
        super(PlusBlock, self).__init__(p=p, parent=parent, factor=factor)
        self._p2 = p2
        self._factor = factor
        self._leafNext = self._leafPrev = None

    def NewBlock(self, parent=None, isLastLyr=False):
        p = self._p if not isLastLyr else self._p2
        return PlusBlock(p=p, p2=self._p2, factor=self._factor, parent=parent)

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
    print('Tree Indexs:')
    BTree.PrettyPrintTree(root)
    BPlusTree.FillValues(values, root, cypher)
    for out in BPlusTree.Find(root, find, cypher, leafLinkSearchMax=lvls):
        print(out)
    print()
    print('Tree Values:')
    BTree.PrettyPrintTree(root)
    print('\n\n')

if __name__=='__main__':
    jobId = ('CD29 CD32 CD42 CD44 CD46 CD48 FCC8 FCC16 FCC32 FCC33 ' +
            'FCC37 FCC44 FCC50 FCC51 LE3 LE8 LE11 LE13 LE14 LE19 ' + 
            'LE28 LE33 LE36 LE42 LE44 LE51 TT4 TT7 TT17 TT20 ' + 
            'TT23 TT27 TT28 TT29 TT33 TT40 TT48').split()
    cypher = SpecialStrSort().Cypher
    find = ['LE3','FCC33']
    p, p2 = 6, 4

    print()
    root = BPlusTree.Create(jobId, p, p2, 7/12)
    Display(root, jobId, find, "ALGORITHM BEST FACTOR= 7/12", cypher)

    root2 = BPlusTree.Create(jobId, p, p2)
    Display(root2, jobId, find, "ALGORITHM FACTOR= 50%", cypher)

    print()