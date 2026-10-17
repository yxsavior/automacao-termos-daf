import argparse
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env da raiz
load_dotenv()

# Importações dos módulos padronizados
from src import config
from src import compiler
from src import latex_editor
from src import merger
from src import scraper

USUARIO_LOGIN = os.getenv("LOGIN_USUARIO")
SENHA_LOGIN = os.getenv("LOGIN_SENHA")

def validar_arquivo_dados(caminho_dados="dados.csv", caminho_exemplo="dados_exemplo.csv") -> bool:
    caminho = Path(caminho_dados)
    
    if not caminho.exists():
        print(f"\n[ERRO] O arquivo '{caminho_dados}' não foi encontrado na raiz do projeto.")
        if Path(caminho_exemplo).exists():
            print(f"       Crie o '{caminho_dados}' com os dados reais baseado no modelo '{caminho_exemplo}'.")
        return False

    return True

def carregar_substituicoes(caminho_arquivo: str = "substituicoes.json") -> dict:
  """Lê e valida o arquivo JSON de substituições.

  Retorna um dicionário vazio caso o arquivo não exista.
  """
  caminho = Path(caminho_arquivo)
  if not caminho.exists():
    print(
        f"[AVISO] Arquivo '{caminho_arquivo}' não encontrado. Nenhuma"
        " substituição será aplicada."
    )
    return {"conf_imagem": [], "voluntariado": []}

  try:
    with open(caminho, "r", encoding="utf-8") as f:
      dados = json.load(f)
      return {
          "conf_imagem": dados.get("conf_imagem", []),
          "voluntariado": dados.get("voluntariado", []),
      }
  except json.JSONDecodeError as e:
    print(
        f"[ERRO] Falha de sintaxe no arquivo '{caminho_arquivo}' na linha"
        f" {e.lineno}: {e.msg}"
    )
    return {"conf_imagem": [], "voluntariado": []}


# Carrega as substituições estruturadas
SUBSTITUICOES = carregar_substituicoes("substituicoes.json")


def fluxo_conf_imagem():
    print("\n=== TERMOS DE CONFIDENCIALIDADE E IMAGEM ===")

    print("\n[1/4] Baixando termos do sistema web...")
    scraper.executar_automacao(
        USUARIO_LOGIN, SENHA_LOGIN, tipos_termos=["confidencialidade", "imagem"]
    )

    print("\n[2/4] Aplicando modificações nos arquivos .tex...")
    pastas_conf_imagem = [
        config.DIR_ZIPS["confidencialidade"],
        config.DIR_ZIPS["imagem"],
    ]
    latex_editor.executar_modificacao(
        pastas_conf_imagem, SUBSTITUICOES["conf_imagem"]
    )

    print("\n[3/4] Compilando .tex para PDF...")
    mapeamento_conf_imagem = [
        (config.DIR_ZIPS["confidencialidade"], config.DIR_INDIVIDUAIS["confidencialidade"]),
        (config.DIR_ZIPS["imagem"], config.DIR_INDIVIDUAIS["imagem"]),
    ]
    compiler.compilar_pastas(mapeamento_conf_imagem)

    print("\n[4/4] Mesclando PDFs...")
    merger.mesclar_termos_especificos(
        pasta_a=config.DIR_INDIVIDUAIS["confidencialidade"],
        pasta_b=config.DIR_INDIVIDUAIS["imagem"],
        prefixo_a="confidentiality",
        prefixo_b="image",
        destino=config.DIR_FINAL["imagem_confidencialidade"]
    )
    print("\nTermos de confidencialidade e imagem gerados com sucesso!")


def fluxo_voluntariado():
    print("\n=== TERMOS DE VOLUNTARIADO ===")

    print("\n[1/4] Baixando termos de voluntariado...")
    scraper.executar_automacao(
        USUARIO_LOGIN, SENHA_LOGIN, tipos_termos=["voluntariado"]
    )

    print("\n[2/4] Aplicando modificações nos arquivos .tex (voluntariado)...")
    pastas_voluntariado = [
        config.DIR_ZIPS["voluntariado"],
    ]
    latex_editor.executar_modificacao(
        pastas_voluntariado, SUBSTITUICOES["voluntariado"]
    )

    print("\n[3/4] Compilando .tex para PDF...")
    compiler.compilar_pastas([
        (config.DIR_ZIPS["voluntariado"], config.DIR_FINAL["voluntariado"])
    ])

    print("\n[4/4] Finalizando voluntariado...")
    print("Compilação de voluntariado finalizada.")


def main():
    if not USUARIO_LOGIN or not SENHA_LOGIN:
        print("[ERRO] Variáveis LOGIN_USUARIO ou LOGIN_SENHA não foram encontradas no .env")
        return

    # Validação do dados.csv antes de iniciar qualquer fluxo
    if not validar_arquivo_dados():
        return

    parser = argparse.ArgumentParser(
        description="CLI para automação de geração, modificação e compilação de termos."
    )
    parser.add_argument(
        "--tipo",
        "-t",
        choices=["conf_imagem", "voluntariado"],
        default=None,
        help="Tipo de fluxo: 'conf_imagem' (Entrada/Trainees) ou 'voluntariado' (Efetivação).",
    )

    args = parser.parse_args()
    tipo = args.tipo

    if not tipo:
        print("Escolha o momento da geração dos termos:")
        print("  1 - Entrada de Trainees (Confidencialidade + Imagem)")
        print("  2 - Efetivação de Membros (Voluntariado)")
        escolha = input("Digite a opção (1 ou 2): ").strip()

        if escolha == "1":
            tipo = "conf_imagem"
        elif escolha == "2":
            tipo = "voluntariado"
        else:
            print("Opção inválida.")
            return

    if tipo == "conf_imagem":
        fluxo_conf_imagem()
    elif tipo == "voluntariado":
        fluxo_voluntariado()


if __name__ == "__main__":
    main()