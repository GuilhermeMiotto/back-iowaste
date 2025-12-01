from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.simulator.simulator import simulator
import time
import signal
import sys


class Command(BaseCommand):
    help = 'Inicia o simulador IoT para bombonas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--intervalo',
            type=int,
            default=300,
            help='Intervalo entre execuções em segundos'
        )
        parser.add_argument(
            '--executar-uma-vez',
            action='store_true',
            help='Executa apenas uma vez'
        )
        parser.add_argument(
            '--modo-rapido',
            action='store_true',
            help='Modo rápido (30s entre execuções)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas'
        )

    def handle(self, *args, **options):
        intervalo = options['intervalo']
        executar_uma_vez = options['executar_uma_vez']
        modo_rapido = options['modo_rapido']
        verbose = options['verbose']
        
        if modo_rapido:
            intervalo = 30
        
        def signal_handler(sig, frame):
            self.stdout.write(self.style.WARNING('\nSimulador interrompido'))
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        self.stdout.write(self.style.SUCCESS(f'Iniciando simulador IoT (intervalo: {intervalo}s)'))
        
        if executar_uma_vez:
            resultado = simulator.simular_todas_bombonas()
            self.exibir_resultado(resultado, verbose)
        else:
            contador = 0
            try:
                while True:
                    contador += 1
                    inicio = time.time()
                    resultado = simulator.simular_todas_bombonas()
                    fim = time.time()
                    
                    self.exibir_resultado(resultado, verbose, contador, fim - inicio)
                    
                    if verbose:
                        self.stdout.write(f'Aguardando {intervalo} segundos...\n')
                    
                    time.sleep(intervalo)
                    
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING(f'\nInterrompido após {contador} execuções'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\nErro: {str(e)}'))
    
    def exibir_resultado(self, resultado, verbose=False, execucao=None, tempo=None):
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if execucao:
            header = f'Execução #{execucao} - {timestamp}'
        else:
            header = f'Simulação - {timestamp}'
            
        if tempo:
            header += f' ({tempo:.2f}s)'
        
        self.stdout.write(self.style.SUCCESS(header))
        
        if verbose:
            self.stdout.write(f'  Bombonas: {resultado["bombonas_processadas"]}')
            self.stdout.write(f'  Leituras: {resultado["leituras_criadas"]}')
            self.stdout.write(f'  Alertas: {resultado["alertas_abertos"]}')
        else:
            self.stdout.write(
                f'  {resultado["bombonas_processadas"]} bombonas | '
                f'{resultado["leituras_criadas"]} leituras | '
                f'{resultado["alertas_abertos"]} alertas'
            )
