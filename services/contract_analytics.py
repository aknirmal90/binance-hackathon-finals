import sqlalchemy as sa
import pandas as pd
import json
import urllib.request
import random
from urllib.error import HTTPError

engine = sa.create_engine('clickhouse://safu_hackathon:SatisfactionGuaranteed@data.bloxy.info:8123/production?readonly=true')
conn = engine.connect()


'''
  Helper functions

'''

def walk_trace(trace, f=print, knows_true=None):
    '''
        
        walks the trace, calling function f(line, knows_true) for every line
        knows_true is a list of 'if' conditions that had to be met to reach a given
        line

    '''
    res = []
    knows_true = knows_true or []

    for idx, line in enumerate(trace):
        found = f(line, knows_true)

        if found is not None:
            res.append(found)

        if opcode(line) == 'IF':
            condition, if_true, if_false = line[1:]
            res.extend(walk_trace(if_true, f, knows_true + [condition]))
            res.extend(walk_trace(if_false, f, knows_true + [('ISZERO', condition)]))

            assert idx == len(trace)-1, trace # IFs always end the trace tree
            break

        if opcode(line) == 'WHILE':
            condition, while_trace = line[1:]
            res.extend(walk_trace(while_trace, f, knows_true + [('ISZERO', condition)]))
            continue

        if opcode(line) == 'LOOP':
            loop_trace, label = line[1:]
            res.extend(walk_trace(loop_trace, f, knows_true))

    return res


def opcode(exp):
    if type(exp) in (list, tuple) and len(exp) > 0:
        return exp[0]
    else:
        return None


def deep_tuple(exp):
    if type(exp) != list:
        return exp

    if len(exp) == 0:
        return tuple()


    # converts (mask_shl, size, 0, 0, (storage, size, offset, val)) ->
    #               -> (storage, size, offset, val)  

    if exp[0] == 'MASK_SHL' and (exp[2], exp[3]) == (0, 0) and opcode(exp[4]) == 'STORAGE' and\
        exp[1] == exp[4][1] and exp[4][2] == 0:
            return deep_tuple(exp[4])

    exp = tuple(deep_tuple(e) for e in exp)
    exp = cleanup_mul_1(exp)

    return exp


def cleanup_mul_1(exp):
    '''

        converts (MUL, 1, X) into plain X within expression
        this simplification should be done by decompiler, and will
        be in the next version

    '''

    if type(exp) != tuple:
        return exp

    if exp[:2] == ('MUL', 1) and len(exp) == 3:
        return exp[2]

    if exp[:2] == ('MUL', 1):
        assert len(exp) > 3
        return cleanup_mul_1(('MUL', ) + exp[2:])

    return tuple(cleanup_mul_1(e) for e in exp)


def flatten(exp):
    if type(exp) != tuple:
        return (exp, )

    res = tuple()

    for e in exp:
        res += flatten(e)

    return res


'''

    Bytecode analysis

'''

def get_features(contract, func_count):

    funcs = []

    for func in contract['functions']:
          func['trace'] = cleanup_mul_1(deep_tuple(func['trace']))
          funcs.append(func)

    def cleanup(exp):
        return cleanup_mul_1(exp)

    def check_call(line, _):
        if opcode(line) != 'CALL':
            return None

        wei = cleanup(line[3])

        return flatten(wei)

    res = []

    for func in funcs:
        res += walk_trace(func['trace'], check_call)

    def count(func):
        return len([1 for r in res if func(r)])

    feature_functions = {
      #  'calls': lambda r: 1,
        'withdrawals': lambda r: r != 0,
        'non_withdrawals': lambda r: r == 0, # 
        'regular': lambda r: r in (('CALLVALUE',), 0, ('BALANCE', 'ADDRESS')), # CALLVALUE, 0, ('BALANCE', 'ADDRESS')
        'big_round_number': lambda r: type(r)==int and r != 0 and r % 10**6 == 0, # X % 100000 == 0
        'having_div': lambda r: type(r) == tuple and 'DIV' in r,
        'having_timestamp': lambda r: type(r) == tuple and 'TIMESTAMP' in r,
        'having_blocknumber': lambda r: type(r) == tuple and 'NUMBER' in r,
        'mul_div_add_timestamp': lambda r: type(r) == tuple and r[:4] == ('MUL', 'DIV', 'ADD', 'TIMESTAMP'),
        'div_balance_address_10': lambda r: type(r) == tuple and r[:4] == ('DIV', 'BALANCE', 'ADDRESS', 10),
        'add_callvalue_mul_minus': lambda r: type(r) == tuple and r[:4] == ('ADD', 'CALLVALUE', 'MUL', -1),
        'div_add_mul_number': lambda r: type(r) == tuple and r[:4] == ('DIV', 'ADD', 'MUL', 'NUMBER'),
        'weird': lambda r: type(r) == tuple and r[:5] == ('STORAGE', 256, 9976689104884298689014692976884767643917891793218981824792812444539348411738112, 4, 'STORAGE'),
        'just_callvalue': lambda r: type(r) == tuple and r == ('CALLVALUE', ),
        'just_balance_address': lambda r: r == ('BALANCE', 'ADDRESS'),
    }

    features = {}

    for key, func in feature_functions.items():
        #features['abs_'+key] = count(func)
        if func_count > 0:
            features['xbc_'+key] = count(func) / func_count
        else:
            features['xbc_'+key] = 0

    return features

def contract_metrics(addr):
    print(f'contract_metrics for {addr} ...')
    try: 
        url = f'http://eveem.org/code/{addr}.json'

        with urllib.request.urlopen(url) as response:
            info = response.info()
            bytelen = int(info['Length'])
            if bytelen > 3000000:
                print(f'skipped smart contract with byte length {bytelen}.')
                return None

            re = response.read()
            contract = json.loads(re)

    except:
        return None

    func_count = 0
    payable_count = 0
    loc = 0

    for func in contract['functions']:
        func_count+=1
        if '[95mpayable' in func['print']:
            payable_count+=1
        loc += len(func['print'].split('\n'))
    
    features = get_features(contract, func_count)
    
    
    #func['print']
    #str(func['trace'])
    
    features['address'] = addr

    features['xbc_payables'] = payable_count/func_count if func_count>0 else 0
    features['xbc_loc_per_function'] = loc/func_count if func_count>0 else 0
    
    return features
    