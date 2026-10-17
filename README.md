# Automação de Geração de Termos e Documentos

Pipeline automatizado para coleta, personalização em LaTeX, compilação via Docker e unificação de termos legais.

---

## 📌 Visão Geral

O projeto automatiza o fluxo de ponta a ponta:
1. **Web Scraping:** Autentica-se em um sistema web via Playwright, preenche formulários a partir de uma planilha `dados.csv` e faz download dos pacotes compactados (`.zip`) contendo fontes LaTeX.
2. **Edição de LaTeX:** Varre os arquivos `.tex` dentro dos zips e realiza a substituição dinâmica de dados de diretoria/representantes legais (nome, CPF, RG, endereço) com base no `substituicoes.json`.
3. **Compilação Docker:** Extrai e compila os templates `.tex` em PDF utilizando a imagem Docker `blang/latex:ubuntu` (isolando dependências TeX do host).
4. **Mesclagem:** Mescla termos correspondentes (ex: Confidencialidade + Imagem) em um único arquivo PDF por pessoa.

---

## 🛠️ Tecnologias e Pré-requisitos

- **Python 3.10+**
- **Docker** (em execução para compilação TeX)
- **Playwright** (navegador Chromium)

### Principais Bibliotecas
- `playwright` (automação web)
- `pandas` (leitura e sanitização da planilha CSV)
- `python-dotenv` (carregamento de variáveis de ambiente)
- `pypdf` (concatenação e manipulação de PDFs)

---

## 📂 Estrutura do Projeto

```text
.
├── main.py                     # Ponto de entrada (CLI) da aplicação
├── substituicoes.example.json  # Modelo para substituições de termos/diretoria
├── dados_exemplo.csv           # Modelo de planilha de entrada (se aplicável)
├── .env.example                # Exemplo de variáveis de ambiente
├── src/
│   ├── config.py               # Estrutura de diretórios do pipeline
│   ├── scraper.py              # Automação Playwright para download dos .zip
│   ├── latex_editor.py         # Mecanismo de busca e substituição no LaTeX
│   ├── compiler.py             # Extração e build do PDF via Docker
│   └── merger.py               # Junção dos PDFs individuais gerados
└── termos/                     # Diretório de trabalho gerado em tempo de execução
    ├── 01_zips/                # Arquivos baixados e modificados
    ├── 02_individuais/         # PDFs compilados individualmente
    └── final/                  # PDFs mesclados finais
```

---

## ⚙️ Configuração do Ambiente

### 1. Clonar o repositório e criar o ambiente virtual

```bash
git clone <url-do-repositorio>
cd <pasta-do-repositorio>

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou: .venv\Scripts\activate  # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
playwright install chromium
```

*(Ou execute: `pip install playwright pandas python-dotenv pypdf`)*

### 3. Baixar a imagem Docker de compilação

Certifique-se de que o Docker está rodando e faça o pull da imagem:

```bash
docker pull blang/latex:ubuntu
```

### 4. Configurar variáveis de ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto:

```ini
URL_BASE=https://sistema.exemplo.com
LOGIN_USUARIO=seu_usuario
LOGIN_SENHA=sua_senha
```

### 5. Configurar dados de entrada

- **Planilha (`dados.csv`):** Coloque na raiz o arquivo `dados.csv` contendo as colunas esperadas:
  - `Nome completo (Como na identidade)`
  - `CPF`
  - `Profissão atual`
  - `Nacionalidade`
  - `CEP (apenas números)`
  - `Estado Civil`
  - `Rua`, `Número`, `Bairro`, `Cidade`, `Estado`
- **Substituições (`substituicoes.json`):** Copie o arquivo modelo e preencha com as pessoas e dados a serem atualizados nos contratos:

```bash
cp substituicoes.example.json substituicoes.json
```

---

## 🚀 Como Executar

### Modo Interativo

Execute o script principal e escolha o fluxo desejado via menu:

```bash
python main.py
```

### Modo CLI (com argumentos)

Você pode rodar diretamente o fluxo pretendido passando o parâmetro `--tipo` (ou `-t`):

- **Apenas Confidencialidade e Imagem:**
  ```bash
  python main.py --tipo conf_imagem
  ```

- **Apenas Voluntariado:**
  ```bash
  python main.py --tipo voluntariado
  ```

Os PDFs finais compilados e organizados estarão disponíveis dentro do diretório `termos/final/`.
