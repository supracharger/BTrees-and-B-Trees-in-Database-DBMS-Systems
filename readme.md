# B-Trees & B+Trees Toy Example found in Database DBMS Systems

Here is my implementation of DBMS B-Trees and B+Trees in python. These two algorithms are used to index a database for fast retrieval of common searches. Feel free to take a look!

EXAMPLE VALUES TO BE INDEXED:
CD29 CD32 CD42 CD44 CD46 CD48 FCC8 FCC16 FCC32 FCC33 FCC37 FCC44 FCC50 FCC51 LE3 LE8 LE11 LE13 LE14 LE19 LE28 LE33 LE36 LE42 LE44 LE51 TT4 TT7 TT17 TT20 TT23 TT27 TT28 TT29 TT33 TT40 TT48

NOTE: I create a 'cypher' as a comparable for the string values above because otherwise it would compare the strings character by character. Additionally, that is not what you want to do. Without the 'cypher' you would get "... A39 A4 A41 ..." when you want "... A4 A39 A41 ..."""



## B-Tree Example & Output:

The target fill factor is two-thirds for each node in the tree. This way when records are added or deleted into the database the B-Tree index is created less often and not every time a record is added or deleted.

EXAMPLE IMPLEMENTATION =========================================
```
from BTree import *

jobId = ('CD29 CD32 CD42 CD44 CD46 CD48 FCC8 FCC16 FCC32 FCC33 ' +
            'FCC37 FCC44 FCC50 FCC51 LE3 LE8 LE11 LE13 LE14 LE19 ' + 
            'LE28 LE33 LE36 LE42 LE44 LE51 TT4 TT7 TT17 TT20 ' + 
            'TT23 TT27 TT28 TT29 TT33 TT40 TT48').split()
cypher = SpecialStrSort().Cypher
find = ['LE3', 'FCC33']

"""
Creates the tree from the number of unique 'values.'
'values': values to be inputted into the tree. Does NOT need to be unique values.
'p': "p" node size. Max size of values in each node.
'fillFactor': (Optional) Default 2/3. The max fill size of every node in the tree.
RETURN: root node of tree.
"""
root = BTree.Create(jobId, p=4)

"""
Displays Tree Indexs & 'values' used. Also, finds the values in 'find.'
'root': The root of the B-Tree.
'values': The values to input into the tree.
'find': A list of values to find in the tree to get the number of block accesses.
'title': The title of the group to display.
'cypher': (Optional) Comparer of the 'values' in the tree to properly find the values. Not needed
            if the values don't need a extra comparer.
"""
Display(root, jobId, find, "ALGORITHM", cypher)
```


### B-Tree Multiple Examples Output:

ALGORITHM: ....................................................
Filled 66%, Nodes#: 14, Levels: 2
Tree Indexs:
15_27

3_7_11    19_23    31_34

0_1_2    4_5_6    8_9_10    12_13_14  |  16_17_18    20_21_22    24_25_26  |  28_29_30    32_33    35_36

Found LE3: 4 Block Access(es).
Found FCC33: 4 Block Access(es).

Tree Values:
LE8_TT7

CD44_FCC16_FCC44    LE19_LE42    TT27_TT33

CD29_CD32_CD42    CD46_CD48_FCC8    FCC32_FCC33_FCC37    FCC50_FCC51_LE3  |  LE11_LE13_LE14    LE28_LE33_LE36    LE44_LE51_TT4  |  TT17_TT20_TT23    TT28_TT29    TT40_TT48




PRE-MADE BEST: ................................................
Filled 66%, Nodes#: 14, Levels: 2
Tree Indexs:
15_27

3_7_11    19_23    31_34

0_1_2    4_5_6    8_9_10    12_13_14  |  16_17_18    20_21_22    24_25_26  |  28_29_30    32_33    35_36

Found LE3: 4 Block Access(es).
Found FCC33: 4 Block Access(es).

Tree Values:
LE8_TT7

CD44_FCC16_FCC44    LE19_LE42    TT27_TT33

CD29_CD32_CD42    CD46_CD48_FCC8    FCC32_FCC33_FCC37    FCC50_FCC51_LE3  |  LE11_LE13_LE14    LE28_LE33_LE36    LE44_LE51_TT4  |  TT17_TT20_TT23    TT28_TT29    TT40_TT48




PRE-MADE 2: ...................................................
Filled 54%, Nodes#: 17, Levels: 2
Tree Indexs:
13_22_31

3_7_10    16_19    25_28    34

0_1_2    4_5_6    8_9    11_12  |  14_15    17_18    20_21  |  23_24    26_27    29_30  |  32_33    35_36

Found LE3: 4 Block Access(es).
Found FCC33: 4 Block Access(es).

