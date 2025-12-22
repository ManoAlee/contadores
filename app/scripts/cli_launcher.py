#!/usr/bin/env python3
"""CLI launcher para executar ações principais sem GUI.

Exemplos:
  python cli_launcher.py snmp --ips app/data/ips.txt --community public
  python cli_launcher.py draft --email app/data/incoming_email.txt --ips app/data/ips.txt --out app/data --community public
"""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'app' / 'src'
import sys
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from get_printer_counters import load_ips, query_printer
from auto_reply_from_email import extract_email, extract_serials, normalize_serial, build_serial_to_counter_map, compose_reply
from send_email import send_email


def cmd_snmp(args):
    ips = load_ips(args.ips)
    results = []
    for name, ip in ips:
        print(f'Consultando {ip} (nome: {name})...')
        try:
            res = query_printer(ip, args.community)
        except Exception as e:
            res = {'ip': ip, 'error': str(e)}
        if name:
            res['location'] = name
        print(json.dumps(res, ensure_ascii=False))
        results.append(res)
    if args.out:
        outp = Path(args.out) / 'snmp_results.json'
        with open(outp, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print('Resultados salvos em', outp)


def cmd_draft(args):
    with open(args.email, 'r', encoding='utf-8') as f:
        email_text = f.read()
    to_addr = extract_email(email_text)
    serials = extract_serials(email_text)
    if not to_addr or not serials:
        print('Não foi possível extrair email ou seriais do arquivo.')
        return
    ips = load_ips(args.ips)
    try:
        mapping = build_serial_to_counter_map(ips, args.community)
    except Exception as e:
        # se pysnmp não disponível, tentar carregar arquivo mapping_*.json em data
        print('Aviso: não foi possível consultar impressoras via SNMP (usando mapping local).', e)
        mapping = {}
        data_dir = Path(args.out)
        # procurar mapping_*.json em data dir ou em app/data
        candidates = list(data_dir.glob('mapping_*.json'))
        if not candidates:
            candidates = list((Path(__file__).resolve().parents[2] / 'app' / 'data').glob('mapping_*.json'))
        if candidates:
            try:
                with open(candidates[0], 'r', encoding='utf-8') as mf:
                    mjson = json.load(mf)
                    mapping = mjson.get('mapping', mjson)
                print('Mapping carregado de', candidates[0])
            except Exception as _:
                print('Falha ao carregar mapping local:', _)
    requested = [normalize_serial(s) for s in serials]
    body = compose_reply(to_addr, requested, mapping)
    safe_email = to_addr.replace('@', '_at_').replace('.', '_')
    out_path = Path(args.out) / f'draft_{safe_email}.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'To: {to_addr}\n')
        f.write('Subject: Re: Contadores solicitados\n\n')
        f.write(body)
    json_path = Path(args.out) / f'mapping_{safe_email}.json'
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump({'requested': requested, 'mapping': mapping}, jf, ensure_ascii=False, indent=2)
    print('Rascunho salvo em:', out_path)
    print('Mapping salvo em:', json_path)
    if args.send:
        if not (args.smtp_server and args.smtp_user):
            print('Para enviar é necessário --smtp-server e --smtp-user')
            return
        pwd = args.smtp_pass
        try:
            send_email(args.smtp_server, int(args.smtp_port), args.smtp_user, pwd, to_addr, 'Re: Contadores solicitados', body, use_ssl=args.smtp_ssl)
            print('E-mail enviado com sucesso para', to_addr)
        except Exception as e:
            print('Falha ao enviar e-mail:', e)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='cmd')

    p1 = sub.add_parser('snmp')
    p1.add_argument('--ips', required=True)
    p1.add_argument('--community', default='public')
    p1.add_argument('--out')

    p2 = sub.add_parser('draft')
    p2.add_argument('--email', required=True)
    p2.add_argument('--ips', required=True)
    p2.add_argument('--out', required=True)
    p2.add_argument('--community', default='public')
    p2.add_argument('--send', action='store_true')
    p2.add_argument('--smtp-server')
    p2.add_argument('--smtp-port', default='465')
    p2.add_argument('--smtp-user')
    p2.add_argument('--smtp-pass')
    p2.add_argument('--smtp-ssl', action='store_true', default=True)

    args = parser.parse_args()
    if args.cmd == 'snmp':
        cmd_snmp(args)
    elif args.cmd == 'draft':
        cmd_draft(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
