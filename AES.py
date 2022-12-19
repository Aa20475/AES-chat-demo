
from copy import deepcopy
import random
from collections import deque

def block_to_state(block):
    state = [[0 for _ in range(4)] for x in range(4)]
    for i in range(4):
        for j in range(4):
            state[i][j] = block[i+(4*j)]
    return state

def state_to_block(state):
    block = []

    for i in range(4):
        for j in range(4):
            block.append(state[j][i])
    return block

def intbytes_from_hex(hex_str):
    return int(hex_str[0], base=16), int(hex_str[1], base=16)

def hex_from_intbytes(bytes):
    a,b = '%X'%bytes[0], '%X'%bytes[1]
    return a+b

SUB_BYTES = None
SUB_BYTES_INV = None
C = None
C_INV = None


def normalize_state(state):
    for i in range(len(state)):
        for j in range(len(state[0])):
            if len(state[i][j])==1:
                state[i][j] = '0'+state[i][j]
    return state

def normalize_block(state):
    for i in range(len(state)):
        if len(state[i])==1:
            state[i] = '0'+state[i]
    return state


def generate_subBytes():
    hexalphabet = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    bytechoices = []
    for i in range(16):
        for j in range(16):
            bytechoices.append(hexalphabet[i]+hexalphabet[j])
    subBytes = []
    global KEY
    KEY = [random.choice(bytechoices) for _ in range(16)]
    choices = deepcopy(bytechoices)
    for i in range(len(hexalphabet)):
        nrow = []
        for j in range(len(hexalphabet)):
            random.shuffle(choices)
            currpick = choices.pop()
            nrow.append(currpick)

        subBytes.append(nrow)
    global SUB_BYTES
    SUB_BYTES = subBytes

#########################################################
generate_subBytes()
def get_sub(hexstr):
    i,j = intbytes_from_hex(hexstr)
    global SUB_BYTES
    return SUB_BYTES[i][j]
##########################################################



def generate_subBytesInv():

    inverse = [[0 for _ in range(16)] for x in range(16)]
    for i in range(16):
        for j in range(16):
            ni,nj = intbytes_from_hex(SUB_BYTES[i][j])
            inverse[ni][nj] = hex_from_intbytes((i,j))

    global SUB_BYTES_INV
    SUB_BYTES_INV = inverse


##################################################
generate_subBytesInv()
def get_sub_inv(hexstr):
    global SUB_BYTES_INV
    ni,nj = intbytes_from_hex(hexstr)
    return SUB_BYTES_INV[ni][nj]
####################################################

