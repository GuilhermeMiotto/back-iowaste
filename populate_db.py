#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de exemplo
Execute: python manage.py shell < populate_db.py
"""

import os
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.authentication.models import User
from apps.empresas.models import Empresa
from apps.bombonas.models import Bombona
from apps.coletas.models import Coleta
from apps.alertas.models import Alerta

def create_users():
    """Criar usuários de exemplo"""
    users_data = [
        {
            'username': 'admin_sistema',
            'email': 'admin@iowaste.com',
            'password': '123456',
            'first_name': 'Administrador',
            'last_name': 'Sistema',
            'tipo_usuario': 'admin',
            'telefone': '(11) 99999-0001'
        },
        {
            'username': 'operador1',
            'email': 'operador1@iowaste.com',
            'password': '123456',
            'first_name': 'João',
            'last_name': 'Silva',
            'tipo_usuario': 'operador',
            'telefone': '(11) 99999-0002'
        },
        {
            'username': 'fiscal1',
            'email': 'fiscal1@prefeitura.sp.gov.br',
            'password': '123456',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'tipo_usuario': 'fiscal',
            'telefone': '(11) 99999-0003'
        },
        {
            'username': 'empresa_petrobras',
            'email': 'contato@petrobras.com.br',
            'password': '123456',
            'first_name': 'Representante',
            'last_name': 'Petrobras',
            'tipo_usuario': 'empresa',
            'telefone': '(11) 99999-0004'
        },
        {
            'username': 'empresa_shell',
            'email': 'contato@shell.com.br',
            'password': '123456',
            'first_name': 'Representante',
            'last_name': 'Shell',
            'tipo_usuario': 'empresa',
            'telefone': '(11) 99999-0005'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            created_users.append(user)
            print(f"✓ Usuário criado: {user.email}")
        else:
            print(f"• Usuário já existe: {user.email}")
    
    return created_users

def create_empresas():
    """Criar empresas de exemplo"""
    empresas_data = [
        {
            'nome': 'Petrobras Distribuidora S.A.',
            'cnpj': '02.342.900/0001-30',
            'razao_social': 'Petrobras Distribuidora S.A.',
            'email': 'contato@petrobras.com.br',
            'telefone': '(11) 3456-7890',
            'endereco': 'Av. Paulista',
            'numero': '1000',
            'bairro': 'Bela Vista',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '01310-100',
            'responsavel': 'Carlos Eduardo Silva',
            'atividade_principal': 'Distribuição de combustíveis',
            'is_active': True
        },
        {
            'nome': 'Shell Brasil Ltda.',
            'cnpj': '34.155.892/0001-52',
            'razao_social': 'Shell Brasil Ltda.',
            'email': 'contato@shell.com.br',
            'telefone': '(11) 2345-6789',
            'endereco': 'Rua dos Petrolíferos',
            'numero': '500',
            'bairro': 'Vila Olímpia',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '04567-890',
            'responsavel': 'Ana Paula Costa',
            'atividade_principal': 'Distribuição de combustíveis',
            'is_active': True
        },
        {
            'nome': 'Ipiranga Produtos de Petróleo S.A.',
            'cnpj': '33.337.122/0001-91',
            'razao_social': 'Ipiranga Produtos de Petróleo S.A.',
            'email': 'sustentabilidade@ipiranga.com.br',
            'telefone': '(11) 3456-1234',
            'endereco': 'Av. das Nações Unidas',
            'numero': '17007',
            'bairro': 'Vila Almeida',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '04795-100',
            'responsavel': 'Roberto Mendes',
            'atividade_principal': 'Distribuição de combustíveis',
            'is_active': True
        },
        {
            'nome': 'BR Distribuidora S.A.',
            'cnpj': '07.526.557/0001-00',
            'razao_social': 'BR Distribuidora S.A.',
            'email': 'meio.ambiente@br.com.br',
            'telefone': '(21) 3876-5432',
            'endereco': 'Praia de Botafogo',
            'numero': '228',
            'bairro': 'Botafogo',
            'cidade': 'Rio de Janeiro',
            'estado': 'RJ',
            'cep': '22250-145',
            'responsavel': 'Fernanda Lima',
            'atividade_principal': 'Distribuição de combustíveis',
            'is_active': True
        },
        {
            'nome': 'Raízen S.A.',
            'cnpj': '15.115.581/0001-87',
            'razao_social': 'Raízen S.A.',
            'email': 'gestao.residuos@raizen.com.br',
            'telefone': '(11) 4567-8901',
            'endereco': 'Rua Fidêncio Ramos',
            'numero': '308',
            'bairro': 'Vila Olímpia',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'cep': '04551-010',
            'responsavel': 'Eduardo Santos',
            'atividade_principal': 'Distribuição de combustíveis',
            'is_active': True
        }
    ]
    
    created_empresas = []
    for empresa_data in empresas_data:
        empresa, created = Empresa.objects.get_or_create(
            cnpj=empresa_data['cnpj'],
            defaults=empresa_data
        )
        if created:
            created_empresas.append(empresa)
            print(f"✓ Empresa criada: {empresa.nome}")
        else:
            print(f"• Empresa já existe: {empresa.nome}")
    
    return created_empresas

def create_bombonas(empresas):
    """Criar bombonas para as empresas"""
    capacidades = [50, 100, 200, 500, 1000]  # Quilogramas
    tipos_residuo = ['quimico', 'perigoso', 'reciclavel', 'organico', 'eletronico']
    
    created_bombonas = []
    
    for empresa in empresas:
        # Cada empresa terá entre 8 e 15 bombonas
        num_bombonas = random.randint(8, 15)
        print(f"Criando {num_bombonas} bombonas para {empresa.nome}")
        
        for i in range(num_bombonas):
            identificacao = f"{empresa.cnpj[:8]}-{str(i+1).zfill(3)}"
            capacidade = random.choice(capacidades)
            
            bombona_data = {
                'identificacao': identificacao,
                'empresa': empresa,
                'tipo_residuo': random.choice(tipos_residuo),
                'capacidade': capacidade,
                'peso_atual': round(random.uniform(0, capacidade * 0.9), 2),
                'latitude': round(random.uniform(-23.7, -23.4), 6),  # São Paulo region
                'longitude': round(random.uniform(-46.8, -46.3), 6),
                'endereco_instalacao': f"Setor {chr(65+i)}, Galpão {i+1}",
                'data_instalacao': (datetime.now() - timedelta(days=random.randint(30, 365))).date(),
                'status': random.choice(['normal', 'quase_cheia', 'cheia']),
                'descricao_residuo': f"Resíduo {random.choice(['oleoso', 'químico', 'industrial'])} tipo {i+1}",
                'temperatura': round(random.uniform(15, 35), 2),
                'is_active': True
            }
            
            bombona, created = Bombona.objects.get_or_create(
                identificacao=identificacao,
                defaults=bombona_data
            )
            
            if created:
                created_bombonas.append(bombona)
                print(f"✓ Bombona criada: {bombona.identificacao} - {bombona.empresa.nome}")
            else:
                print(f"• Bombona já existe: {bombona.identificacao}")
    
    return created_bombonas

def create_coletas(bombonas):
    """Criar registros de coleta"""
    created_coletas = []
    
    # Pegar um usuário operador para as coletas
    operador = User.objects.filter(tipo_usuario='operador').first()
    
    for bombona in bombonas:
        # Cada bombona terá entre 2 e 8 coletas históricas
        num_coletas = random.randint(2, 8)
        
        for i in range(num_coletas):
            data_coleta = datetime.now() - timedelta(days=random.randint(1, 180))
            peso_coletado = round(random.uniform(bombona.capacidade * 0.3, bombona.capacidade * 0.9), 2)
            
            coleta_data = {
                'bombona': bombona,
                'operador': operador,
                'data_coleta': data_coleta,
                'peso_coletado': peso_coletado,
                'destino': random.choice([
                    'Aterro Industrial São Paulo',
                    'Central de Tratamento ABC',
                    'Incinerador Industrial XYZ',
                    'Recicladora Verde Ltda'
                ]),
                'empresa_destino': random.choice([
                    'EcoTech Soluções Ambientais',
                    'Verde Reciclagem Ltda',
                    'Ambiente Limpo S.A.',
                    'Resíduo Zero Ind. e Com.'
                ]),
                'observacoes': random.choice([
                    'Coleta realizada sem intercorrências',
                    'Bombona com nível alto, coleta urgente',
                    'Manutenção preventiva realizada',
                    'Acesso dificultado por obras no local',
                    'Coleta programada executada'
                ]),
                'status': 'concluida',
                'numero_manifesto': f"MAN-{random.randint(100000, 999999)}"
            }
            
            coleta = Coleta.objects.create(**coleta_data)
            created_coletas.append(coleta)
    
    print(f"✓ {len(created_coletas)} coletas criadas")
    return created_coletas

def create_alertas(bombonas):
    """Criar alertas para as bombonas"""
    tipos_alerta = [
        ('nivel_alto', 'Nível Alto'),
        ('manutencao', 'Manutenção Necessária'),
        ('sensor_offline', 'Sensor Offline'),
        ('vazamento', 'Possível Vazamento')
    ]
    
    created_alertas = []
    
    # Criar alguns alertas ativos
    bombonas_list = list(bombonas)
    print(f"Bombonas disponíveis para alertas: {len(bombonas_list)}")
    if not bombonas_list:
        # Se não há bombonas na lista, buscar no banco
        bombonas_list = list(Bombona.objects.all())
        print(f"Bombonas encontradas no banco: {len(bombonas_list)}")
    
    for bombona in random.sample(bombonas_list, min(len(bombonas_list) // 3, 20)):
        tipo, descricao = random.choice(tipos_alerta)
        
        resolvido = random.choice([True, False, False])  # 2/3 dos alertas não resolvidos
        
        alerta_data = {
            'bombona': bombona,
            'tipo': tipo,
            'nivel': random.choice(['baixo', 'medio', 'alto', 'critico']),
            'descricao': f"{descricao} detectado na bombona {bombona.identificacao}",
            'resolvido': resolvido,
            'data_resolucao': datetime.now() - timedelta(hours=random.randint(1, 24)) if resolvido else None,
            'observacoes_resolucao': 'Problema resolvido pela equipe de manutenção' if resolvido else None
        }
        
        alerta = Alerta.objects.create(**alerta_data)
        created_alertas.append(alerta)
    
    print(f"✓ {len(created_alertas)} alertas criados")
    return created_alertas

def main():
    """Executar população do banco de dados"""
    print("🚀 Iniciando população do banco de dados...")
    print("=" * 50)
    
    # Criar usuários
    print("\n📥 Criando usuários...")
    users = create_users()
    
    # Criar empresas
    print("\n🏢 Criando empresas...")
    empresas = create_empresas()
    print(f"Total de empresas disponíveis: {len(empresas)}")
    if not empresas:
        # Se não foram criadas, buscar as existentes
        from apps.empresas.models import Empresa
        empresas = list(Empresa.objects.all())
        print(f"Empresas encontradas no banco: {len(empresas)}")
    
    # Criar bombonas
    print("\n🛢️  Criando bombonas...")
    bombonas = create_bombonas(empresas)
    
    # Criar coletas
    print("\n🚛 Criando coletas...")
    coletas = create_coletas(bombonas)
    
    # Criar alertas
    print("\n⚠️  Criando alertas...")
    alertas = create_alertas(bombonas)
    
    print("\n" + "=" * 50)
    print("✅ População do banco de dados concluída!")
    print(f"👥 {User.objects.count()} usuários")
    print(f"🏢 {Empresa.objects.count()} empresas")
    print(f"🛢️  {Bombona.objects.count()} bombonas")
    print(f"🚛 {Coleta.objects.count()} coletas")
    print(f"⚠️  {Alerta.objects.count()} alertas")
    print("=" * 50)

if __name__ == "__main__":
    main()