from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel

from app.api.dependencies import get_importar_xml_nfe, get_usuario_atual
from app.application.use_cases.importar_xml_nfe import ImportarXmlNFe, ImportarXmlNFeInput
from app.domain.entities.movimentacao import Localizacao
from app.domain.entities.usuario import Usuario
from app.infrastructure.xml.nfe_parser import parsear_xml_nfe


class ImportacaoResponse(BaseModel):
    produtos_criados: int
    produtos_existentes: int
    movimentacoes_geradas: int
    detalhes: list[str]


router = APIRouter(prefix="/importacao", tags=["Importação"])


@router.post("/nfe", response_model=ImportacaoResponse, status_code=status.HTTP_200_OK)
async def importar_nfe(
    arquivo: UploadFile = File(...),
    localizacao: Localizacao = Localizacao.LOJA,
    use_case: ImportarXmlNFe = Depends(get_importar_xml_nfe),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    if not arquivo.filename.endswith(".xml"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo deve ser um XML de NF-e.",
        )

    conteudo = await arquivo.read()

    try:
        itens = parsear_xml_nfe(conteudo)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao processar o XML. Verifique se é um XML de NF-e válido.",
        )

    if not itens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum item encontrado no XML.",
        )

    resultado = use_case.executar(
        ImportarXmlNFeInput(
            itens=itens,
            usuario_id=usuario_atual.id,
            localizacao=localizacao,
        )
    )

    return resultado