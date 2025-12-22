from pysnmp.hlapi import *
import threading

# Standard Printer MIB OID for Total Pages (prtMarkerLifeCount)
OID_TOTAL_PAGES = '1.3.6.1.2.1.43.10.2.1.4.1.1'
DEFAULT_COMMUNITY = 'public'
DEFAULT_PORT = 161

def get_printer_counter(ip_address, community=DEFAULT_COMMUNITY, timeout=1, retries=1):
    """
    Queries the printer at ip_address for its total page count.
    Returns the integer count or None if unreachable/error.
    """
    print(f"[SNMP] Querying {ip_address}...")
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1), # SNMP v2c
            UdpTransportTarget((ip_address, DEFAULT_PORT), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(OID_TOTAL_PAGES))
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            print(f"[SNMP] Error checking {ip_address}: {errorIndication}")
            return None
        elif errorStatus:
            print(f"[SNMP] Error Status at {ip_address}: {errorStatus.prettyPrint()}")
            return None
        else:
            for varBind in varBinds:
                # varBind is (OID, Value)
                val = varBind[1]
                # Try to convert to int explicitly
                try:
                    return int(val)
                except:
                    print(f"[SNMP] Could not convert value {val} to int")
                    return None
                    
    except Exception as e:
        print(f"[SNMP] Exception querying {ip_address}: {e}")
        return None

def scan_and_update_db(printers_list, update_callback=None):
    from .db import insert_counter
    from datetime import datetime
    
    updates_made = 0
    errors = []
    
    for p in printers_list:
        raw_model = p.get('model', '')
        printer_id = p.get('printer_id')
        
        # Extract IP
        ip = None
        if "|" in raw_model:
            parts = raw_model.split("|")
            if len(parts) > 2:
                ip = parts[2].strip()
        
        if ip:
            # Try getting counter
            result = get_printer_counter(ip)
            
            if isinstance(result, int):
                print(f"[SNMP] Success {ip}: {result}")
                insert_counter(printer_id, raw_model, result, datetime.now())
                updates_made += 1
            else:
                # result is error message or None
                error_msg = str(result) if result else "Sem resposta"
                print(f"[SNMP] Fail {ip}: {error_msg}")
                errors.append(f"{ip}: {error_msg}")
    
    return updates_made, errors

def get_printer_counter(ip_address, community=DEFAULT_COMMUNITY, timeout=2, retries=1): # Increased timeout
    print(f"[SNMP] Querying {ip_address}...")
    try:
        # Using pysnmp synchronous getCmd
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1), # v2c
            UdpTransportTarget((ip_address, DEFAULT_PORT), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(OID_TOTAL_PAGES))
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            return f"Erro de Conexão: {errorIndication}"
        elif errorStatus:
            return f"Erro SNMP: {errorStatus.prettyPrint()}"
        else:
            for varBind in varBinds:
                val = varBind[1]
                try:
                    return int(val)
                except:
                    return f"Valor inválido recebido: {val}"
        return "Nenhum dado retornado"
                    
    except Exception as e:
        return f"Exceção: {str(e)}"
