from pathlib import Path
import subprocess
import tempfile
import zipfile


def compilar_com_docker(pasta_origem: Path, pasta_destino: Path):
    pasta_destino.mkdir(parents=True, exist_ok=True)
    arquivos_zip = list(pasta_origem.glob("*.zip"))

    if not arquivos_zip:
        print(f"Nenhum .zip encontrado em: {pasta_origem}")
        return

    raiz_projeto = Path.cwd().resolve()
    # Caminho absoluto da pasta de destino para montar no Docker
    dest_abs = pasta_destino.resolve()

    for zip_file in arquivos_zip:
        print(f"Processando: {zip_file.name}")
        pdf_final = pasta_destino / f"{zip_file.stem}.pdf"

        with tempfile.TemporaryDirectory(dir=raiz_projeto) as temp_dir_str:
            temp_dir = Path(temp_dir_str)

            # 1. Extrai o zip
            with zipfile.ZipFile(zip_file, "r") as z:
                z.extractall(temp_dir)

            candidatos_tex = list(temp_dir.rglob("*.tex"))
            if not candidatos_tex:
                print(f"  [AVISO] Nenhum .tex em {zip_file.name}")
                continue

            tex_file = next(
                (f for f in candidatos_tex if f.stem.lower() == "main"),
                candidatos_tex[0],
            )

            # Pasta onde o .tex e os assets (logos, background) estão
            pasta_do_tex = tex_file.parent.resolve()

            # Montamos a pasta do tex em /workdir e a pasta de destino final em /output
            # -jobname define o nome final do PDF diretamente igual ao nome do ZIP
            comando = [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{pasta_do_tex}:/workdir",
                "-v",
                f"{dest_abs}:/output",
                "-w",
                "/workdir",
                "blang/latex:ubuntu",
                "pdflatex",
                "-interaction=nonstopmode",
                f"-jobname={zip_file.stem}",
                f"-output-directory=/output",
                tex_file.name,
            ]

            subprocess.run(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Validação baseada na existência real do arquivo final gerado
            if pdf_final.exists() and pdf_final.stat().st_size > 0:
                print(f"  [OK] PDF gerado: {pdf_final}")
                # Remove arquivos auxiliares da pasta de destino
                for ext in [".aux", ".log", ".out", ".toc"]:
                    lixo = pasta_destino / f"{zip_file.stem}{ext}"
                    if lixo.exists():
                        try:
                            lixo.unlink()
                        except OSError:
                            pass
            else:
                print(f"  [ERRO] O PDF final não foi encontrado em {pdf_final}")

def compilar_pastas(mapeamento):
    for origem, destino in mapeamento:
        if Path(origem).exists():
            compilar_com_docker(Path(origem), Path(destino))
        else:
            print(f"Diretório não encontrado: {origem}")