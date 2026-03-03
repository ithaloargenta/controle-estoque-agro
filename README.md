# 🌾 Sistema de Controle de Estoque

> API REST para controle de estoque interno desenvolvida com Clean Architecture, FastAPI e PostgreSQL. Pensada para pequenos e médios negócios que precisam de rastreabilidade de estoque com baixo custo operacional.

---

## 📋 Índice

- [🌾 Sistema de Controle de Estoque](#-sistema-de-controle-de-estoque)
  - [📋 Índice](#-índice)
  - [Sobre o projeto](#sobre-o-projeto)
  - [Para quais negócios serve](#para-quais-negócios-serve)
  - [Funcionalidades](#funcionalidades)
  - [Relatórios](#relatórios)
    - [Operacionais — uso diário e semanal](#operacionais--uso-diário-e-semanal)
    - [Gerenciais — uso mensal](#gerenciais--uso-mensal)
    - [Estratégicos — uso trimestral](#estratégicos--uso-trimestral)
  - [Tecnologias e por que cada uma foi escolhida](#tecnologias-e-por-que-cada-uma-foi-escolhida)
    - [Python 3.13](#python-313)
    - [FastAPI](#fastapi)
    - [PostgreSQL 16](#postgresql-16)
    - [SQLAlchemy 2.0](#sqlalchemy-20)
    - [Alembic](#alembic)
    - [Docker e Docker Compose](#docker-e-docker-compose)
    - [JWT (JSON Web Token)](#jwt-json-web-token)
    - [bcrypt](#bcrypt)
    - [pytest](#pytest)
  - [Arquitetura](#arquitetura)
    - [Estrutura de pastas](#estrutura-de-pastas)
  - [Modelagem do banco de dados](#modelagem-do-banco-de-dados)
  - [Como rodar localmente](#como-rodar-localmente)
  - [Endpoints da API](#endpoints-da-api)
  - [Testes](#testes)
  - [Variáveis de ambiente](#variáveis-de-ambiente)
  - [Próximos passos](#próximos-passos)
  - [Autor](#autor)

---

## Sobre o projeto

Este sistema nasceu de uma necessidade real: uma empresa agropecuária familiar precisava controlar seu estoque de forma simples, rastreável e sem depender de planilhas ou sistemas caros.

O objetivo foi construir uma solução interna que:

- Mantivesse o histórico completo de todas as movimentações de estoque
- Nunca permitisse saldo negativo
- Importasse automaticamente notas fiscais de entrada via XML de NF-e
- Controlasse produtos com validade (como medicamentos veterinários) separadamente dos demais
- Funcionasse com múltiplas localizações físicas (loja, galpão, depósito)
- Alertasse automaticamente sobre produtos abaixo do estoque mínimo, com base no NCM do produto
- Fornecesse relatórios operacionais, gerenciais e estratégicos para tomada de decisão

Além de resolver o problema prático, o projeto foi desenvolvido com foco em aprendizado de arquitetura de software — aplicando Clean Architecture em um contexto real, com decisões técnicas justificadas e documentadas.

---

## Para quais negócios serve

Embora desenvolvido para uma agropecuária, a arquitetura do sistema é genérica o suficiente para atender qualquer negócio que precise controlar estoque físico com rastreabilidade. Com pequenas adaptações, serve para:

**Comércio em geral**
Lojas de material de construção, ferragens, pet shops, farmácias, mercados e qualquer varejo que precise registrar entradas de mercadoria via NF-e e baixar o estoque após as vendas.

**Distribuidoras e atacadistas**
Empresas que trabalham com múltiplos fornecedores e precisam rastrear o histórico de preços de custo por fornecedor ao longo do tempo.

**Indústria e manufatura**
Controle de matérias-primas com validade, como produtos químicos, alimentícios ou farmacêuticos. O sistema suporta controle por lote/validade nativamente.

**Clínicas e consultórios veterinários ou de saúde**
Controle de medicamentos e insumos com validade obrigatória, com rastreabilidade de quem fez cada movimentação e quando.

**Restaurantes e cozinhas industriais**
Controle de insumos perecíveis com validade, com alertas de vencimento próximo.

**Cooperativas agrícolas**
Controle de insumos (sementes, fertilizantes, defensivos) distribuídos entre múltiplos pontos físicos.

O que torna o sistema adaptável é a separação entre **catálogo de produtos** e **estoque** — o produto é um conceito genérico, e o estoque é a quantidade disponível em cada localização com cada validade. Essa modelagem funciona para qualquer tipo de item físico.

---

## Funcionalidades

**Gestão de produtos**
- Cadastro de produtos com descrição, NCM, unidade comercial e flag de controle de validade
- Estoque mínimo calculado automaticamente pelo NCM do produto — medicamentos recebem mínimo 5, ferramentas recebem mínimo 2, equipamentos recebem mínimo 1, e assim por diante
- Tabela de regras por NCM com 58 categorias mapeadas, editável via API
- Produtos com `requer_validade=true` só aceitam movimentações com data de validade informada
- Produtos podem ser desativados sem perda de histórico

**Gestão de fornecedores**
- Cadastro de fornecedores com CNPJ validado
- Relacionamento N:N entre produtos e fornecedores com código do produto por fornecedor

**Controle de estoque**
- Estoque separado por produto + localização + validade
- Saldo nunca pode ser negativo — rejeitado tanto na aplicação quanto no banco de dados
- Toda alteração de estoque passa obrigatoriamente por uma movimentação — nunca edição direta

**Movimentações**
- `ENTRADA` — compra de mercadoria
- `SAIDA` — venda ou consumo
- `AJUSTE_ENTRADA` — correção positiva (inventário)
- `AJUSTE_SAIDA` — correção negativa (perda, vencimento, quebra)
- Ajustes exigem motivo obrigatório para rastreabilidade
- Registro de valor unitário para histórico de preços de custo

**Importação de NF-e**
- Upload de XML de NF-e de entrada
- Leitura automática dos itens da nota
- Criação automática de produtos inexistentes no catálogo
- Geração automática de movimentações de entrada para cada item
- Seleção da localização de destino no momento do upload

**Autenticação**
- Login com email e senha
- Token JWT com prazo de expiração configurável
- Todas as rotas protegidas por autenticação

---

## Relatórios

O sistema possui 12 relatórios organizados em três níveis de uso:

### Operacionais — uso diário e semanal

**R01 — Lista de reposição**
Produtos cujo estoque atual está igual ou abaixo do estoque mínimo definido pelo NCM. Ordenado por maior quantidade faltante. Substitui o caderninho de anotações de reposição.

**R02 — Produtos próximos ao vencimento**
Lista produtos com validade preenchida que vencem nos próximos X dias (configurável: 30, 60 ou 90 dias). Essencial para medicamentos, vacinas e defensivos.

**R03 — Produtos vencidos**
Lista produtos que já passaram da data de validade e ainda têm estoque positivo. Permite identificar o que precisa ser baixado via ajuste.

### Gerenciais — uso mensal

**R04 — Giro por produto no período**
Soma de saídas por produto em um intervalo de datas, com comparativo automático do período anterior de mesmo tamanho e variação percentual.

**R05 — Gasto por fornecedor no período**
Soma das entradas agrupadas por fornecedor com valor total. Base para negociação de preços e prazos.

**R06 — Histórico de movimentações por período**
Todas as entradas e saídas com filtros por data, produto e tipo. Permite conferir se as baixas batem com as notas emitidas.

**R07 — Produtos sem movimentação**
Itens sem nenhuma entrada ou saída nos últimos X dias. Identifica produtos parados no estoque que podem estar ocupando espaço desnecessariamente.

**R08 — Valor total do estoque**
Soma do estoque atual multiplicado pelo último preço de custo de cada produto. Mostra o capital imobilizado em estoque por produto e o total geral.

### Estratégicos — uso trimestral

**R09 — Curva ABC por categoria NCM**
Classifica as categorias de produto pelo volume de saídas com percentual e classificação A, B ou C. Identifica onde concentrar capital de giro.

**R10 — Evolução de preço de custo por produto**
Histórico do valor unitário registrado em cada entrada de um produto ao longo do tempo, com variação percentual entre compras. Base para perceber inflação de insumos.

**R11 — Sazonalidade por categoria**
Volume de saídas agrupado por mês e categoria NCM para um ano inteiro. Identifica quais categorias vendem mais em cada época — plantio, colheita, vacinação.

**R12 — Comparativo mensal**
Compara entradas, saídas e valor de entradas entre dois meses selecionados, com variação percentual. Permite acompanhar a evolução do negócio mês a mês.

---

## Tecnologias e por que cada uma foi escolhida

### Python 3.13
Python é a linguagem mais adotada para backends modernos pela combinação de produtividade, ecossistema rico e legibilidade. A versão 3.13 traz melhorias de performance e a sintaxe moderna de type hints (`str | None` ao invés de `Optional[str]`) que torna o código mais expressivo e seguro.

### FastAPI
FastAPI foi escolhido por três razões principais. Primeiro, a geração automática de documentação interativa via `/docs` — qualquer pessoa consegue testar a API sem precisar de ferramentas externas. Segundo, a validação automática de dados via Pydantic — erros de tipo e formato são capturados antes de chegar na lógica de negócio. Terceiro, a injeção de dependências nativa — que é a peça fundamental para a Clean Architecture funcionar de forma elegante.

Comparado ao Django REST Framework, o FastAPI é mais moderno, mais performático e exige menos boilerplate para o mesmo resultado.

### PostgreSQL 16
PostgreSQL é o banco de dados open source mais robusto disponível. A escolha foi motivada por funcionalidades específicas que outros bancos não oferecem com a mesma maturidade:

- **Triggers** — usadas para atualizar o estoque automaticamente após cada movimentação, garantindo consistência mesmo se alguém inserir dados diretamente no banco
- **Partial Unique Indexes** — usados para resolver o problema de unicidade com campos nullable (validade), sem recorrer a datas sentinela fictícias
- **Expressões regulares em constraints** — usadas para validar o formato do CNPJ diretamente no banco
- **Transações ACID** — garantem que uma movimentação nunca seja registrada sem que o estoque seja atualizado, e vice-versa

### SQLAlchemy 2.0
SQLAlchemy é o ORM mais maduro do ecossistema Python. A versão 2.0 trouxe a sintaxe `Mapped[tipo]` com `mapped_column`, que usa type hints nativos do Python para declarar as colunas — tornando o código mais legível e com melhor suporte a ferramentas de análise estática como o mypy.

### Alembic
Alembic é a ferramenta padrão de migrations para SQLAlchemy. Ele mantém um histórico versionado de todas as alterações no schema do banco — cada mudança na estrutura das tabelas é registrada como um arquivo Python com métodos `upgrade()` e `downgrade()`. Isso permite evoluir o banco de forma controlada e reverter alterações quando necessário.

### Docker e Docker Compose
Docker resolve o problema clássico de "funciona na minha máquina". Com Docker, o ambiente de desenvolvimento é idêntico ao de produção — mesma versão do Python, mesma versão do PostgreSQL, mesmas variáveis de ambiente. O Docker Compose orquestra os dois containers (aplicação e banco) com um único comando.

### JWT (JSON Web Token)
JWT é o padrão de autenticação mais adotado para APIs REST. O token é gerado no login e enviado em todas as requisições subsequentes — o servidor não precisa manter sessões, o que facilita escalar horizontalmente. A biblioteca `python-jose` foi escolhida por ser a mais adotada no ecossistema FastAPI.

### bcrypt
bcrypt é o algoritmo de hash de senhas mais recomendado pela comunidade de segurança. Diferente de MD5 ou SHA, bcrypt é propositalmente lento e inclui um "salt" aleatório — o que torna ataques de força bruta e rainbow tables inviáveis na prática.

### pytest
pytest é o framework de testes mais popular do ecossistema Python. Os testes foram escritos sem dependência de banco de dados — usando repositórios falsos em memória (fakes) — o que torna a suíte de testes extremamente rápida e confiável. Essa abordagem só é possível graças à Clean Architecture, onde os casos de uso dependem de interfaces e não de implementações concretas.

---

## Arquitetura

O projeto aplica **Clean Architecture** com separação em quatro camadas. A regra fundamental é que as dependências sempre apontam para dentro — camadas externas conhecem as internas, nunca o contrário.

```
┌─────────────────────────────────────────┐
│              API (FastAPI)              │  ← Rotas, schemas Pydantic, autenticação
├─────────────────────────────────────────┤
│          Application (Use Cases)        │  ← Casos de uso, orquestração
├─────────────────────────────────────────┤
│        Infrastructure (SQLAlchemy)      │  ← Modelos, repositórios concretos, XML
├─────────────────────────────────────────┤
│              Domain (Core)              │  ← Entidades, interfaces, regras de negócio
└─────────────────────────────────────────┘
```

**Domain** — O núcleo do sistema. Entidades Python puras com regras de negócio embutidas (`Produto`, `Estoque`, `Movimentacao`). Interfaces de repositório que definem contratos sem implementação. Nenhuma dependência externa.

**Application** — Casos de uso que orquestram o domínio. Cada caso de uso representa uma ação do sistema (`CadastrarProduto`, `RegistrarMovimentacao`, `ImportarXmlNFe`, `RelatorioReposicao`). Depende apenas do domínio — nunca de banco ou framework.

**Infrastructure** — Implementações concretas dos contratos do domínio. Modelos SQLAlchemy, repositórios que falam com o PostgreSQL, parser de XML de NF-e. Depende do domínio e da aplicação.

**API** — Porta de entrada HTTP. Rotas FastAPI, schemas Pydantic para validação, injeção de dependências que cola todas as camadas. Depende de tudo, mas nenhuma outra camada depende dela.

### Estrutura de pastas

```
estoque/
├── app/
│   ├── domain/
│   │   ├── entities/          # Produto, Estoque, Movimentacao, Usuario, Fornecedor
│   │   └── repositories/      # Interfaces de repositório (contratos)
│   ├── application/
│   │   └── use_cases/         # Casos de uso e 12 relatórios
│   ├── infrastructure/
│   │   ├── database/          # Conexão, settings, Base SQLAlchemy
│   │   ├── models/            # Modelos SQLAlchemy (inclui ncm_regra)
│   │   ├── repositories/      # Implementações concretas dos repositórios
│   │   └── xml/               # Parser de XML de NF-e
│   └── api/
│       ├── routers/           # Rotas FastAPI por recurso e relatórios
│       ├── schemas/           # Schemas Pydantic de entrada e saída
│       ├── auth.py            # Funções JWT e verificação de senha
│       └── dependencies.py    # Injeção de dependências
├── alembic/                   # Migrations do banco de dados
├── tests/
│   ├── fakes/                 # Repositórios falsos para testes
│   ├── test_cadastrar_produto.py
│   ├── test_cadastrar_usuario.py
│   └── test_registrar_movimentacao.py
├── main.py
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

---

## Modelagem do banco de dados

```
produto ──────────────── produto_fornecedor ──── fornecedor
   │
   ├──────────────────── estoque
   │                    (produto + localização + validade → quantidade)
   │
   └──────────────────── movimentacao
                        (toda alteração de estoque passa por aqui)

ncm_regra
(58 categorias NCM com estoque mínimo padrão por categoria)
```

**Decisões de modelagem relevantes:**

- Produto é catálogo — não tem quantidade. Quantidade vive em `estoque`
- Estoque é identificado pela combinação `produto + localização + validade` — permitindo rastrear lotes separados do mesmo produto
- `validade` é genuinamente `NULL` para produtos sem controle de validade — dois partial unique indexes garantem unicidade correta sem datas sentinela
- Movimentação é imutável — nunca editada, apenas inserida. Uma trigger atualiza o estoque automaticamente após cada insert
- Quantidade em movimentação é sempre positiva — a direção é definida pelo tipo
- `estoque_minimo` no produto é calculado automaticamente pelo NCM via tabela `ncm_regra` no momento do cadastro, podendo ser sobrescrito manualmente

---

## Como rodar localmente

**Pré-requisitos:** [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) instalados.

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/estoque.git
cd estoque

# 2. Crie o arquivo de variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# 3. Suba os containers
docker-compose up -d

# 4. Rode as migrations
docker-compose exec app alembic upgrade head
```

Acesse a documentação interativa em **http://localhost:8000/docs**.

**Fluxo básico de uso:**

1. Cadastre um usuário em `POST /usuarios/`
2. Faça login em `POST /auth/login` e copie o token
3. Clique em **Authorize** no `/docs` e cole o token
4. Importe uma NF-e em `POST /importacao/nfe` ou cadastre produtos manualmente
5. Registre movimentações em `POST /movimentacoes/`
6. Consulte o estoque em `GET /estoque/enriquecido`
7. Acesse os relatórios em `GET /relatorios/`

---

## Endpoints da API

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/auth/login` | Login e geração de token JWT | ❌ |
| POST | `/usuarios/` | Cadastro de usuário | ❌ |
| POST | `/produtos/` | Cadastro de produto | ✅ |
| POST | `/fornecedores/` | Cadastro de fornecedor | ✅ |
| POST | `/movimentacoes/` | Registro de movimentação | ✅ |
| GET | `/estoque/` | Consulta de estoque simples | ✅ |
| GET | `/estoque/enriquecido` | Consulta de estoque com nome do produto | ✅ |
| POST | `/importacao/nfe` | Importação de XML de NF-e | ✅ |
| GET | `/relatorios/reposicao` | Lista de reposição | ✅ |
| GET | `/relatorios/vencimento` | Produtos próximos ao vencimento | ✅ |
| GET | `/relatorios/vencidos` | Produtos vencidos | ✅ |
| GET | `/relatorios/giro` | Giro por produto no período | ✅ |
| GET | `/relatorios/gasto-fornecedor` | Gasto por fornecedor | ✅ |
| GET | `/relatorios/historico` | Histórico de movimentações | ✅ |
| GET | `/relatorios/sem-movimentacao` | Produtos sem movimentação | ✅ |
| GET | `/relatorios/valor-estoque` | Valor total do estoque | ✅ |
| GET | `/relatorios/curva-abc` | Curva ABC por categoria NCM | ✅ |
| GET | `/relatorios/preco-custo/{id}` | Evolução de preço de custo | ✅ |
| GET | `/relatorios/sazonalidade` | Sazonalidade por categoria | ✅ |
| GET | `/relatorios/comparativo-mensal` | Comparativo entre dois meses | ✅ |
| GET | `/health` | Status da aplicação | ❌ |

---

## Testes

```bash
docker-compose exec app python -m pytest tests/ -v
```

A suíte cobre 12 casos de teste sem dependência de banco de dados:

- Cadastro de produto com e sem NCM
- Geração de IDs únicos por produto
- Cadastro de usuário com verificação de email duplicado
- Verificação de que a senha nunca é salva em texto puro
- Movimentação de entrada com sucesso
- Rejeição de produto não encontrado
- Rejeição de produto inativo
- Rejeição de movimentação sem validade em produto que exige
- Rejeição de saída com saldo insuficiente
- Rejeição de ajuste sem motivo

---

## Variáveis de ambiente

Veja o arquivo `.env.example` para todas as variáveis necessárias:

```env
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=nome_do_banco
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://seu_usuario:sua_senha@db:5432/nome_do_banco

SECRET_KEY=sua_chave_secreta_longa_e_aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

---

## Próximos passos

- [ ] Interface web para uso por usuários não técnicos
- [ ] Deploy na AWS EC2 com banco gerenciado no RDS
- [ ] Backup automático do banco de dados

---

## Autor

Desenvolvido por **Íthalo** como projeto de aprendizado e uso interno.

Dúvidas ou sugestões? Abra uma issue ou entre em contato.