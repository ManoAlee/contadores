#!/usr/bin/env python3
"""Detecta endereço de e-mail e seriais em um e-mail de entrada, consulta as impressoras
e gera um rascunho de resposta com os contadores reais.

Uso:
  python auto_reply_from_email.py --email-file incoming_email.txt --ips ips.txt --community public

Opcional: --send + args SMTP para enviar diretamente.
"""
import re
import argparse
import json
from datetime import datetime

try:
    from get_printer_counters import query_printer, load_ips
except Exception:
    print('Erro: não foi possível importar get_printer_counters. Execute a partir da pasta do projeto.')
    raise


def extract_email(text):
    m = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", text)
    return m.group(1) if m else None


def extract_serials(text):
    # Encontrar tokens com letras e números de tamanho típico de serial (6-9)
    candidates = re.findall(r"\b([A-Z0-9]{6,9})\b", text.upper())
    # Filtrar por padrão plausível (começam com dígito ou letra) - manter ordem e unicidade
    seen = set()
    out = []
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def normalize_serial(s):
    if not s:
        return s
    s2 = s.strip().upper()
    if '-' in s2:
        s2 = s2.split('-', 1)[0]
    return s2


def build_serial_to_counter_map(ips, community):
    results = []
    for name, ip in ips:
        res = query_printer(ip, community)
        if name:
            res['location'] = name
        results.append(res)

    mapping = {}
    for r in results:
        raw = r.get('serial')
        norm = normalize_serial(raw)
        if norm:
            mapping[norm] = {
                'counter': r.get('counter'),
                'ip': r.get('ip'),
                'location': r.get('location'),
                'model': r.get('model'),
                'serial_raw': raw,
            }
    return mapping


def compose_reply(to_email, requested_serials, mapping):
    lines = []
    lines.append('Boa Tarde!')
    lines.append('')
    lines.append(f'{to_email}')
    lines.append('')
    lines.append('Segue os contadores solicitados:')
    lines.append('')
    for s in requested_serials:
        norm = normalize_serial(s)
        info = mapping.get(norm)
        if info and info.get('counter'):
            lines.append(f'{norm} – C: {info.get("counter")}')
        else:
            lines.append(f'{norm} – C: NÃO ENCONTRADO')
    lines.append('')
    lines.append('At.te,')
    lines.append('Alessandro Meneses')
    lines.append(f'Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Automação: identificar email e seriais, gerar rascunho com contadores')
    parser.add_argument('--email-file', '-e', required=True)
    parser.add_argument('--ips', '-i', required=True)
    parser.add_argument('--community', '-c', default='public')
    parser.add_argument('--output-dir', '-o', default='.')
    parser.add_argument('--send', action='store_true', help='Enviar em vez de só criar rascunho (requer args SMTP)')
    parser.add_argument('--smtp-server')
    parser.add_argument('--smtp-port', type=int, default=465)
    parser.add_argument('--smtp-user')
    parser.add_argument('--smtp-pass')
    args = parser.parse_args()

    with open(args.email_file, 'r', encoding='utf-8') as f:
        email_text = f.read()

    to_addr = extract_email(email_text)
    serials = extract_serials(email_text)

    if not to_addr:
        print('Não foi possível identificar email no conteúdo. Aborting.')
        return
    if not serials:
        print('Não foram encontrados seriais no email. Aborting.')
        return

    ips = load_ips(args.ips)
    mapping = build_serial_to_counter_map(ips, args.community)

    # filtrar apenas os seriais solicitados (ordem original)
    requested = [normalize_serial(s) for s in serials]

    body = compose_reply(to_addr, requested, mapping)

    # gravar rascunho
    safe_email = to_addr.replace('@', '_at_').replace('.', '_')
    draft_path = f"{args.output_dir}/draft_{safe_email}.txt"
    with open(draft_path, 'w', encoding='utf-8') as f:
        f.write(f'To: {to_addr}\n')
        f.write('Subject: Re: Contadores solicitados\n\n')
        f.write(body)

    print('Rascunho gerado em', draft_path)

    # salvar also json mapping for audit
    json_path = f"{args.output_dir}/mapping_{safe_email}.json"
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump({'requested': requested, 'mapping': mapping}, jf, ensure_ascii=False, indent=2)

    print('Mapping salvo em', json_path)

    if args.send:
        # preencher senha com keyring se não informada
        if not (args.smtp_server and args.smtp_user):
            print('Para enviar é necessário --smtp-server e --smtp-user')
            return
        if not args.smtp_pass:
            try:
                import keyring
                stored = keyring.get_password('automotion_smtp', args.smtp_user)
                args.smtp_pass = stored
            except Exception:
                args.smtp_pass = None
        if not args.smtp_pass:
            print('Para enviar é necessário fornecer a senha via --smtp-pass ou armazená-la com store_smtp_creds.py')
            return
        # enviar por SMTP
        from send_test_email import send_email
        subject = 'Re: Contadores solicitados'
        try:
            send_email(args.smtp_server, args.smtp_port, args.smtp_user, args.smtp_pass, to_addr, subject, body)
            print('E-mail enviado com sucesso.')
        except Exception as e:
            print('Falha ao enviar e-mail:', e)


if __name__ == '__main__':
    main()
