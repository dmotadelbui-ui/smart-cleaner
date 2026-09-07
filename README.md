# Smart Cleaner

Smart Cleaner é uma ferramenta desenvolvida em Python para análise, organização e gerenciamento de arquivos.

O projeto foi criado para auxiliar na identificação de arquivos que podem estar ocupando espaço desnecessariamente, como arquivos temporários, instaladores, arquivos duplicados e arquivos de grande tamanho.

A aplicação prioriza a segurança durante o processo de limpeza, permitindo que os arquivos sejam enviados primeiro para uma área de quarentena antes de uma exclusão permanente.

---

## Funcionalidades

- Análise automática dos arquivos de uma pasta;
- Identificação de arquivos temporários;
- Detecção de arquivos duplicados utilizando hash SHA-256;
- Agrupamento de arquivos duplicados para facilitar a análise;
- Identificação de instaladores;
- Listagem dos maiores arquivos encontrados;
- Cálculo do espaço potencialmente recuperável;
- Envio seguro de arquivos para quarentena;
- Restauração de arquivos enviados para quarentena;
- Exclusão permanente de arquivos a partir da quarentena;
- Registro das informações dos arquivos enviados para quarentena;
- Sistema de confirmação antes de operações importantes;
- Seleção individual ou múltipla de arquivos;
- Opção para selecionar todos os arquivos de uma categoria;
- Proteção contra operações em determinadas estruturas consideradas sensíveis.

---

## Estrutura do Projeto

```text
project_smartcleaner/
│
├── smart_cleaner.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── quarantine/
│   └── .gitkeep
│
├── backups/
│   └── .gitkeep
│
├── reports/
│   └── .gitkeep
│
└── logs/
    └── .gitkeep
```

### Descrição das Pastas

- **quarantine/**: armazena temporariamente arquivos enviados para quarentena;
- **backups/**: destinada ao armazenamento de cópias de segurança do projeto;
- **reports/**: reservada para futuras funcionalidades relacionadas à geração de relatórios;
- **logs/**: destinada ao armazenamento de registros locais da aplicação.

Os arquivos `.gitkeep` são utilizados para manter a estrutura das pastas no repositório GitHub mesmo quando elas estiverem vazias.

---

## Tecnologias Utilizadas

O projeto foi desenvolvido utilizando Python e módulos da biblioteca padrão.

Principais módulos utilizados:

- `os`
- `shutil`
- `hashlib`
- `json`
- `pathlib`
- `datetime`
- `collections`

Atualmente, não são necessárias dependências externas para executar o projeto.

---

## Como Funciona

O Smart Cleaner realiza uma análise dos arquivos presentes na pasta configurada e organiza as informações em diferentes categorias.

Durante a análise, a aplicação pode identificar:

- Arquivos temporários;
- Arquivos duplicados;
- Instaladores;
- Arquivos de maior tamanho.

Os arquivos identificados não são excluídos automaticamente.

O usuário pode revisar os resultados e decidir quais arquivos deseja mover para a quarentena.

---

## Sistema de Quarentena

Para aumentar a segurança, os arquivos selecionados não são excluídos imediatamente.

O Smart Cleaner utiliza uma pasta de quarentena, permitindo que o usuário:

1. Mova arquivos para a quarentena;
2. Revise os arquivos armazenados;
3. Restaure arquivos para seu local de origem;
4. Exclua arquivos permanentemente apenas quando desejar.

As informações sobre a origem dos arquivos são registradas para permitir sua restauração posterior.

---

## Detecção de Arquivos Duplicados

A identificação de arquivos duplicados é realizada através do cálculo do hash SHA-256.

Arquivos com o mesmo hash possuem o mesmo conteúdo.

Os arquivos duplicados são agrupados para facilitar a análise e o programa apresenta o espaço potencialmente recuperável caso arquivos redundantes sejam removidos.

A identificação de arquivos duplicados não significa que todos os arquivos devem ser excluídos automaticamente. A decisão final permanece com o usuário.

---

## Segurança

O Smart Cleaner foi desenvolvido com foco na redução de riscos durante operações de limpeza.

Entre as medidas implementadas estão:

- Nenhum arquivo é excluído automaticamente;
- Operações importantes exigem confirmação;
- Arquivos podem ser enviados para quarentena antes da exclusão;
- Arquivos podem ser restaurados para seu local de origem;
- Informações sobre a origem dos arquivos são registradas para permitir sua restauração;
- Estruturas consideradas protegidas recebem tratamento especial;
- O usuário escolhe manualmente quais arquivos deseja processar.

Mesmo com essas medidas, recomenda-se sempre revisar os arquivos antes de movê-los ou excluí-los permanentemente.

---

## Como Executar

### 1. Clone o Repositório

```bash
git clone https://github.com/SEU-USUARIO/Smart-Cleaner.git
```

### 2. Acesse a Pasta do Projeto

```bash
cd Smart-Cleaner
```

### 3. Execute o Programa

```bash
python smart_cleaner.py
```

---

## Requisitos

- Python 3.10 ou superior.

Como o projeto utiliza apenas bibliotecas da biblioteca padrão do Python, atualmente não é necessário instalar dependências externas.

---

## Versão Atual

**Smart Cleaner v1.4**

---

## Próximas Melhorias

Algumas funcionalidades planejadas para futuras versões incluem:

- Seleção personalizada da pasta para análise;
- Organização automática de arquivos por categoria;
- Filtros por extensão;
- Filtros por data;
- Relatórios mais detalhados;
- Histórico de operações;
- Sistema de logs;
- Sugestões inteligentes de limpeza;
- Interface gráfica;
- Melhorias na análise de arquivos duplicados;
- Recursos de inteligência artificial para auxiliar na classificação de arquivos.

---

## Autor

Desenvolvido por **Daniel Mota**.

Projeto desenvolvido com o objetivo de aplicar conhecimentos em Python, automação, manipulação de arquivos e desenvolvimento de soluções voltadas à organização e análise de dados.
````
