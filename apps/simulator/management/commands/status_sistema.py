from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.bombonas.models import Bombona
from apps.coletas.models import Coleta
from apps.alertas.models import Alerta
from apps.empresas.models import Empresa
from apps.authentication.models import User
from django.db.models import Avg, Count, Q
import json


class Command(BaseCommand):
    help = 'Exibe o status completo do sistema IoWaste'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Retorna output em formato JSON'
        )
        parser.add_argument(
            '--resumido',
            action='store_true',
            help='Exibe apenas informações essenciais'
        )

    def handle(self, *args, **options):
        output_json = options['json']
        resumido = options['resumido']
        
        # Coleta dados do sistema
        dados = self.coletar_dados_sistema()
        
        if output_json:
            self.stdout.write(json.dumps(dados, indent=2, default=str))
        else:
            self.exibir_status_visual(dados, resumido)
    
    def coletar_dados_sistema(self):
        """Coleta todos os dados relevantes do sistema"""
        
        # Bombonas
        bombonas_total = Bombona.objects.filter(is_active=True).count()
        bombonas_ativas = Bombona.objects.filter(is_active=True)
        
        # Calcular ocupação média baseada na property
        ocupacao_total = 0
        bombonas_criticas = 0
        bombonas_alerta = 0
        bombonas_ok = 0
        
        for bombona in bombonas_ativas:
            percentual = bombona.percentual_ocupacao
            ocupacao_total += percentual
            
            if percentual >= 80:
                bombonas_criticas += 1
            elif percentual >= 60:
                bombonas_alerta += 1
            else:
                bombonas_ok += 1
        
        ocupacao_media = round(ocupacao_total / bombonas_total, 2) if bombonas_total > 0 else 0
        
        # Coletas
        coletas_hoje = Coleta.objects.filter(
            data_coleta__date=timezone.now().date()
        ).count()
        
        coletas_total = Coleta.objects.count()
        
        # Alertas
        alertas_abertos = Alerta.objects.filter(resolvido=False).count()
        alertas_total = Alerta.objects.count()
        
        # Empresas
        empresas_ativas = Empresa.objects.filter(is_active=True).count()
        
        # Usuários
        usuarios_ativos = User.objects.filter(is_active=True).count()
        
        # Última atividade
        ultima_coleta = Coleta.objects.order_by('-data_coleta').first()
        ultimo_alerta = Alerta.objects.order_by('-created_at').first()
        
        return {
            'timestamp': timezone.now(),
            'bombonas': {
                'total': bombonas_total,
                'ocupacao_media': ocupacao_media,
                'status': {
                    'ok': bombonas_ok,
                    'alerta': bombonas_alerta,
                    'critico': bombonas_criticas
                }
            },
            'coletas': {
                'total': coletas_total,
                'hoje': coletas_hoje
            },
            'alertas': {
                'total': alertas_total,
                'abertos': alertas_abertos
            },
            'empresas': {
                'ativas': empresas_ativas
            },
            'usuarios': {
                'ativos': usuarios_ativos
            },
            'ultima_atividade': {
                'coleta': ultima_coleta.data_coleta if ultima_coleta else None,
                'alerta': ultimo_alerta.created_at if ultimo_alerta else None
            }
        }
    
    def exibir_status_visual(self, dados, resumido=False):
        """Exibe o status de forma visual no terminal"""
        
        timestamp = dados['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        
        # Header
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS(f"🏭 STATUS DO SISTEMA IOWASTE - {timestamp}"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        
        # Bombonas
        bombonas = dados['bombonas']
        self.stdout.write(f"\n📦 BOMBONAS ({bombonas['total']} total)")
        self.stdout.write(f"   📊 Ocupação média: {bombonas['ocupacao_media']}%")
        self.stdout.write(f"   ✅ OK: {bombonas['status']['ok']}")
        self.stdout.write(f"   ⚠️  Alerta: {bombonas['status']['alerta']}")
        self.stdout.write(f"   🚨 Crítico: {bombonas['status']['critico']}")
        
        # Coletas
        coletas = dados['coletas']
        self.stdout.write(f"\n🚛 COLETAS")
        self.stdout.write(f"   📈 Total: {coletas['total']}")
        self.stdout.write(f"   📅 Hoje: {coletas['hoje']}")
        
        # Alertas
        alertas = dados['alertas']
        self.stdout.write(f"\n🔔 ALERTAS")
        self.stdout.write(f"   📊 Total: {alertas['total']}")
        self.stdout.write(f"   🔴 Abertos: {alertas['abertos']}")
        
        if not resumido:
            # Empresas
            empresas = dados['empresas']
            self.stdout.write(f"\n🏢 EMPRESAS")
            self.stdout.write(f"   ✅ Ativas: {empresas['ativas']}")
            
            # Usuários
            usuarios = dados['usuarios']
            self.stdout.write(f"\n👥 USUÁRIOS")
            self.stdout.write(f"   ✅ Ativos: {usuarios['ativos']}")
            
            # Última atividade
            atividade = dados['ultima_atividade']
            self.stdout.write(f"\n⏰ ÚLTIMA ATIVIDADE")
            if atividade['coleta']:
                coleta_str = atividade['coleta'].strftime("%Y-%m-%d %H:%M:%S")
                self.stdout.write(f"   🚛 Coleta: {coleta_str}")
            else:
                self.stdout.write(f"   🚛 Coleta: Nenhuma registrada")
                
            if atividade['alerta']:
                alerta_str = atividade['alerta'].strftime("%Y-%m-%d %H:%M:%S")
                self.stdout.write(f"   🔔 Alerta: {alerta_str}")
            else:
                self.stdout.write(f"   🔔 Alerta: Nenhum registrado")
        
        # Status geral
        self.stdout.write(f"\n🎯 STATUS GERAL")
        if bombonas['status']['critico'] > 0:
            self.stdout.write(self.style.ERROR("   🚨 ATENÇÃO: Bombonas críticas detectadas!"))
        elif bombonas['status']['alerta'] > 0:
            self.stdout.write(self.style.WARNING("   ⚠️  ATENÇÃO: Bombonas em alerta detectadas!"))
        else:
            self.stdout.write(self.style.SUCCESS("   ✅ Sistema operando normalmente"))
            
        if alertas['abertos'] > 0:
            self.stdout.write(self.style.WARNING(f"   🔔 {alertas['abertos']} alertas aguardando resolução"))
        
        self.stdout.write(self.style.SUCCESS("=" * 60))