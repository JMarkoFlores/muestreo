import argparse, json, sys, time
from urllib.request import Request, urlopen

def send(url, payload):
    req = Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    with urlopen(req, timeout=15) as r:
        raw = r.read().decode()
        try:
            res = json.loads(raw)
            if res.get('discarded'):
                print(f"  [DESCARTADA] Alerta '{payload['title']}' ({payload['severity'].upper()}): Descartada por politica de filtrado (severidad baja).")
            elif res.get('status') == 'accepted':
                print(f"  [PROCESADA]  Alerta '{payload['title']}' ({payload['severity'].upper()}): Aceptada y procesada. ID asignado: #{res.get('alert_id')}")
            else:
                print(f"  [RESPUESTA]  {res}")
        except Exception:
            print(f"  [{r.status}] {raw}")

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Simulador de alertas Wazuh/OPNsense para SOC-Lite')
    p.add_argument('--url', default='http://localhost:5678/webhook/soc-lite-alert')
    p.add_argument('--count', type=int, default=3)
    p.add_argument('--duplicate', action='store_true', help='Enviar IDs fijos para probar la deteccion de duplicados')
    args = p.parse_args()

    # Si no es prueba de duplicados, generamos un identificador unico por ejecucion
    suffix = "001" if args.duplicate else f"{int(time.time())}"
    
    samples = [
        {
            'external_id': f'SIM-HIGH-{suffix}',
            'source': 'wazuh',
            'title': f'Brute force SSH detectado ({suffix})',
            'description': '12 fallos de autenticacion en 60 segundos detectados por Wazuh',
            'source_ip': '8.8.8.8',
            'destination_ip': '10.0.0.10',
            'severity': 'high'
        },
        {
            'external_id': f'SIM-MED-{suffix}',
            'source': 'opnsense',
            'title': f'Escaneo de puertos TCP ({suffix})',
            'description': 'Conexiones anomalas a multiples puertos detectadas por OPNsense',
            'source_ip': '1.1.1.1',
            'destination_ip': '192.168.1.20',
            'severity': 'medium'
        },
        {
            'external_id': f'SIM-LOW-{suffix}',
            'source': 'wazuh',
            'title': f'Evento informativo ({suffix})',
            'description': 'Cambio rutinario en reglas locales',
            'source_ip': '10.0.0.2',
            'destination_ip': '10.0.0.1',
            'severity': 'low'
        }
    ]

    print(f"\n--- Enviando {min(args.count, len(samples))} alerta(s) de prueba al Webhook de n8n ---")
    if args.duplicate:
        print("Modo: PRUEBA DE DUPLICADOS (IDs estaticos SIM-*-001)")
    else:
        print(f"Modo: ALERTAS NUEVAS EN VIVO (ID unico: {suffix})")

    for item in samples[:args.count]:
        try:
            send(args.url, item)
        except Exception as e:
            print(f'  [ERROR] enviando {item["external_id"]}: {e}', file=sys.stderr)
        time.sleep(0.3)
    
    print("\nCompletado. Ahora haz clic en 'Actualizar' en tu navegador (localhost:5173) para ver los cambios.\n")
