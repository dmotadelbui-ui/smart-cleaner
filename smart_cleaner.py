import os
import shutil
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime


# ==================================================
# SMART CLEANER v1.4
# Scanner e gerenciador inteligente de arquivos
# ==================================================


# =========================
# CONFIGURAÇÕES
# =========================

PASTA_ANALISAR = Path.home() / "Downloads"

PASTA_PROJETO = Path(__file__).resolve().parent

PASTA_QUARENTENA = (
    PASTA_PROJETO / "quarantine"
)

ARQUIVO_DADOS_QUARENTENA = (
    PASTA_QUARENTENA
    / "quarantine_data.json"
)

TOP_MAIORES = 10


EXTENSOES_TEMPORARIAS = {
    ".tmp",
    ".temp",
    ".bak",
    ".old"
}


EXTENSOES_INSTALADORES = {
    ".exe",
    ".msi"
}


# Pastas e estruturas que não devem
# ser movimentadas individualmente.
PASTAS_PROTEGIDAS = {
    "visualg",
    "program files",
    "program files (x86)",
    "windows",
    "system32",
    "appdata"
}


ARQUIVOS_SISTEMA_QUARENTENA = {
    ".gitkeep",
    "quarantine_data.json"
}


# =========================
# FUNÇÕES AUXILIARES
# =========================

def formatar_tamanho(tamanho_bytes):

    tamanho = float(tamanho_bytes)

    for unidade in [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ]:

        if tamanho < 1024:

            return (
                f"{tamanho:.2f} "
                f"{unidade}"
            )

        tamanho /= 1024

    return (
        f"{tamanho:.2f} PB"
    )


def calcular_hash(caminho_arquivo):

    hash_sha256 = hashlib.sha256()

    try:

        with open(
            caminho_arquivo,
            "rb"
        ) as arquivo:

            while True:

                bloco = arquivo.read(
                    1024 * 1024
                )

                if not bloco:

                    break

                hash_sha256.update(
                    bloco
                )

        return (
            hash_sha256.hexdigest()
        )

    except (
        PermissionError,
        OSError
    ):

        return None


def esta_em_pasta_protegida(caminho):

    try:

        partes = {

            parte.lower()

            for parte
            in Path(caminho).parts

        }

        return any(

            pasta.lower()
            in partes

            for pasta
            in PASTAS_PROTEGIDAS

        )

    except (
        TypeError,
        OSError
    ):

        return False


def eh_arquivo_temporario(
    nome,
    extensao
):

    return (

        extensao
        in EXTENSOES_TEMPORARIAS

        or

        nome.startswith("~$")
    )


def eh_instalador(extensao):

    return (
        extensao
        in EXTENSOES_INSTALADORES
    )


def arquivo_pode_ser_movido(caminho):

    if not caminho.exists():

        return False, (
            "O arquivo não existe mais."
        )


    if not caminho.is_file():

        return False, (
            "O caminho informado não é um arquivo."
        )


    if esta_em_pasta_protegida(caminho):

        return False, (
            "Arquivo localizado em uma "
            "estrutura protegida."
        )


    return True, ""


# =========================
# DADOS DA QUARENTENA
# =========================

