#!/usr/bin/env python3
"""Consulta contadores e informação de impressoras via SNMP.
Uso: python get_printer_counters.py --ips ips.txt --community public
"""
import sys
import argparse

# Tentativa de import do pysnmp adiada: módulos de teste podem querer
# importar funções como `load_ips` sem ter pysnmp instalado.
_HAS_PYSNMP = True
try:
    from pysnmp.hlapi import *
except Exception:
    _HAS_PYSNMP = False

# OIDs a consultar (tentativas múltiplas para compatibilidade)
OIDS = {
    'sysName': '1.3.6.1.2.1.1.5.0',
    'sysDescr': '1.3.6.1.2.1.1.1.0',
    # Printer-MIB possíveis OIDs
    'prtGeneralSerialNumber': '1.3.6.1.2.1.43.5.1.1.17.1',
    # prtMarkerLifeCount (can be table; try common instance)
    'prtMarkerLifeCount': '1.3.6.1.2.1.43.10.2.1.4.1.1',
    # Fallbacks from HOST-RESOURCES / ENTITY-MIB
    'entPhysicalModelName': '1.3.6.1.2.1.47.1.1.1.1.13.1',
    'entPhysicalSerialNum': '1.3.6.1.2.1.47.1.1.1.1.11.1',
}


def snmp_get(ip, community, oid, timeout=2, retries=1):
    if not _HAS_PYSNMP:
        raise RuntimeError('pysnmp não disponível in this environment')
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((ip, 161), timeout=timeout, retries=retries),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    if errorIndication:
        return None
    if errorStatus:
        return None
    for varBind in varBinds:
        # varBind is (ObjectName, ObjectValue)
        return str(varBind[1])
    return None


def query_printer(ip, community):
    result = {'ip': ip, 'community': community}
    # básicos
    result['sysName'] = snmp_get(ip, community, OIDS['sysName'])
    result['sysDescr'] = snmp_get(ip, community, OIDS['sysDescr'])

    # tentar serial em ordem de preferência
    serial_oids = [
        OIDS['prtGeneralSerialNumber'],
        OIDS['entPhysicalSerialNum'],
    ]
    result['serial'] = None
    for oid in serial_oids:
        val = snmp_get(ip, community, oid)
        if val and val not in ('', '0'):
            result['serial'] = val
            break

    # tentar modelo
    model_oids = [
        OIDS['entPhysicalModelName'],
        OIDS['sysDescr'],
    ]
    result['model'] = None
    for oid in model_oids:
        if oid == OIDS['sysDescr']:
            val = result.get('sysDescr')
        else:
            val = snmp_get(ip, community, oid)
        if val and val not in ('', '0'):
            result['model'] = val
            break

    # tentar contador (pages)
    count_oids = [OIDS['prtMarkerLifeCount']]
    result['counter'] = None
    for oid in count_oids:
        val = snmp_get(ip, community, oid)
        if val and val not in ('', '0'):
            result['counter'] = val
            break

    return result


def load_ips(path):
    ips = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            # aceitar formato "Nome,IP" ou apenas "IP"
            if ',' in s:
                name, ip = [p.strip() for p in s.split(',', 1)]
            else:
                name = None
                ip = s
            ips.append((name, ip))
    return ips


def main():
    parser = argparse.ArgumentParser(description='Consulta contadores de impressoras via SNMP')
    parser.add_argument('--ips', '-i', required=True, help='Arquivo com IPs (uma linha por registro: "Nome,IP" ou "IP")')
    parser.add_argument('--community', '-c', default='public', help='Comunidade SNMP (padrão: public)')
    args = parser.parse_args()

    ips = load_ips(args.ips)
    if not ips:
        print('Nenhum IP encontrado em', args.ips)
        sys.exit(1)

    results = []
    for name, ip in ips:
        print(f'Consultando {ip} (nome: {name})...')
        res = query_printer(ip, args.community)
        if name:
            res['location'] = name
        results.append(res)

    # imprimir resultado formatado
    print('\nResultados:')
    for r in results:
        print('---')
        print('Localidade:', r.get('location') or '-')
        print('IP:', r.get('ip'))
        print('Modelo (tentativa):', r.get('model') or '-')
        print('Serial (tentativa):', r.get('serial') or '-')
        print('Contador (tentativa):', r.get('counter') or '-')
        print('sysName:', r.get('sysName') or '-')
        print('sysDescr:', r.get('sysDescr') or '-')

if __name__ == '__main__':
    main()
