import time
import pandas as pd
import random

# --- Función de estrategia (cópiala de tu app) ---
def estrategia_ind(tipo, banco, monto):
    if tipo == 'Tipo01':
        return 'Interbancario Banamex'
    elif tipo == 'Tipo02':
        if banco == 14:
            return 'Interbancario Banamex'
        elif banco == 12 and monto >= 1000:
            return 'BBVA Matutino'
        else:
            return 'Interbancario Banamex'
    elif tipo == 'Tipo03':
        if monto < 300:
            return 'Interbancario Banamex'
        else:
            return 'BBVA Tradicional'
    elif tipo == 'Tipo04':
        return 'Interbancario Banamex'
    else:
        return 'Sin estrategia'

# 1) Cobertura de combinaciones límite
tipos = ['Tipo01', 'Tipo02', 'Tipo03', 'Tipo04', 'SinTipo']
bancos = [2, 12, 14, 72, 99]     # Banamex, BBVA, Santander, Banorte, Otro
montos = [0, 299, 300, 999, 1000, 5000]

combos = []
for t in tipos:
    for b in bancos:
        for m in montos:
            pred = estrategia_ind(t, b, m)
            combos.append({
                'TipoCliente': t,
                'idBanco': b,
                'montoExigible': m,
                'Estrategia': pred
            })

combos_df = pd.DataFrame(combos)
coverage = combos_df.groupby(['TipoCliente', 'idBanco'])['Estrategia'] \
                    .agg(lambda x: ', '.join(sorted(set(x)))) \
                    .reset_index()
print("=== Cobertura de Estrategias por (TipoCliente, idBanco) ===")
print(coverage.to_string(index=False))

# 2) Benchmark de velocidad
N = 100_000
sample_data = pd.DataFrame({
    'TipoCliente': [random.choice(tipos) for _ in range(N)],
    'idBanco':      [random.choice(bancos) for _ in range(N)],
    'montoExigible': [random.choice(montos) for _ in range(N)],
})

start = time.time()
sample_data['Estrategia'] = sample_data.apply(
    lambda r: estrategia_ind(r['TipoCliente'], r['idBanco'], r['montoExigible']),
    axis=1
)
elapsed = time.time() - start
print(f"\nProcesadas {N} filas en {elapsed:.3f} s — {N/elapsed:.0f} filas/s")

# 3) Distribución de estrategias en la muestra
dist = sample_data['Estrategia'].value_counts().reset_index()
dist.columns = ['Estrategia', 'Count']
print("\n=== Distribución de Estrategias en la muestra ===")
print(dist.to_string(index=False))
