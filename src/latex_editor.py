import os
from pathlib import Path
import re
import shutil
import tempfile
import zipfile


def modificar_latex_no_zip(caminho_zip, substituicoes):
  temp_dir = tempfile.mkdtemp()

  try:
    with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
      zip_ref.extractall(temp_dir)

    tex_file_path = None
    for root, _, files in os.walk(temp_dir):
      for file in files:
        if file.endswith(".tex"):
          tex_file_path = os.path.join(root, file)
          break
      if tex_file_path:
        break

    if not tex_file_path:
      print(
          f"  [Aviso] Nenhum arquivo .tex encontrado em:"
          f" {os.path.basename(caminho_zip)}"
      )
      return

    with open(tex_file_path, "r", encoding="utf-8") as f:
      conteudo = f.read()

    for pessoa in substituicoes:
          nome_antigo = pessoa["nome_anterior"]
          nome_novo = pessoa["nome_atual"]
          cpf_novo = pessoa.get("cpf_atual")

          # 1. Substituição direta de RG, CEP e Endereço
          if "rg_anterior" in pessoa and "rg_atual" in pessoa:
            conteudo = conteudo.replace(pessoa["rg_anterior"], pessoa["rg_atual"])

          if "cep_anterior" in pessoa and "cep_atual" in pessoa:
            conteudo = conteudo.replace(pessoa["cep_anterior"], pessoa["cep_atual"])

          if "endereco_anterior" in pessoa and "endereco_atual" in pessoa:
            conteudo = conteudo.replace(
                pessoa["endereco_anterior"], pessoa["endereco_atual"]
            )

          indices = [
              m.start() for m in re.finditer(re.escape(nome_antigo), conteudo)
          ]

          for indice in reversed(indices):
            trecho = conteudo[indice : indice + 600]

            # --- CPF ---
            if cpf_novo:
              match_cpf = re.search(
                  r"([\d]{3}\.?\s*[\d]{3}\.?\s*[\d]{3}\s*-?\s*[\d]{2})", trecho
              )
              if match_cpf:
                inicio_cpf = indice + match_cpf.start(1)
                fim_cpf = indice + match_cpf.end(1)
                conteudo = conteudo[:inicio_cpf] + cpf_novo + conteudo[fim_cpf:]

            # --- RG (Opcional) ---
            if "rg_atual" in pessoa:
              match_rg = re.search(
                  r"(?:RG|identidade|vias?|nº)\s*([\d\.\-]{5,15})",
                  trecho,
                  re.IGNORECASE,
              )
              if match_rg:
                inicio_rg = indice + match_rg.start(1)
                fim_rg = indice + match_rg.end(1)
                conteudo = conteudo[:inicio_rg] + pessoa["rg_atual"] + conteudo[fim_rg:]

            # --- CEP (Opcional) ---
            if "cep_atual" in pessoa:
              match_cep = re.search(r"([\d]{5}\s*-?\s*[\d]{3})", trecho)
              if match_cep:
                inicio_cep = indice + match_cep.start(1)
                fim_cep = indice + match_cep.end(1)
                conteudo = (
                    conteudo[:inicio_cep] + pessoa["cep_atual"] + conteudo[fim_cep:]
                )

            # --- ENDEREÇO (Opcional) ---
            if "endereco_anterior" in pessoa and "endereco_atual" in pessoa:
              end_antigo = pessoa["endereco_anterior"]
              if end_antigo in trecho:
                inicio_end = conteudo.find(end_antigo, indice, indice + 800)
                if inicio_end != -1:
                  fim_end = inicio_end + len(end_antigo)
                  conteudo = (
                      conteudo[:inicio_end]
                      + pessoa["endereco_atual"]
                      + conteudo[fim_end:]
                  )

          # Substituição global do nome
          conteudo = conteudo.replace(nome_antigo, nome_novo)

    with open(tex_file_path, "w", encoding="utf-8") as f:
      f.write(conteudo)

    caminho_sem_extensao = os.path.splitext(caminho_zip)[0]
    shutil.make_archive(caminho_sem_extensao, "zip", temp_dir)
    print(f"  [Sucesso] Arquivo modificado: {os.path.basename(caminho_zip)}")

  finally:
    shutil.rmtree(temp_dir)


def executar_modificacao(pastas_alvo, substituicoes):
  """Recebe a lista de diretórios (Path ou str) e a lista de substituições a aplicar."""
  if not substituicoes:
    print("  [Info] Nenhuma substituição necessária para esta etapa.")
    return

  arquivos_processados = 0

  for pasta in pastas_alvo:
    pasta_path = Path(pasta)
    if not pasta_path.exists():
      continue

    print(f"Processando modificações em: {pasta_path}")
    for arquivo in pasta_path.glob("*.zip"):
      modificar_latex_no_zip(str(arquivo), substituicoes)
      arquivos_processados += 1

  print(f"Total de arquivos ZIP modificados: {arquivos_processados}")