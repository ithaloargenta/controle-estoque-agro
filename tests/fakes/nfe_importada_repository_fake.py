class NfeImportadaRepositoryFake:
    def __init__(self):
        self._chaves: set[str] = set()

    def ja_importada(self, chave_acesso: str) -> bool:
        return chave_acesso in self._chaves

    def registrar(self, chave_acesso: str, fornecedor_cnpj: str | None = None):
        self._chaves.add(chave_acesso)