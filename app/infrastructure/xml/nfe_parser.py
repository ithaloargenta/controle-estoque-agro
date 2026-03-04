import xml.etree.ElementTree as ET
from dataclasses import dataclass
from decimal import Decimal


NS = {"nfe": "http://www.portalfiscal.inf.br/nfe"}


@dataclass
class ItemNFe:
    descricao: str
    ncm: str
    unidade_comercial: str
    quantidade: Decimal
    valor_unitario: Decimal
    codigo_fornecedor: str | None


@dataclass
class Emitente:
    cnpj: str
    razao_social: str


@dataclass
class ResultadoParserNFe:
    emitente: Emitente | None
    itens: list[ItemNFe]


def parsear_xml_nfe(conteudo_xml: bytes) -> ResultadoParserNFe:
    root = ET.fromstring(conteudo_xml)

    # Extrai dados do emitente
    emit = root.find(".//nfe:emit", NS)
    emitente = None
    if emit is not None:
        cnpj = _texto(emit, "nfe:CNPJ")
        razao_social = _texto(emit, "nfe:xNome")
        if cnpj and razao_social:
            emitente = Emitente(
                cnpj=cnpj,
                razao_social=razao_social,
            )

    # Extrai itens da nota
    itens = []
    for det in root.findall(".//nfe:det", NS):
        prod = det.find("nfe:prod", NS)
        if prod is None:
            continue

        descricao = _texto(prod, "nfe:xProd")
        ncm = _texto(prod, "nfe:NCM")
        unidade = _texto(prod, "nfe:uCom")
        quantidade = Decimal(_texto(prod, "nfe:qCom") or "0")
        valor_unitario = Decimal(_texto(prod, "nfe:vUnCom") or "0")
        codigo_fornecedor = _texto(prod, "nfe:cProd")

        if not descricao or quantidade <= 0:
            continue

        itens.append(
            ItemNFe(
                descricao=descricao,
                ncm=ncm or "",
                unidade_comercial=unidade or "UN",
                quantidade=quantidade,
                valor_unitario=valor_unitario,
                codigo_fornecedor=codigo_fornecedor,
            )
        )

    return ResultadoParserNFe(emitente=emitente, itens=itens)


def _texto(elemento: ET.Element, tag: str) -> str | None:
    filho = elemento.find(tag, NS)
    return filho.text if filho is not None else None