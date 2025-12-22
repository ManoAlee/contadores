#!/usr/bin/env python3
"""Launcher GUI refinada para consultas SNMP, geração de rascunhos e envio de e-mail.

Funcionalidades:
- Aba "Consultas" para executar SNMP em lote
- Aba "Rascunho & Envio" para gerar rascunhos a partir de um e-mail e enviar
- Aba "Histórico" para visualizar execuções anteriores
- Aba "Config" para ajustar SNMP/SMTP
"""
import os
import sys
import json
import threading
from pathlib import Path

# garantir que app/src esteja no path quando executado a partir da raiz
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'app' / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import PySimpleGUI as sg
except Exception:
    print('PySimpleGUI não encontrado. Instale com: pip install PySimpleGUI')
    raise

from get_printer_counters import load_ips, query_printer
from auto_reply_from_email import extract_email, extract_serials, compose_reply, normalize_serial, build_serial_to_counter_map
from send_email import send_email
from config import load_config, save_config, get as cfg_get, set_config

DATA_DIR = ROOT / 'app' / 'data'
HISTORY_FILE = DATA_DIR / 'history.json'


def append_history(record: dict):
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                arr = json.load(f)
        else:
            arr = []
        arr.insert(0, record)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(arr, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_history():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        return []
    return []


def run_snmp(ips_path, community, window):
    try:
        ips = load_ips(ips_path)
    except Exception as e:
        sg.popup_error('Erro ao carregar IPs', str(e))
        return
    window['-LOG-'].print(f'Iniciando consultas SNMP ({len(ips)} hosts) ...')
    results = []
    for name, ip in ips:
        window['-LOG-'].print(f'Consultando {ip} ...')
        res = query_printer(ip, community)
        if name:
            res['location'] = name
        results.append(res)
    window['-LOG-'].print('Consultas finalizadas.')
    window['-LOG-'].print(json.dumps(results, ensure_ascii=False, indent=2))
    append_history({'type': 'snmp_run', 'ips_file': ips_path, 'community': community, 'results': results})


def generate_and_optionally_send(email_file, ips_file, community, output_dir, smtp_cfg, send_now, window):
    try:
        with open(email_file, 'r', encoding='utf-8') as f:
            email_text = f.read()
    except Exception as e:
        sg.popup_error('Erro ao ler e-mail', str(e))
        return
    to_addr = extract_email(email_text)
    serials = extract_serials(email_text)
    if not to_addr or not serials:
        sg.popup_error('Não foi possível extrair email ou seriais do arquivo.')
        return
    window['-LOG-'].print(f'Encontrado email {to_addr} e seriais: {serials}')
    ips = load_ips(ips_file)
    mapping = build_serial_to_counter_map(ips, community)
    requested = [normalize_serial(s) for s in serials]
    body = compose_reply(to_addr, requested, mapping)
    safe_email = to_addr.replace('@', '_at_').replace('.', '_')
    out_path = os.path.join(output_dir, f'draft_{safe_email}.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'To: {to_addr}\n')
        f.write('Subject: Re: Contadores solicitados\n\n')
        f.write(body)
    json_path = os.path.join(output_dir, f'mapping_{safe_email}.json')
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump({'requested': requested, 'mapping': mapping}, jf, ensure_ascii=False, indent=2)
    window['-LOG-'].print('Rascunho salvo em: ' + out_path)
    window['-LOG-'].print('Mapping salvo em: ' + json_path)
    record = {'type': 'draft', 'email': to_addr, 'draft': out_path, 'mapping': json_path}
    if send_now:
        try:
            send_email(smtp_cfg['server'], int(smtp_cfg['port']), smtp_cfg['user'], smtp_cfg['pass'], to_addr, 'Re: Contadores solicitados', body, use_ssl=smtp_cfg.get('ssl', True))
            window['-LOG-'].print('E-mail enviado com sucesso para ' + to_addr)
            record['sent'] = True
        except Exception as e:
            window['-LOG-'].print('Falha ao enviar e-mail: ' + str(e))
            record['sent'] = False
            record['error'] = str(e)
    append_history(record)


def build_gui():
    # carregar tema salvo
    theme = load_config().get('theme', 'SystemDefault')
    # nem todas as versões de PySimpleGUI expõem `theme()` da mesma forma;
    # tentar aplicar, mas ignorar se não disponível
    try:
        if hasattr(sg, 'theme'):
            sg.theme(theme)
    except Exception:
        # se falhar, continuar sem lançar erro
        pass
    tabs = [
        [sg.Text('Arquivo de IPs:'), sg.InputText(str(DATA_DIR / 'ips.txt'), key='-IPS-'), sg.FileBrowse(target='-IPS-')],
        [sg.Text('Comunidade SNMP:'), sg.InputText('public', key='-COMM-'), sg.Button('Executar SNMP', key='-RUN_SNMP-')],
    ]

    draft_tab = [
        [sg.Text('Arquivo de e-mail (fonte):'), sg.InputText(str(DATA_DIR / 'incoming_email.txt'), key='-EMAIL-'), sg.FileBrowse(target='-EMAIL-')],
        [sg.Text('Pasta de saída:'), sg.InputText(str(DATA_DIR), key='-OUT-'), sg.FolderBrowse(target='-OUT-')],
        [sg.Checkbox('Enviar agora via SMTP', key='-SEND_NOW-'), sg.Button('Gerar rascunho', key='-GEN_DRAFT-')],
    ]

    # carregar cfg salvo
    cfg = load_config()
    smtp_tab = [
        [sg.Text('SMTP Server'), sg.InputText(cfg.get('smtp_server', 'smtp.example.com'), key='-SMTP_SERVER-')],
        [sg.Text('Porta'), sg.InputText(cfg.get('smtp_port', '465'), key='-SMTP_PORT-')],
        [sg.Text('Usuário'), sg.InputText(cfg.get('smtp_user', ''), key='-SMTP_USER-')],
        [sg.Text('Senha'), sg.InputText('', key='-SMTP_PASS-', password_char='*')],
        [sg.Checkbox('Usar SSL', default=cfg.get('smtp_ssl', True), key='-SMTP_SSL-')],
        [sg.Button('Salvar Config', key='-SAVE_CFG-')],
    ]

    history_column = [
        [sg.Listbox(values=[h.get('type', '') + ' - ' + (h.get('email') or h.get('ips_file') or '') for h in load_history()], size=(60, 10), key='-HIST_LIST-')],
        [sg.Button('Abrir selecção', key='-HIST_OPEN-'), sg.Button('Limpar histórico', key='-HIST_CLEAR-')],
    ]

    layout = [
        [sg.TabGroup([[
            sg.Tab('Consultas', tabs),
            sg.Tab('Rascunho & Envio', draft_tab),
            sg.Tab('SMTP / Config', smtp_tab),
            sg.Tab('Histórico', history_column),
        ]])],
        [sg.Multiline('', size=(100, 20), autoscroll=True, key='-LOG-')],
        [sg.Button('Sair')]
    ]

    return sg.Window('Contadores - Launcher (Refinado)', layout, finalize=True)


def main():
    window = build_gui()

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Sair'):
            break
        if event == '-RUN_SNMP-':
            ips_path = values['-IPS-']
            comm = values['-COMM-']
            t = threading.Thread(target=run_snmp, args=(ips_path, comm, window), daemon=True)
            t.start()
        if event == '-GEN_DRAFT-':
            send_now = values.get('-SEND_NOW-', False)
            smtp_cfg = {'server': values.get('-SMTP_SERVER-'), 'port': values.get('-SMTP_PORT-'), 'user': values.get('-SMTP_USER-'), 'pass': values.get('-SMTP_PASS-'), 'ssl': values.get('-SMTP_SSL-')}
            # validações básicas
            if not values['-EMAIL-'] or not values['-IPS-']:
                sg.popup_error('Arquivo de e-mail e arquivo de IPs são obrigatórios.')
            else:
                t = threading.Thread(target=generate_and_optionally_send, args=(values['-EMAIL-'], values['-IPS-'], values['-COMM-'], values['-OUT-'], smtp_cfg, send_now, window), daemon=True)
                t.start()
        if event == '-SAVE_CFG-':
            # validar porta
            port = values.get('-SMTP_PORT-')
            try:
                int(port)
            except Exception:
                sg.popup_error('Porta SMTP inválida')
                continue
            # não depender de `sg.theme()` estar disponível; salvar o tema carregado
            cfg_to_save = {'smtp_server': values.get('-SMTP_SERVER-'), 'smtp_port': values.get('-SMTP_PORT-'), 'smtp_user': values.get('-SMTP_USER-'), 'smtp_ssl': values.get('-SMTP_SSL-'), 'theme': theme}
            try:
                save_config(cfg_to_save)
                sg.popup('Config salva')
            except Exception as e:
                sg.popup_error('Falha ao salvar config: ' + str(e))
        if event == '-HIST_CLEAR-':
            try:
                if HISTORY_FILE.exists():
                    HISTORY_FILE.unlink()
                window['-HIST_LIST-'].update(values=[])
                window['-LOG-'].print('Histórico limpo.')
            except Exception as e:
                window['-LOG-'].print('Falha ao limpar histórico: ' + str(e))
        if event == '-HIST_OPEN-':
            sel = values.get('-HIST_LIST-')
            if sel:
                # apenas mostrar no log (poderia abrir arquivo)
                idx = values['-HIST_LIST-'][0]
                window['-LOG-'].print('Selecionado: ' + idx)

    window.close()


if __name__ == '__main__':
    main()
