#!/usr/bin/env python3
"""
Simulador de métricas do GitHub Actions para BuildToValue v7.2
Em produção, substituir por exportador real
"""

from prometheus_client import start_http_server, Gauge, Counter, Histogram
import random
import time
import threading

# Métricas do Pipeline Síncrono
sync_pipeline_duration = Histogram('btv_pipeline_sync_duration_seconds', 
                                  'Duração do pipeline síncrono', 
                                  ['branch', 'status'])
sync_pipeline_failures = Counter('btv_pipeline_sync_failures_total',
                                'Falhas do pipeline síncrono')
sync_pipeline_total = Counter('btv_pipeline_sync_total',
                             'Total de execuções síncronas')

# Métricas do Pipeline Assíncrono  
async_pipeline_duration = Histogram('btv_pipeline_async_duration_seconds',
                                   'Duração do pipeline assíncrono',
                                   ['branch', 'status'])
async_pipeline_failures = Counter('btv_pipeline_async_failures_total',
                                 'Falhas do pipeline assíncrono')
async_pipeline_total = Counter('btv_pipeline_async_total',
                              'Total de execuções assíncronas')

# Métricas de Qualidade
mutation_test_score = Gauge('btv_mutation_test_score',
                           'Score dos mutation tests',
                           ['branch'])
flaky_test_rate = Gauge('btv_flaky_test_rate',
                       'Taxa de testes flaky',
                       ['branch'])
code_coverage = Gauge('btv_code_coverage',
                     'Code coverage por módulo',
                     ['branch', 'module'])

def simulate_pipeline_metrics():
    """Simula métricas dos pipelines"""
    while True:
        # Pipeline Síncrono (rápido)
        duration = random.uniform(120, 180)  # 2-3 minutos
        status = 'success' if random.random() > 0.05 else 'failure'
        
        sync_pipeline_duration.labels(branch='main', status=status).observe(duration)
        sync_pipeline_total.inc()
        if status == 'failure':
            sync_pipeline_failures.inc()

        # Pipeline Assíncrono (lento)
        async_duration = random.uniform(600, 900)  # 10-15 minutos
        async_status = 'success' if random.random() > 0.1 else 'failure'
        
        async_pipeline_duration.labels(branch='main', status=async_status).observe(async_duration)
        async_pipeline_total.inc()
        if async_status == 'failure':
            async_pipeline_failures.inc()

        time.sleep(30)  # Nova métrica a cada 30s

def simulate_quality_metrics():
    """Simula métricas de qualidade"""
    while True:
        # Mutation Test Score (85-95%)
        mutation_test_score.labels(branch='main').set(random.uniform(85, 95))
        
        # Flaky Test Rate (2-8%)
        flaky_test_rate.labels(branch='main').set(random.uniform(0.02, 0.08))
        
        # Code Coverage por módulo
        modules = ['domain', 'application', 'infrastructure', 'ui']
        for module in modules:
            coverage = random.uniform(75, 95)
            code_coverage.labels(branch='main', module=module).set(coverage)

        time.sleep(60)  # Atualiza a cada minuto

if __name__ == '__main__':
    # Iniciar servidor de métricas
    start_http_server(8080)
    print("🚀 Simulador de métricas BuildToValue v7.2 iniciado na porta 8080")

    # Iniciar simulações em threads separadas
    threading.Thread(target=simulate_pipeline_metrics, daemon=True).start()
    threading.Thread(target=simulate_quality_metrics, daemon=True).start()

    # Manter servidor rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Parando simulador...")