def carregar_dados_quarentena():

    PASTA_QUARENTENA.mkdir(
        exist_ok=True
    )


    if not (
        ARQUIVO_DADOS_QUARENTENA
        .exists()
    ):

        return {}


    try:

        with open(
            ARQUIVO_DADOS_QUARENTENA,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(
                arquivo
            )


        if isinstance(
            dados,
            dict
        ):

            return dados


        return {}


    except (
        json.JSONDecodeError,
        OSError
    ):

        return {}


def salvar_dados_quarentena(
    dados
):

    PASTA_QUARENTENA.mkdir(
        exist_ok=True
    )


    with open(
        ARQUIVO_DADOS_QUARENTENA,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


# =========================
# ESCANEAMENTO
# =========================

def analisar_pasta(pasta):

    arquivos = []

    temporarios = []

    instaladores = []

    hashes = defaultdict(
        list
    )


    print(
        "\n🔍 Iniciando análise..."
    )

    print(
        f"📁 Pasta: {pasta}\n"
    )


    for raiz, _, nomes_arquivos in os.walk(
        pasta
    ):

        for nome in nomes_arquivos:

            caminho = (
                Path(raiz)
                / nome
            )

            try:

                if not caminho.is_file():

                    continue


                tamanho = (
                    caminho.stat()
                    .st_size
                )

                extensao = (
                    caminho.suffix
                    .lower()
                )


                dados_arquivo = {

                    "nome":
                        nome,

                    "caminho":
                        caminho,

                    "tamanho":
                        tamanho,

                    "extensao":
                        extensao,

                    "protegido":
                        esta_em_pasta_protegida(
                            caminho
                        )
                }


                arquivos.append(
                    dados_arquivo
                )


                # =====================
                # TEMPORÁRIOS
                # =====================

                if (
                    eh_arquivo_temporario(
                        nome,
                        extensao
                    )
                ):

                    temporarios.append(
                        dados_arquivo
                    )


                # =====================
                # INSTALADORES
                # =====================

                if (
                    eh_instalador(
                        extensao
                    )
                ):

                    instaladores.append(
                        dados_arquivo
                    )


                # =====================
                # HASH
                # =====================

                hash_arquivo = (
                    calcular_hash(
                        caminho
                    )
                )


                if hash_arquivo:

                    hashes[
                        hash_arquivo
                    ].append(
                        dados_arquivo
                    )


            except (
                PermissionError,
                OSError
            ):

                print(
                    "⚠️ Não foi possível "
                    f"acessar: {caminho}"
                )


    return {

        "arquivos":
            arquivos,

        "temporarios":
            temporarios,

        "instaladores":
            instaladores,

        "hashes":
            hashes
    }


# =========================
# DUPLICADOS
# =========================

def obter_duplicados(hashes):

    duplicados = []


    for grupo in hashes.values():

        if len(grupo) <= 1:

            continue


        protegido = any(

            arquivo["protegido"]

            for arquivo
            in grupo

        )


        if protegido:

            continue


        duplicados.append(
            grupo
        )


    return duplicados


def calcular_espaco_duplicados(
    grupos
):

    espaco_total = 0


    for grupo in grupos:

        if len(grupo) <= 1:

            continue


        tamanho_arquivo = (
            grupo[0]["tamanho"]
        )


        espaco_redundante = (

            tamanho_arquivo
            * (
                len(grupo) - 1
            )

        )


        espaco_total += (
            espaco_redundante
        )


    return espaco_total


def calcular_quantidade_redundante(
    grupos
):

    quantidade = 0


    for grupo in grupos:

        quantidade += (
            len(grupo) - 1
        )


    return quantidade


# =========================
# RESUMO DA ANÁLISE
# =========================

def exibir_resumo_analise(
    dados
):

    arquivos = (
        dados["arquivos"]
    )


    temporarios = (
        dados["temporarios"]
    )


    instaladores = (
        dados["instaladores"]
    )


    duplicados = (
        obter_duplicados(
            dados["hashes"]
        )
    )


    tamanho_total = sum(

        arquivo["tamanho"]

        for arquivo
        in arquivos

    )


    tamanho_temporarios = sum(

        arquivo["tamanho"]

        for arquivo
        in temporarios

    )


    tamanho_instaladores = sum(

        arquivo["tamanho"]

        for arquivo
        in instaladores

    )


    espaco_duplicados = (
        calcular_espaco_duplicados(
            duplicados
        )
    )


    quantidade_redundante = (
        calcular_quantidade_redundante(
            duplicados
        )
    )


    maiores = (
        obter_maiores_arquivos(
            arquivos
        )
    )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "🧹 SMART CLEANER v1.4"
    )

    print(
        "📊 RELATÓRIO INTELIGENTE DE LIMPEZA"
    )

    print(
        "=" * 60
    )


    print(
        f"\n📄 Arquivos analisados: "
        f"{len(arquivos)}"
    )


    print(
        "💾 Espaço utilizado: "
        f"{formatar_tamanho(tamanho_total)}"
    )


    print(
        "\n🟢 POSSÍVEIS ARQUIVOS "
        "TEMPORÁRIOS"
    )


    print(
        f"📄 Arquivos encontrados: "
        f"{len(temporarios)}"
    )


    print(
        "💾 Espaço potencial: "
        f"{formatar_tamanho(
            tamanho_temporarios
        )}"
    )


    print(
        "\n♻️ ARQUIVOS DUPLICADOS"
    )


    print(
        f"📂 Grupos encontrados: "
        f"{len(duplicados)}"
    )


    print(
        f"📄 Arquivos redundantes: "
        f"{quantidade_redundante}"
    )


    print(
        "💾 Espaço potencial recuperável: "
        f"{formatar_tamanho(
            espaco_duplicados
        )}"
    )


    print(
        "\n🟡 INSTALADORES"
    )


    print(
        f"📄 Arquivos encontrados: "
        f"{len(instaladores)}"
    )


    print(
        "💾 Espaço ocupado: "
        f"{formatar_tamanho(
            tamanho_instaladores
        )}"
    )


    print(
        "\n🔥 TOP "
        f"{TOP_MAIORES} "
        "MAIORES ARQUIVOS"
    )


    if maiores:

        for indice, arquivo in enumerate(
            maiores,
            start=1
        ):

            print(
                f"\n{indice}. "
                f"{arquivo['nome']}"
            )

            print(
                "   💾 "
                f"{formatar_tamanho(
                    arquivo['tamanho']
                )}"
            )


    print(
        "\n"
        + "=" * 60
    )


