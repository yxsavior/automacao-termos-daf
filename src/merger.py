from pathlib import Path
from pypdf import PdfWriter

def mesclar_termos_especificos(
    pasta_a: Path, pasta_b: Path, prefixo_a: str, prefixo_b: str, destino: Path
):
    destino.mkdir(parents=True, exist_ok=True)
    if not pasta_a.exists() or not pasta_b.exists():
        print(f"Pastas necessárias para mesclagem não existem.")
        return

    arquivos_a = list(pasta_a.glob(f"{prefixo_a}_*.pdf"))
    for pdf_a in arquivos_a:
        nome_pessoa = pdf_a.stem.replace(f"{prefixo_a}_", "", 1)
        pdf_b = pasta_b / f"{prefixo_b}_{nome_pessoa}.pdf"

        if not pdf_b.exists():
            print(f"[AVISO] Arquivo par não encontrado para: {nome_pessoa}")
            continue

        pdf_unificado = destino / f"{prefixo_a}_{prefixo_b}_{nome_pessoa}.pdf"

        writer = PdfWriter()
        writer.append(str(pdf_a))
        writer.append(str(pdf_b))

        with open(pdf_unificado, "wb") as f_out:
            writer.write(f_out)
        writer.close()
        print(f"[OK] Unificado: {pdf_unificado.name}")