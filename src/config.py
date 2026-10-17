from pathlib import Path

# Raiz dos dados
BASE_DIR = Path("termos")

# Camada 1: ZIPs (Entrada do web scraper e modificador LaTeX)
DIR_ZIPS = {
    "confidencialidade": BASE_DIR / "01_zips" / "confidencialidade",
    "imagem": BASE_DIR / "01_zips" / "imagem",
    "voluntariado": BASE_DIR / "01_zips" / "voluntariado",
}

# Camada 2: PDFs individuais gerados pelo compilador LaTeX
DIR_INDIVIDUAIS = {
    "confidencialidade": BASE_DIR / "02_individuais" / "confidencialidade",
    "imagem": BASE_DIR / "02_individuais" / "imagem",
}

# Camada 3: PDFs finais
DIR_FINAL = {
    "imagem_confidencialidade": BASE_DIR / "final" / "confidencialidade_imagem",
    "voluntariado": BASE_DIR / "final" / "voluntariado",
}


def garantir_diretorios():
    """Cria toda a árvore de diretórios necessária."""
    todas_pastas = (
        list(DIR_ZIPS.values())
        + list(DIR_INDIVIDUAIS.values())
        + list(DIR_FINAL.values())
    )
    for pasta in todas_pastas:
        pasta.mkdir(parents=True, exist_ok=True)