# =========================
# EXIBIR LISTAS
# =========================

def exibir_lista(
    titulo,
    arquivos
):

    print(
        "\n"
        + "=" * 60
    )

    print(
        titulo
    )

    print(
        "=" * 60
    )


    if not arquivos:

        print(
            "\nNenhum arquivo encontrado."
        )

        return


    for indice, arquivo in enumerate(
        arquivos,
        start=1
    ):

        print(
            f"\n[{indice}] "
            f"{arquivo['nome']}"
        )

        print(
            "    💾 "
            f"{formatar_tamanho(
                arquivo["tamanho"]
            )}"
        )

        print(
            "    📁 "
            f"{arquivo["caminho"]}"
        )


        if arquivo.get(
            "protegido",
            False
        ):

            print(
                "    🛡️ Estrutura protegida"
            )


# =========================
# EXIBIR DUPLICADOS
# =========================

def exibir_duplicados(
    grupos
):

    print(
        "\n"
        + "=" * 60
    )

    print(
        "♻️ ARQUIVOS DUPLICADOS"
    )

    print(
        "=" * 60
    )


    if not grupos:

        print(
            "\nNenhum grupo de "
            "duplicados encontrado."
        )

        return


    for indice_grupo, grupo in enumerate(
        grupos,
        start=1
    ):

        tamanho = (
            grupo[0]["tamanho"]
        )


        espaco_redundante = (

            tamanho
            * (
                len(grupo) - 1
            )

        )


        print(
            f"\n📂 GRUPO "
            f"{indice_grupo}"
        )


        print(
            f"📄 Arquivos: "
            f"{len(grupo)}"
        )


        print(
            "💾 Espaço potencial "
            "recuperável: "
            f"{formatar_tamanho(
                espaco_redundante
            )}"
        )


        for arquivo in grupo:

            print(
                f"\n• {arquivo['nome']}"
            )

            print(
                "  📁 "
                f"{arquivo['caminho']}"
            )


# =========================
# MAIORES ARQUIVOS
# =========================

def obter_maiores_arquivos(
    arquivos
):

    return sorted(

        arquivos,

        key=lambda arquivo:
            arquivo["tamanho"],

        reverse=True

    )[:TOP_MAIORES]


