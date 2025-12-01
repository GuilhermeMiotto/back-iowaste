"""
Simulador IoT para bombonas de resíduos
Simula leituras de sensores de peso e temperatura
"""
import random
from decimal import Decimal
from django.utils import timezone
from apps.bombonas.models import Bombona, LeituraSensor
from apps.alertas.models import Alerta


class IoTSimulator:
    """Classe para simular leituras de sensores IoT"""
    
    def __init__(self):
        self.temperatura_base = 25.0
        self.temperatura_variacao = 5.0
        self.peso_incremento_min = 0.5
        self.peso_incremento_max = 3.0
    
    def simular_leitura_bombona(self, bombona):
        """Simula uma leitura de sensores para uma bombona específica"""
        
        if not bombona.is_active:
            return None
        
        # Simular incremento de peso (lixo sendo adicionado)
        incremento_peso = Decimal(random.uniform(
            self.peso_incremento_min,
            self.peso_incremento_max
        ))
        
        # Atualizar peso (não ultrapassar capacidade)
        novo_peso = bombona.peso_atual + incremento_peso
        if novo_peso > bombona.capacidade:
            novo_peso = bombona.capacidade
        
        # Simular temperatura com variação
        variacao = random.uniform(-self.temperatura_variacao, self.temperatura_variacao)
        nova_temperatura = Decimal(self.temperatura_base + variacao)
        
        # Atualizar bombona
        bombona.peso_atual = novo_peso
        bombona.temperatura = nova_temperatura
        bombona.ultima_leitura = timezone.now()
        bombona.save()
        
        # Atualizar status automaticamente
        bombona.atualizar_status()
        
        # Criar registro de leitura
        leitura = LeituraSensor.objects.create(
            bombona=bombona,
            peso=novo_peso,
            temperatura=nova_temperatura,
            simulado=True
        )
        
        # Verificar e gerar alertas
        self.verificar_alertas(bombona)
        
        return leitura
    
    def verificar_alertas(self, bombona):
        """Verifica condições e gera alertas se necessário"""
        
        percentual = bombona.percentual_ocupacao
        
        # Alerta de nível crítico (>= 95%)
        if percentual >= 95:
            # Verificar se já existe alerta não resolvido
            alerta_existente = Alerta.objects.filter(
                bombona=bombona,
                tipo='nivel_critico',
                resolvido=False
            ).exists()
            
            if not alerta_existente:
                Alerta.objects.create(
                    bombona=bombona,
                    tipo='nivel_critico',
                    nivel='critico',
                    descricao=f'Bombona {bombona.identificacao} atingiu {percentual:.1f}% de capacidade. Coleta urgente necessária!'
                )
        
        # Alerta de nível alto (>= 80%)
        elif percentual >= 80:
            alerta_existente = Alerta.objects.filter(
                bombona=bombona,
                tipo='nivel_alto',
                resolvido=False
            ).exists()
            
            if not alerta_existente:
                Alerta.objects.create(
                    bombona=bombona,
                    tipo='nivel_alto',
                    nivel='alto',
                    descricao=f'Bombona {bombona.identificacao} atingiu {percentual:.1f}% de capacidade. Agendar coleta em breve.'
                )
        
        # Alerta de temperatura alta (> 40°C)
        if float(bombona.temperatura) > 40.0:
            alerta_existente = Alerta.objects.filter(
                bombona=bombona,
                tipo='temperatura_alta',
                resolvido=False
            ).exists()
            
            if not alerta_existente:
                Alerta.objects.create(
                    bombona=bombona,
                    tipo='temperatura_alta',
                    nivel='medio',
                    descricao=f'Bombona {bombona.identificacao} com temperatura elevada: {bombona.temperatura}°C'
                )
    
    def simular_todas_bombonas(self):
        """Simula leituras para todas as bombonas ativas"""
        
        bombonas = Bombona.objects.filter(is_active=True)
        leituras_criadas = 0
        alertas_criados = 0
        
        for bombona in bombonas:
            # Decidir aleatoriamente se simula leitura (80% de chance)
            if random.random() < 0.8:
                leitura = self.simular_leitura_bombona(bombona)
                if leitura:
                    leituras_criadas += 1
        
        # Contar alertas não resolvidos
        alertas_criados = Alerta.objects.filter(resolvido=False).count()
        
        return {
            'bombonas_processadas': bombonas.count(),
            'leituras_criadas': leituras_criadas,
            'alertas_abertos': alertas_criados,
        }
    
    def resetar_bombona(self, bombona):
        """Reseta uma bombona para peso zero (simula esvaziamento)"""
        
        bombona.peso_atual = Decimal('0.0')
        bombona.status = 'normal'
        bombona.save()
        
        # Resolver alertas abertos
        Alerta.objects.filter(
            bombona=bombona,
            resolvido=False
        ).update(
            resolvido=True,
            data_resolucao=timezone.now(),
            observacoes_resolucao='Bombona esvaziada - reset automático'
        )
    
    def popular_dados_exemplo(self):
        """Popula o sistema com dados de exemplo para demonstração - REGIÃO DO PARANÁ"""
        
        from apps.empresas.models import Empresa
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # EMPRESAS DA REGIÃO DO PARANÁ
        empresas_parana = [
            {
                'cnpj': '75.123.456/0001-10',
                'nome': 'Hospital e Maternidade São Francisco - Cianorte',
                'razao_social': 'Hospital e Maternidade São Francisco LTDA',
                'endereco': 'Av. Souza Naves',
                'numero': '1234',
                'bairro': 'Centro',
                'cidade': 'Cianorte',
                'estado': 'PR',
                'cep': '87200-000',
                'telefone': '(44) 3619-2000',
                'email': 'residuos@hospitalsaofrancisco.com.br',
                'responsavel': 'Dr. Carlos Eduardo Silva',
            },
            {
                'cnpj': '75.234.567/0001-11',
                'nome': 'Hospital Universitário Regional de Maringá - UEM',
                'razao_social': 'Hospital Universitário UEM',
                'endereco': 'Av. Mandacaru',
                'numero': '1590',
                'bairro': 'Zona 7',
                'cidade': 'Maringá',
                'estado': 'PR',
                'cep': '87083-240',
                'telefone': '(44) 3011-9000',
                'email': 'meio.ambiente@huem.uem.br',
                'responsavel': 'Dra. Maria Helena Costa',
            },
            {
                'cnpj': '75.345.678/0001-12',
                'nome': 'Santa Casa de Maringá',
                'razao_social': 'Santa Casa de Misericórdia de Maringá',
                'endereco': 'Rua XV de Novembro',
                'numero': '1423',
                'bairro': 'Centro',
                'cidade': 'Maringá',
                'estado': 'PR',
                'cep': '87013-230',
                'telefone': '(44) 3027-3434',
                'email': 'sustentabilidade@santacasamaringa.com.br',
                'responsavel': 'Dr. João Pedro Almeida',
            },
            {
                'cnpj': '75.456.789/0001-13',
                'nome': 'Hospital São Paulo - Umuarama',
                'razao_social': 'Hospital São Paulo LTDA',
                'endereco': 'Av. Rio Branco',
                'numero': '3355',
                'bairro': 'Centro',
                'cidade': 'Umuarama',
                'estado': 'PR',
                'cep': '87501-130',
                'telefone': '(44) 3621-3000',
                'email': 'residuos@hospitalsaopaulo-uma.com.br',
                'responsavel': 'Dra. Ana Paula Fernandes',
            },
            {
                'cnpj': '75.567.890/0001-14',
                'nome': 'Hospital e Maternidade Paraná - Paranavaí',
                'razao_social': 'Hospital Paraná LTDA',
                'endereco': 'Rua Getúlio Vargas',
                'numero': '777',
                'bairro': 'Centro',
                'cidade': 'Paranavaí',
                'estado': 'PR',
                'cep': '87705-020',
                'telefone': '(44) 3423-1500',
                'email': 'gestao.residuos@hospitalparana.com.br',
                'responsavel': 'Dr. Roberto Lima Santos',
            },
            {
                'cnpj': '75.678.901/0001-15',
                'nome': 'Clínica e Hospital São Vicente - Campo Mourão',
                'razao_social': 'Hospital São Vicente LTDA',
                'endereco': 'Av. Capitão Índio Bandeira',
                'numero': '1050',
                'bairro': 'Centro',
                'cidade': 'Campo Mourão',
                'estado': 'PR',
                'cep': '87301-020',
                'telefone': '(44) 3518-2000',
                'email': 'meio.ambiente@saovicente-cm.com.br',
                'responsavel': 'Dra. Juliana Martins',
            },
            {
                'cnpj': '75.789.012/0001-16',
                'nome': 'Hospital Regional do Noroeste - Paranavaí',
                'razao_social': 'Hospital Regional do Noroeste do PR',
                'endereco': 'Rua Piauí',
                'numero': '550',
                'bairro': 'Centro',
                'cidade': 'Paranavaí',
                'estado': 'PR',
                'cep': '87703-030',
                'telefone': '(44) 3045-3000',
                'email': 'residuos@hospitalregional.pr.gov.br',
                'responsavel': 'Dr. Fernando Oliveira',
            },
            {
                'cnpj': '75.890.123/0001-17',
                'nome': 'Hospital Santa Rita - Maringá',
                'razao_social': 'Hospital Santa Rita LTDA',
                'endereco': 'Av. Colombo',
                'numero': '2222',
                'bairro': 'Zona 7',
                'cidade': 'Maringá',
                'estado': 'PR',
                'cep': '87020-030',
                'telefone': '(44) 3031-7000',
                'email': 'sustentabilidade@santarita.com.br',
                'responsavel': 'Dra. Patricia Souza',
            },
        ]
        
        # Criar empresas
        empresas_criadas = []
        for emp_data in empresas_parana:
            empresa, created = Empresa.objects.get_or_create(
                cnpj=emp_data['cnpj'],
                defaults=emp_data
            )
            empresas_criadas.append(empresa)
        
        # BOMBONAS - 12 TOTAL (Cianorte:2, Maringá:6, Umuarama:1, Paranavaí:2, Campo Mourão:1)
        bombonas_config = [
            # Cianorte (2)
            {
                'identificacao': 'CNT-HOS-001',
                'empresa': empresas_criadas[0],  # Cianorte
                'lat': -23.6636,
                'lng': -52.6056,
                'endereco': 'Av. Souza Naves, 1234 - UTI Ala A',
                'tipo': 'hospitalar_infectante'
            },
            {
                'identificacao': 'CNT-HOS-002',
                'empresa': empresas_criadas[0],  # Cianorte
                'lat': -23.6640,
                'lng': -52.6050,
                'endereco': 'Av. Souza Naves, 1234 - Centro Cirúrgico',
                'tipo': 'hospitalar_perfurocortante'
            },
            # Maringá UEM (2)
            {
                'identificacao': 'MGA-UEM-001',
                'empresa': empresas_criadas[1],  # Maringá UEM
                'lat': -23.4205,
                'lng': -51.9331,
                'endereco': 'Av. Mandacaru, 1590 - Pronto Socorro',
                'tipo': 'hospitalar_infectante'
            },
            {
                'identificacao': 'MGA-UEM-002',
                'empresa': empresas_criadas[1],  # Maringá UEM
                'lat': -23.4209,
                'lng': -51.9335,
                'endereco': 'Av. Mandacaru, 1590 - Laboratório',
                'tipo': 'hospitalar_quimico'
            },
            # Maringá Santa Casa (2)
            {
                'identificacao': 'MGA-STC-001',
                'empresa': empresas_criadas[2],  # Santa Casa
                'lat': -23.4252,
                'lng': -51.9392,
                'endereco': 'Rua XV de Novembro, 1423 - Emergência',
                'tipo': 'hospitalar_infectante'
            },
            {
                'identificacao': 'MGA-STC-002',
                'empresa': empresas_criadas[2],  # Santa Casa
                'lat': -23.4248,
                'lng': -51.9388,
                'endereco': 'Rua XV de Novembro, 1423 - Maternidade',
                'tipo': 'hospitalar_perfurocortante'
            },
            # Umuarama (1)
            {
                'identificacao': 'UMU-HOS-001',
                'empresa': empresas_criadas[3],  # Umuarama
                'lat': -23.7665,
                'lng': -53.3250,
                'endereco': 'Av. Rio Branco, 3355 - Central',
                'tipo': 'hospitalar_infectante'
            },
            # Paranavaí Hospital Paraná (1)
            {
                'identificacao': 'PNV-PAR-001',
                'empresa': empresas_criadas[4],  # Paranavaí Hospital Paraná
                'lat': -23.0732,
                'lng': -52.4652,
                'endereco': 'Rua Getúlio Vargas, 777 - Ala Sul',
                'tipo': 'hospitalar_infectante'
            },
            # Campo Mourão (1)
            {
                'identificacao': 'CMO-SVC-001',
                'empresa': empresas_criadas[5],  # Campo Mourão
                'lat': -24.0462,
                'lng': -52.3786,
                'endereco': 'Av. Capitão Índio Bandeira, 1050',
                'tipo': 'hospitalar_quimico'
            },
            # Paranavaí Regional (1)
            {
                'identificacao': 'PNV-REG-001',
                'empresa': empresas_criadas[6],  # Paranavaí Regional
                'lat': -23.0777,
                'lng': -52.4585,
                'endereco': 'Rua Piauí, 550 - Ala Norte',
                'tipo': 'hospitalar_perfurocortante'
            },
            # Maringá Santa Rita (2)
            {
                'identificacao': 'MGA-STR-001',
                'empresa': empresas_criadas[7],  # Santa Rita
                'lat': -23.4095,
                'lng': -51.9552,
                'endereco': 'Av. Colombo, 2222 - UTI',
                'tipo': 'hospitalar_infectante'
            },
            {
                'identificacao': 'MGA-STR-002',
                'empresa': empresas_criadas[7],  # Santa Rita
                'lat': -23.4099,
                'lng': -51.9548,
                'endereco': 'Av. Colombo, 2222 - Centro Cirúrgico',
                'tipo': 'hospitalar_quimico'
            },
        ]
        
        # Criar bombonas
        bombonas_criadas = 0
        for config in bombonas_config:
            _, created = Bombona.objects.get_or_create(
                identificacao=config['identificacao'],
                defaults={
                    'empresa': config['empresa'],
                    'latitude': Decimal(str(config['lat'])),
                    'longitude': Decimal(str(config['lng'])),
                    'endereco_instalacao': config['endereco'],
                    'capacidade': Decimal('200.0'),
                    'tipo_residuo': config['tipo'],
                    'peso_atual': Decimal('0.0'),
                    'data_instalacao': timezone.now().date(),
                }
            )
            if created:
                bombonas_criadas += 1
        
        return f'Criadas {len(empresas_criadas)} empresas e {bombonas_criadas} bombonas na região do Paraná'


# Instância global do simulador
simulator = IoTSimulator()
