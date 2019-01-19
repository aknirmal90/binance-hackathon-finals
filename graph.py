import sqlalchemy as sa
import json
engine = sa.create_engine('clickhouse://safu_hackathon:SatisfactionGuaranteed@data.bloxy.info:8123/production?readonly=true')
conn = engine.connect()

def node_of(t):
    address = t[1]
    annotation = t[6]
    label = address[:10]
    if annotation!='':
        label = annotation
    node = {
          'id': address,
          'label': label,
          'group': 'address',
          'title': address,
          'link': ''
    }
    return [node,t[0],t[1],t[2],t[3],t[4],t[5]]

def nodes_by_address(address):
    query_graph = """    SELECT
            'transfer_from' activity,
            concat('0x',lower(hex(transfer_from_bin))) as address,
            'ETH' symbol,
            sum(value)/1e18 as amount,
            count() count,
            toUInt32(1) as t_currency_id,
            dictGetString('address_annotation', 'text', tuple(toUInt32(1), address)) address_annotation,
            dictGetString('smart_contract_by_address', 'display_type', tuple(address)) address_type
          FROM production.transfers_to
          WHERE transfer_to_bin=unhex('{}') and currency_id=1
          GROUP BY address
          ORDER BY amount desc
          LIMIT 100

          UNION ALL

    SELECT
            'transfer_to' activity,
            concat('0x',lower(hex(transfer_to_bin))) as address,
            'ETH' symbol,
            sum(value)/1e18 as amount,
            count() count,
            toUInt32(1) as t_currency_id,
            dictGetString('address_annotation', 'text', tuple(toUInt32(1), address)) address_annotation,
            dictGetString('smart_contract_by_address', 'display_type', tuple(address)) address_type
          FROM production.transfers_from
          WHERE transfer_from_bin=unhex('{}') and currency_id=1
          GROUP BY address
          ORDER BY amount desc
          LIMIT 100"""

    rows = conn.execute(query_graph.format(address[2:],address[2:]))
    return list(map(lambda t: node_of(t), rows.fetchall()))