# =========================
# SELEÇÃO DE ARQUIVOS
# =========================

def selecionar_arquivos(
    arquivos
):

    if not arquivos:

        print(
            "\nNenhum arquivo disponível."
        )

        return []


    print(
        "\nDigite os números dos "
        "arquivos que deseja mover."
    )


    print(
        "\nExemplos:"
    )


    print(
        "1,3,5  → seleciona arquivos específicos"
    )


    print(
        "1-5    → seleciona do arquivo 1 ao 5"
    )


    print(
        "todos  → seleciona todos os arquivos"
    )


    print(
        "0      → cancela a operação"
    )


    escolha = input(
        "\nSua escolha: "
    ).strip().lower()


    if escolha == "0":

        return []


    if escolha == "todos":

        return arquivos.copy()


    selecionados = []


    try:

        partes = (
            escolha.split(",")
        )


        for parte in partes:

            parte = (
                parte.strip()
            )


            if "-" in parte:

                inicio, fim = (
                    parte.split(
                        "-",
                        1
                    )
                )


                inicio = int(
                    inicio.strip()
                )


                fim = int(
                    fim.strip()
                )


                if inicio > fim:

                    inicio, fim = (
                        fim,
                        inicio
                    )


                for numero in range(
                    inicio,
                    fim + 1
                ):

                    indice = (
                        numero - 1
                    )


                    if (

                        0 <= indice
                        < len(arquivos)

                    ):

                        arquivo = (
                            arquivos[indice]
                        )


                        if (
                            arquivo
                            not in selecionados
                        ):

                            selecionados.append(
                                arquivo
                            )


                    else:

                        print(
                            "⚠️ Número inválido: "
                            f"{numero}"
                        )


            else:

                numero = int(
                    parte
                )


                indice = (
                    numero - 1
                )


                if (

                    0 <= indice
                    < len(arquivos)

                ):

                    arquivo = (
                        arquivos[indice]
                    )


                    if (
                        arquivo
                        not in selecionados
                    ):

                        selecionados.append(
                            arquivo
                        )


                else:

                    print(
                        "⚠️ Número inválido: "
                        f"{numero}"
                    )


    except ValueError:

        print(
            "\n❌ Entrada inválida."
        )

        return []


    return selecionados


# =========================
# MOVER PARA QUARENTENA
# =========================

def mover_para_quarentena(
    arquivos
):

    if not arquivos:

        print(
            "\nNenhum arquivo selecionado."
        )

        return


    arquivos_validos = []

    arquivos_bloqueados = []


    for arquivo in arquivos:

        permitido, motivo = (
            arquivo_pode_ser_movido(
                arquivo["caminho"]
            )
        )


        if permitido:

            arquivos_validos.append(
                arquivo
            )


        else:

            arquivos_bloqueados.append(
                (
                    arquivo,
                    motivo
                )
            )


    if arquivos_bloqueados:

        print(
            "\n🛡️ ARQUIVOS BLOQUEADOS"
        )


        for arquivo, motivo in (
            arquivos_bloqueados
        ):

            print(
                f"\n• {arquivo['nome']}"
            )

            print(
                f"  ⚠️ {motivo}"
            )


    if not arquivos_validos:

        print(
            "\n❌ Nenhum arquivo pode "
            "ser movido para a "
            "quarentena."
        )

        return


    print(
        "\n⚠️ CONFIRMAÇÃO"
    )


    print(
        "\nOs seguintes arquivos "
        "serão movidos para a "
        "quarentena:"
    )


    for arquivo in arquivos_validos:

        print(
            f"\n• {arquivo['nome']}"
        )

        print(
            "  💾 "
            f"{formatar_tamanho(
                arquivo["tamanho"]
            )}"
        )


    confirmacao = input(
        "\nDeseja continuar? "
        "[S/N]: "
    ).strip().lower()


    if confirmacao != "s":

        print(
            "\n❌ Operação cancelada."
        )

        return


    PASTA_QUARENTENA.mkdir(
        exist_ok=True
    )


    dados_quarentena = (
        carregar_dados_quarentena()
    )


    print(
        "\n📦 Movendo arquivos..."
    )


    for arquivo in arquivos_validos:

        try:

            caminho_origem = (
                arquivo["caminho"]
            )


            if not (
                caminho_origem.exists()
            ):

                print(
                    f"❌ Arquivo não encontrado: "
                    f"{arquivo['nome']}"
                )

                continue


            caminho_destino = (

                PASTA_QUARENTENA

                /

                caminho_origem.name

            )


            contador = 1


            while (
                caminho_destino.exists()
            ):

                caminho_destino = (

                    PASTA_QUARENTENA

                    /

                    f"{caminho_origem.stem}"
                    f"_{contador}"
                    f"{caminho_origem.suffix}"

                )


                contador += 1


            shutil.move(
                str(caminho_origem),
                str(caminho_destino)
            )


            dados_quarentena[
                caminho_destino.name
            ] = {

                "origem":
                    str(caminho_origem),

                "data":
                    datetime.now()
                    .strftime(
                        "%d/%m/%Y %H:%M:%S"
                    ),

                "tamanho":
                    arquivo["tamanho"]

            }


            print(
                f"✅ {arquivo['nome']}"
            )


        except (
            PermissionError,
            OSError
        ) as erro:

            print(
                f"❌ Erro ao mover "
                f"{arquivo['nome']}: "
                f"{erro}"
            )


    salvar_dados_quarentena(
        dados_quarentena
    )


    print(
        "\n🧹 Operação concluída."
    )


