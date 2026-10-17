import os
import re
from . import config
import pandas as pd
from playwright.sync_api import sync_playwright


def limpar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).strip()
    texto = re.sub(r"[^\x00-\x7FÀ-ÿ]+", "", texto)
    return texto


def tratar_nacionalidade(texto):
    termos_brasil = ["brasil", "brasileiro", "brasileira", "salvador bahia brasil"]
    if texto.lower() in termos_brasil:
        return "Brasileiro"
    return texto


def tratar_estado_civil(texto):
    if texto.lower() == "solteir@":
        return "Solteiro(a)"
    return texto


def apenas_numeros(texto):
    return re.sub(r"\D", "", texto)


def preencher_e_baixar(page, dados, url, pasta_destino, nome_botao, tipo_documento):
    try:
        page.goto(url)

        page.fill('input[name="name"]', dados["nome"])
        page.fill('input[name="cpf"]', dados["cpf"])
        page.fill('input[name="role"]', dados["profissao"])
        page.fill('input[name="nationality"]', dados["nacionalidade"])
        page.fill('input[name="address"]', dados["endereco"])
        page.fill('input[name="zipCode"]', dados["cep"])

        page.click('button[role="combobox"]', timeout=3000)
        opcao_site = dados["estado_civil"].split("(")[0]
        page.get_by_role("option", name=opcao_site, exact=True).click(timeout=3000)

        page.get_by_role("button", name=nome_botao).click(timeout=3000)

        page.wait_for_selector('text="Termo gerado com sucesso !"', timeout=4000)

        with page.expect_download(timeout=4000) as download_info:
            page.get_by_role("button", name="Download").click(force=True, timeout=3000)

        download = download_info.value
        extensao = os.path.splitext(download.suggested_filename)[1]

        nome_arquivo = f"{tipo_documento}_{dados['nome'].replace(' ', '_')}{extensao}"
        caminho_final = os.path.join(pasta_destino, nome_arquivo)
        download.save_as(caminho_final)
    except Exception:
        pass


def executar_automacao(usuario, senha, tipos_termos=None):

    url_base = os.getenv("URL_BASE")

    if not url_base:
        print("[ERRO] Variável URL_BASE não foi encontrada no .env")
        return

    url_base = url_base.rstrip("/")

    if tipos_termos is None:
        tipos_termos = ["confidencialidade", "imagem"]

    config.garantir_diretorios()

    try:
        df = pd.read_csv("dados.csv", sep=None, engine="python")
        df.columns = df.columns.str.strip()
        if len(df) <= 2:
            return
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto(url_base)
        page.wait_for_selector('input[name="username"]', state="visible", timeout=15000)
        page.fill('input[name="username"]', usuario)
        page.fill('input[name="password"]', senha)
        page.get_by_role("button", name="Login").click()
        page.wait_for_selector('h1:has-text("Termo de Confidencialidade")', timeout=15000)

        for _, linha in df.iterrows():
            try:
                rua = limpar_texto(linha["Rua"])
                numero = limpar_texto(linha["Número"])
                bairro = limpar_texto(linha["Bairro"])
                cidade = limpar_texto(linha["Cidade"])
                estado = limpar_texto(linha["Estado"])

                if numero.endswith(".0"):
                    numero = numero[:-2]
                if not numero:
                    numero = "S/N"

                endereco_formatado = f"{rua}, {numero} - {bairro}, {cidade} - {estado}"

                dados_limpos = {
                    "nome": limpar_texto(linha["Nome completo (Como na identidade)"]),
                    "cpf": apenas_numeros(limpar_texto(linha["CPF"])),
                    "profissao": limpar_texto(linha["Profissão atual"]).capitalize(),
                    "nacionalidade": tratar_nacionalidade(limpar_texto(linha["Nacionalidade"])),
                    "cep": apenas_numeros(limpar_texto(linha["CEP (apenas números)"])),
                    "estado_civil": tratar_estado_civil(limpar_texto(linha["Estado Civil"])),
                    "endereco": endereco_formatado,
                }
            except KeyError as e:
                print(f"Erro de chave: {e}. Verifique as colunas do CSV.")
                break

            if "confidencialidade" in tipos_termos:
                preencher_e_baixar(
                    page,
                    dados_limpos,
                     f"{url_base}",
                    str(config.DIR_ZIPS["confidencialidade"]),
                    "Gerar Termo de Confidencialidade",
                    "confidentiality",
                )

            if "imagem" in tipos_termos:
                preencher_e_baixar(
                    page,
                    dados_limpos,
                     f"{url_base}/image",
                    str(config.DIR_ZIPS["imagem"]),
                    "Gerar Termo de Imagem",
                    "image",
                )

            if "voluntariado" in tipos_termos:
                preencher_e_baixar(
                    page,
                    dados_limpos,
                    f"{url_base}/volunteering",
                    str(config.DIR_ZIPS["voluntariado"]),
                    "Gerar Termo de Voluntariado",
                    "volunteering",
                )

        browser.close()

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    USUARIO_LOGIN = os.getenv("LOGIN_USUARIO")
    SENHA_LOGIN = os.getenv("LOGIN_SENHA")

    if not USUARIO_LOGIN or not SENHA_LOGIN:
        print("[ERRO] Variáveis LOGIN_USUARIO ou LOGIN_SENHA não foram encontradas no .env")
    else:
        executar_automacao(USUARIO_LOGIN, SENHA_LOGIN)