def state_subBytes(state):
    state = normalize_state(state)
    subtest = [[0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            subtest[i][j] = get_sub(state[i][j])
    return subtest

def state_subBytesInv(state):
    state = normalize_state(state)
    subtestinv = [[0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            subtestinv[i][j] = get_sub_inv(state[i][j])
    return subtestinv





test = [['%X'%random.randint(0,255) for _ in range(4)] for x in range(4)]
#subtest = state_subBytes(test)
#subtestinv = state_subBytesInv(subtest)
#print(test)
#print(subtest)
#print(subtestinv)

def shiftRows(state):
    state = normalize_state(state)
    statec = state[:]
    for i in range(1,4):
        temp = deque(statec[i])
        temp.rotate(-i)
        statec[i] = list(temp)
        #state[i] = state[i][i:]+state[i][:i]
  
    return statec

def shiftRowsInv(state):
    state = normalize_state(state)
    statec = state[:]
    for i in range(1,4):
        temp = deque(statec[i])
        temp.rotate(i)
        statec[i] = list(temp)
        #state[i] = state[i][-i:]+state[i][:-i]


    return statec

def generate_C():
    c = [[2,3,1,1], [1,2,3,1],[1,1,2,3],[3,1,1,2]]
    for i in range(4):
        for j in range(4):
            c[i][j] = '%X'%c[i][j]
    global C
    C = normalize_state(c)
generate_C()

def generate_C_Inv():
    c = [['0E','0B','0D','09'], ['09','0E','0B','0D'],['0D','09','0E','0B'],['0B','0D','09','0E']]
    global C_INV
    C_INV = normalize_state(c)
generate_C_Inv()


# def gmul(a,b):
#     print(a,b)
#     if b == 1:
#         return a
#     tmp = (a << 1) & 0xff
#     if b == 2:
#         return tmp if a < 128 else tmp ^ 0x1b
#     if b == 3:
#         return gmul(a, 2) ^ a


@staticmethod
def gmul(a, b):
    p = 0
    for c in range(8):
        if b & 1:
            p ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11b
        b >>= 1
    return p

def mixColumn(arr):
    a,b,c,d = arr
    v1 = (gmul(a, 2) ^ gmul(b, 3) ^ gmul(c, 1) ^ gmul(d, 1))
    v2 = (gmul(a, 1) ^ gmul(b, 2) ^ gmul(c, 3) ^ gmul(d, 1))
    v3 = (gmul(a, 1) ^ gmul(b, 1) ^ gmul(c, 2) ^ gmul(d, 3))
    v4 = (gmul(a, 3) ^ gmul(b, 1) ^ gmul(c, 1) ^ gmul(d, 2))
    return [v1,v2,v3,v4]

def mixColumns(state):
    global C

    ans = [[0 for _ in range(4)] for x in range(4)]
    for col in range(4):
        currcol = [int(state[i][col],base = 16) for i in range(4)]
        arr = mixColumn(currcol)
#        v1 = (2*currcol[0])^(3*currcol[1])^(currcol[2])^(currcol[3])
#        v2 = (2*currcol[1])^(3*currcol[2])^(currcol[3])^(currcol[0])
#        v3 = (2*currcol[2])^(3*currcol[3])^(currcol[0])^(currcol[1])
#        v4 = (2*currcol[3])^(3*currcol[0])^(currcol[1])^(currcol[2])
        ans[0][col] = '%X'%arr[0]
        ans[1][col] = '%X'%arr[1]
        ans[2][col] = '%X'%arr[2]
        ans[3][col] = '%X'%arr[3]
    
    return normalize_state(ans)

def invmixColumn(arr):
    #print(arr)
    a,b,c,d = arr
    
    #print(m1,m2,m3,m4)
    v1 = (gmul(a, 14) ^ gmul(b, 11) ^ gmul(c, 13) ^ gmul(d, 9))
    v2 = (gmul(a, 9) ^ gmul(b, 14) ^ gmul(c, 11) ^ gmul(d, 13))
    v3 = (gmul(a, 13) ^ gmul(b, 9) ^ gmul(c, 14) ^ gmul(d, 11))
    v4 = (gmul(a, 11) ^ gmul(b, 13) ^ gmul(c, 9) ^ gmul(d, 14))
    return [v1,v2,v3,v4]

def invmixColumns(x):
    global C

    ans = [[0 for _ in range(4)] for x in range(4)]
    for col in range(4):
        currcol = [int(x[i][col],base = 16) for i in range(4)]
        #print(currcol)
        arr = invmixColumn(currcol)
#        v1 = (2*currcol[0])^(3*currcol[1])^(currcol[2])^(currcol[3])
#        v2 = (2*currcol[1])^(3*currcol[2])^(currcol[3])^(currcol[0])
#        v3 = (2*currcol[2])^(3*currcol[3])^(currcol[0])^(currcol[1])
#        v4 = (2*currcol[3])^(3*currcol[0])^(currcol[1])^(currcol[2])
        ans[0][col] = '%X'%arr[0]
        ans[1][col] = '%X'%arr[1]
        ans[2][col] = '%X'%arr[2]
        ans[3][col] = '%X'%arr[3]
    
    return normalize_state(ans)


# xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)

# def mix_single_column(a):
#     # see Sec 4.1.2 in The Design of Rijndael
#     t = a[0] ^ a[1] ^ a[2] ^ a[3]
#     u = a[0]
#     a[0] ^= t ^ xtime(a[0] ^ a[1])
#     a[1] ^= t ^ xtime(a[1] ^ a[2])
#     a[2] ^= t ^ xtime(a[2] ^ a[3])
#     a[3] ^= t ^ xtime(a[3] ^ u)


# def mix_columns(s):
#     for i in range(4):
#         mix_single_column(s[i])



# def inv_mix_columns(s):
#     # see Sec 4.1.3 in The Design of Rijndael
#     for i in range(4):
#         u = xtime(xtime(s[i][0] ^ s[i][2]))
#         v = xtime(xtime(s[i][1] ^ s[i][3]))
#         s[i][0] ^= u
#         s[i][1] ^= v
#         s[i][2] ^= u
#         s[i][3] ^= v

#     mix_columns(s)


def RotWord(word):
    temp = deque(word)
    temp.rotate(-2)
    return "".join(list(temp))
    return temp

def SubWord(word):
    word = [word[i:i+2] for i in range(0,len(word), 2)]
    word = normalize_block(word)

    word = [get_sub(x) for x in word]
    #print(word)
    return "".join(word)

def AddRoundKey(state, key):


    # keys = [[0 for _ in range(4)] for x in range(4)]
    # for k in range(len(keys)):
    #     for i in range(4):
    #         keys[i][k] = keys[k][i*2:i*2+2]

    Nb = len(state)
    # print(key)
    keys= [[None for j in range(4)] for i in range(Nb)]
    for j,k in enumerate(key):
        for i in range(0,4):
            keys[i][j]= k[2*i:2*i+2]
    #print(key)
    #print(keys)
    new_state = [[None for j in range(4)] for i in range(Nb)]
    
    for i in range(len(state)):
        for j in range(len(state[0])):
            #print('state',state[i][j], 'key',keys[i][j])
            new_state[i][j]= '%X'%(int(state[i][j],base =16)^int(keys[i][j],base=16))
    return normalize_state(new_state)



def keyExpansion(key):
    RCon = ['01', '02','04','08', '10', '20', '40', '80', '1B', '36']
    words = []
    for i in range(0,len(key),4):
        wi = ''
        for x in key[i:i+4]:
            wi+=x
        words.append(wi)

    for i in range(4, 44):
        if i%4!=0:
            #print(i-1, i-4)
            #print(words[i-1])
            #print(words[i-4])
            wi = '%X'%(int(words[i-1],base = 16) ^ int(words[i-4], base=16))
            # if len(wi)<8: print(wi)
            if len(wi)<8:
                for i in range(8-len(wi)):
                    wi='0'+wi
            words.append(wi)
        else:
            #print(i//4 - 1)
            #print(RCon[i//4])
            t = int(SubWord(RotWord(words[i-1])), base=16) ^ int(RCon[i//4 - 1], base=16)
            wi = '%X'%(t^int(words[i-4],base = 16))
            if len(wi)<8:
                for i in range(8-len(wi)):
                    wi='0'+wi
            words.append(wi)
            # if len(wi)<8: print(wi)
    return words




def cipher(state,Key):
    global KEY
    
    Key=KEY

    roundkeys = keyExpansion(Key)
    # print(roundkeys)
    round=0
    newState= AddRoundKey(state,roundkeys[round* 4:round*4+4])

    for round in range(1,10):
        newState=state_subBytes(newState)
        newState=shiftRows(newState)
        newState=mixColumns(newState)
        newState= AddRoundKey(newState,roundkeys[round*4:round*4+4])

    newState=state_subBytes(newState)
    newState=shiftRows(newState)
    newState= AddRoundKey(newState,roundkeys[40:44])

    return newState

    
def decipher(state,Key):
    global KEY    
    Key=KEY
    roundkeys = keyExpansion(Key)
    round=10
    newState= AddRoundKey(state,roundkeys[round* 4:round*4+4])
    for round in range(9,-1,-1):
        # print(round, round*4, round*4+4)
        newState=shiftRowsInv(newState)
        newState=state_subBytesInv(newState)
        newState=AddRoundKey(newState,roundkeys[round*4:round*4+4])
        if (round!=0):
            newState=invmixColumns(newState)
    return newState

roundkeys = keyExpansion(KEY)
state = [['63','C9','FE','30'],['F2','63','26','F2'],['7D','D4','C9','C9'],['D4','FA','63','82']]

# chk = state_subBytes(state)
# chkinv = state_subBytesInv(chk)

# chk = shiftRows(state)
# chkinv = shiftRowsInv(chk)

# chk = mixColumns(state)
# chkinv = invmixColumns(chk)

# chk = AddRoundKey(state, roundkeys[23:27])
# chkinv = AddRoundKey(chk, roundkeys[23:27])

# chk = cipher(state, KEY)
# chkinv = decipher(chk, KEY)

# print(state)
# print(chk)
# print(chkinv)



# roundkeys = keyExpansion(KEY)
# print(roundkeys)


# newState= AddRoundKey(state,roundkeys[0:4])
# print(newState)

pt = 'My name is Slim shady. Hi kis do you like violence? Wanna see me stick nine inch nails through each one of my eyelids. Wanna copy me and do exactly like i did? Try and see if it gets fucked up worse than my life is?'

for i in range(16-len(pt)%16):
    pt+=' '


test = ''
for i in range(0,len(pt), 16):
    curr_pt = pt[i:i+16]

    state = block_to_state(curr_pt)

    for i in range(4):
        for j in range(4):
            state[i][j] = '%X'%ord(state[i][j])
    # chk = state_to_block(state)
    # chk = [chr(int(x, base=16)) for x in chk]
    # s = ''.join(chk)
    # test = test+s
    cstate = cipher(state, KEY)
    cstate = state_to_block(cstate)
    #chk = [chr(int(x, base=16)) for x in cstate]
    s = ''.join(cstate)
    test = test+s

print()
print('CipherText:',test)
print()
testc = ''
for i in range(0,len(test), 32):

    curr_pt = test[i:i+32]
    curr_pt = [curr_pt[i:i+2] for i in range(0,len(curr_pt), 2)]
    #print('curr:',curr_pt)

    state = block_to_state(curr_pt)

    # chk = state_to_block(state)
    # chk = [chr(int(x, base=16)) for x in chk]
    # s = ''.join(chk)
    # test = test+s
    cstate = decipher(state, KEY)
    cstate = state_to_block(cstate)
    chk = [chr(int(x, base=16)) for x in cstate]
    s = ''.join(chk)
    testc = testc+s

print('PlainText:', testc)


#### 
# To do:
# padding for chuinks of text
###