# =========================
# LISTAR QUARENTENA
# =========================

def listar_quarentena():

    dados = (
        carregar_dados_quarentena()
    )


    arquivos = []


    try:

        caminhos = sorted(
            PASTA_QUARENTENA.iterdir()
        )


    except OSError:

        print(
            "\n❌ Não foi possível "
            "acessar a quarentena."
        )

        return []


    for caminho in caminhos:

        if (
            caminho.name
            in ARQUIVOS_SISTEMA_QUARENTENA
        ):

            continue


        if caminho.is_file():

            arquivos.append(
                caminho
            )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "📦 QUARENTENA"
    )

    print(
        "=" * 60
    )


    if not arquivos:

        print(
            "\nA quarentena está vazia."
        )

        return []


    for indice, caminho in enumerate(
        arquivos,
        start=1
    ):

        print(
            f"\n[{indice}] "
            f"{caminho.name}"
        )

        print(
            "    💾 "
            f"{formatar_tamanho(
                caminho.stat().st_size
            )}"
        )


        if caminho.name in dados:

            origem = (
                dados[caminho.name]
                .get(
                    "origem",
                    "Origem desconhecida"
                )
            )


            data = (
                dados[caminho.name]
                .get(
                    "data",
                    "Data desconhecida"
                )
            )


            print(
                "    📁 Origem: "
                f"{origem}"
            )


            print(
                "    📅 Movido em: "
                f"{data}"
            )


        else:

            print(
                "    ⚠️ Informações de "
                "origem não encontradas."
            )


    return arquivos


# =========================
# RESTAURAR ARQUIVOS
# =========================