Tree Values:
FCC51_LE36_TT27

CD44_FCC16_FCC37    LE11_LE19    LE51_TT17    TT33

CD29_CD32_CD42    CD46_CD48_FCC8    FCC32_FCC33    FCC44_FCC50  |  LE3_LE8    LE13_LE14    LE28_LE33  |  LE42_LE44    TT4_TT7    TT20_TT23  |  TT28_TT29    TT40_TT48



## B+Tree Example & Output:

In B+Trees the address to the block record is only found in the leaf's of the tree. The target fill factor is 50% for each node in the tree. This way when records are added or deleted into the database the B+Tree index is created less often and not every time a record is added or deleted.

EXAMPLE IMPLEMENTATION =========================================
```
from BPlusTree import *
from BTree import SpecialStrSort

jobId = ('CD29 CD32 CD42 CD44 CD46 CD48 FCC8 FCC16 FCC32 FCC33 ' +
            'FCC37 FCC44 FCC50 FCC51 LE3 LE8 LE11 LE13 LE14 LE19 ' + 
            'LE28 LE33 LE36 LE42 LE44 LE51 TT4 TT7 TT17 TT20 ' + 
            'TT23 TT27 TT28 TT29 TT33 TT40 TT48').split()
cypher = SpecialStrSort().Cypher
find = ['LE3', 'FCC33']
p, p2 = 6, 4

"""
Creates the tree from the number of unique 'values.'
'values': values to be inputted into the tree. Does NOT need to be unique values.
'p': "p" internal node size. Max size of values in each internal node.
'p2': "p" leaf node size. Max size of the values in each leaf node.
'factor': (Optional) Default 50%. The max fill percent of every node in the tree.
RETURN: root node of tree.
"""
root = BPlusTree.Create(jobId, p, p2)

"""
Displays Tree Indexs & 'values' used. Also, finds the values in 'find.'
'root': The root of the B-Tree.
'values': The values to input into the tree.
'find': A list of values to find in the tree to get the number of block accesses.
'title': The title of the group to display.
'cypher': (Optional) Comparer of the 'values' in the tree to properly find the values. Not needed
            if the values don't need a extra comparer.
"""
Display(root, jobId, find, "ALGORITHM FACTOR= 50%", cypher)
```


### B+Tree Multiple Examples Output:

ALGORITHM BEST FACTOR= 7/12: ..................................
Filled 51%, Nodes#: 24, Levels: 2
Tree Indexs:
9_19_29

1_3_5_7    11_13_15_17    21_23_25_27    31_33_35

0_1    2_3    4_5    6_7    8_9  |  10_11    12_13    14_15    16_17    18_19  |  20_21    22_23    24_25    26_27    28_29  |  30_31    32_33    34_35    36

Found! FCC33: 4 Block Access(es).
Found! LE3: 4 Block Access(es).

Tree Values:
FCC33_LE19_TT20

CD32_CD44_CD48_FCC16    FCC44_FCC51_LE8_LE13    LE33_LE42_LE51_TT7    TT27_TT29_TT40

CD29_CD32    CD42_CD44    CD46_CD48    FCC8_FCC16    FCC32_FCC33  |  FCC37_FCC44    FCC50_FCC51    LE3_LE8    LE11_LE13    LE14_LE19  |  LE28_LE33    LE36_LE42    LE44_LE51    TT4_TT7    TT17_TT20  |  TT23_TT27    TT28_TT29    TT33_TT40    TT48




ALGORITHM FACTOR= 50%: ........................................
Filled 45%, Nodes#: 27, Levels: 3
Tree Indexs:
23

7_15    31

1_3_5    9_11_13    17_19_21  |  25_27_29    33_35

0_1    2_3    4_5    6_7  |  8_9    10_11    12_13    14_15  |  16_17    18_19    20_21    22_23  |  24_25    26_27    28_29    30_31  |  32_33    34_35    36

Found! FCC33: 5 Block Access(es).
Found! LE3: 4 Block Access(es). Using Linked Leaf(s)!!: FCC33.

Tree Values:
LE42

FCC16_LE8    TT27

CD32_CD44_CD48    FCC33_FCC44_FCC51    LE13_LE19_LE33  |  LE51_TT7_TT20    TT29_TT40

CD29_CD32    CD42_CD44    CD46_CD48    FCC8_FCC16  |  FCC32_FCC33    FCC37_FCC44    FCC50_FCC51    LE3_LE8  |  LE11_LE13    LE14_LE19    LE28_LE33    LE36_LE42  |  LE44_LE51    TT4_TT7    TT17_TT20    TT23_TT27  |  TT28_TT29    TT33_TT40    TT48