def restaurar_da_quarentena():

    arquivos = (
        listar_quarentena()
    )


    if not arquivos:

        return


    selecionados = (
        selecionar_arquivos(
            [
                {
                    "nome": arquivo.name,
                    "caminho": arquivo,
                    "tamanho":
                        arquivo.stat().st_size
                }

                for arquivo
                in arquivos
            ]
        )
    )


    if not selecionados:

        return


    dados = (
        carregar_dados_quarentena()
    )


    print(
        "\n↩️ Restaurando arquivos..."
    )


    for item in selecionados:

        arquivo = (
            item["caminho"]
        )


        try:

            if (
                arquivo.name
                not in dados
            ):

                print(
                    f"❌ Não foi possível "
                    f"identificar a origem de "
                    f"{arquivo.name}"
                )

                continue


            origem_texto = (
                dados[
                    arquivo.name
                ].get(
                    "origem"
                )
            )


            if not origem_texto:

                print(
                    f"❌ Origem inválida para "
                    f"{arquivo.name}"
                )

                continue


            destino = Path(
                origem_texto
            )


            if destino.exists():

                print(
                    f"⚠️ Já existe um arquivo "
                    f"em:"
                )

                print(
                    f"📁 {destino}"
                )

                continue


            destino.parent.mkdir(
                parents=True,
                exist_ok=True
            )


            shutil.move(
                str(arquivo),
                str(destino)
            )


            del dados[
                arquivo.name
            ]


            print(
                f"↩️ Restaurado: "
                f"{arquivo.name}"
            )


        except (
            PermissionError,
            OSError
        ) as erro:

            print(
                f"❌ Erro ao restaurar "
                f"{arquivo.name}: "
                f"{erro}"
            )


    salvar_dados_quarentena(
        dados
    )


# =========================
# EXCLUIR DA QUARENTENA
# =========================

def excluir_da_quarentena():

    arquivos = (
        listar_quarentena()
    )


    if not arquivos:

        return


    arquivos_selecao = [

        {
            "nome": arquivo.name,
            "caminho": arquivo,
            "tamanho":
                arquivo.stat().st_size
        }

        for arquivo
        in arquivos

    ]


    selecionados = (
        selecionar_arquivos(
            arquivos_selecao
        )
    )


    if not selecionados:

        return


    print(
        "\n⚠️ ATENÇÃO!"
    )


    print(
        "Os arquivos selecionados "
        "serão excluídos "
        "permanentemente."
    )


    print(
        "\nEssa ação não poderá "
        "ser desfeita."
    )


    confirmacao = input(
        "\nTem certeza que deseja "
        "EXCLUIR PERMANENTEMENTE? "
        "[S/N]: "
    ).strip().lower()


    if confirmacao != "s":

        print(
            "\n❌ Operação cancelada."
        )

        return


    dados = (
        carregar_dados_quarentena()
    )


    espaco_liberado = 0


    for item in selecionados:

        arquivo = (
            item["caminho"]
        )


        try:

            if not (
                arquivo.exists()
            ):

                print(
                    f"⚠️ Arquivo não encontrado: "
                    f"{arquivo.name}"
                )

                continue


            tamanho = (
                arquivo.stat()
                .st_size
            )


            arquivo.unlink()


            espaco_liberado += (
                tamanho
            )


            if (
                arquivo.name
                in dados
            ):

                del dados[
                    arquivo.name
                ]


            print(
                f"🗑️ Excluído: "
                f"{arquivo.name}"
            )


        except (
            PermissionError,
            OSError
        ) as erro:

            print(
                f"❌ Erro ao excluir "
                f"{arquivo.name}: "
                f"{erro}"
            )


    salvar_dados_quarentena(
        dados
    )


    print(
        "\n💾 Espaço total liberado: "
        f"{formatar_tamanho(
            espaco_liberado
        )}"
    )


# =========================
# MENU QUARENTENA
# =========================

def menu_quarentena():

    while True:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "📦 GERENCIADOR DE QUARENTENA"
        )

        print(
            "=" * 60
        )


        print(
            "\n[1] Ver arquivos"
        )

        print(
            "[2] Restaurar arquivos"
        )

        print(
            "[3] Excluir permanentemente"
        )

        print(
            "[0] Voltar"
        )


        opcao = input(
            "\nEscolha uma opção: "
        ).strip()


        if opcao == "1":

            listar_quarentena()


        elif opcao == "2":

            restaurar_da_quarentena()


        elif opcao == "3":

            excluir_da_quarentena()


        elif opcao == "0":

            break


        else:

            print(
                "\n❌ Opção inválida."
            )


# =========================
# MENU PRINCIPAL
# =========================

def menu(dados):

    while True:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "🧹 SMART CLEANER v1.4"
        )

        print(
            "=" * 60
        )


        print(
            "\n[1] Ver resumo da análise"
        )

        print(
            "[2] Ver arquivos temporários"
        )

        print(
            "[3] Ver arquivos duplicados"
        )

        print(
            "[4] Ver instaladores"
        )

        print(
            "[5] Ver maiores arquivos"
        )

        print(
            "[6] Mover arquivos "
            "para quarentena"
        )

        print(
            "[7] Gerenciar quarentena"
        )

        print(
            "[8] Atualizar análise"
        )

        print(
            "[0] Sair"
        )


        opcao = input(
            "\nEscolha uma opção: "
        ).strip()


        # =====================
        # RESUMO
        # =====================

        if opcao == "1":

            exibir_resumo_analise(
                dados
            )


        # =====================
        # TEMPORÁRIOS
        # =====================

        elif opcao == "2":

            exibir_lista(
                "🟢 ARQUIVOS TEMPORÁRIOS",
                dados["temporarios"]
            )


        # =====================
        # DUPLICADOS
        # =====================

        elif opcao == "3":

            duplicados = (
                obter_duplicados(
                    dados["hashes"]
                )
            )


            exibir_duplicados(
                duplicados
            )


        # =====================
        # INSTALADORES
        # =====================

        elif opcao == "4":

            instaladores = sorted(

                dados["instaladores"],

                key=lambda arquivo:
                    arquivo["tamanho"],

                reverse=True

            )


            exibir_lista(
                "🟡 INSTALADORES",
                instaladores
            )


        # =====================
        # MAIORES ARQUIVOS
        # =====================

        elif opcao == "5":

            maiores = (
                obter_maiores_arquivos(
                    dados["arquivos"]
                )
            )


            exibir_lista(
                "🔥 MAIORES ARQUIVOS",
                maiores
            )


        # =====================
        # MOVER PARA QUARENTENA
        # =====================

        elif opcao == "6":

            print(
                "\nEscolha uma categoria:"
            )


            print(
                "\n[1] Temporários"
            )

            print(
                "[2] Instaladores"
            )

            print(
                "[3] Maiores arquivos"
            )


            categoria = input(
                "\nEscolha: "
            ).strip()


            if categoria == "1":

                lista = (
                    dados["temporarios"]
                )


            elif categoria == "2":

                lista = sorted(

                    dados["instaladores"],

                    key=lambda arquivo:
                        arquivo["tamanho"],

                    reverse=True

                )


            elif categoria == "3":

                lista = (
                    obter_maiores_arquivos(
                        dados["arquivos"]
                    )
                )


            else:

                print(
                    "\n❌ Categoria inválida."
                )

                continue


            exibir_lista(
                "📂 ARQUIVOS DISPONÍVEIS",
                lista
            )


            selecionados = (
                selecionar_arquivos(
                    lista
                )
            )


            mover_para_quarentena(
                selecionados
            )


        # =====================
        # QUARENTENA
        # =====================

        elif opcao == "7":

            menu_quarentena()


        # =====================
        # ATUALIZAR ANÁLISE
        # =====================

        elif opcao == "8":

            dados = (
                analisar_pasta(
                    PASTA_ANALISAR
                )
            )


            print(
                "\n📊 Análise atualizada."
            )


            exibir_resumo_analise(
                dados
            )


        # =====================
        # SAIR
        # =====================

        elif opcao == "0":

            print(
                "\n👋 Encerrando "
                "Smart Cleaner."
            )

            break


        else:

            print(
                "\n❌ Opção inválida."
            )


# =========================
# EXECUÇÃO
# =========================

if __name__ == "__main__":

    if not (
        PASTA_ANALISAR.exists()
    ):

        print(
            "❌ A pasta configurada "
            "para análise não foi "
            "encontrada."
        )

        print(
            f"📁 Caminho: "
            f"{PASTA_ANALISAR}"
        )


    else:

        dados = (
            analisar_pasta(
                PASTA_ANALISAR
            )
        )


        exibir_resumo_analise(
            dados
        )


        menu(
            dados
        )
