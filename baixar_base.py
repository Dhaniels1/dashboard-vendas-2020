"""Baixa a planilha original disponibilizada pelo professor."""
from dados import baixar_base, CAMINHO_PADRAO

if __name__ == '__main__':
    print('Base salva em:', baixar_base(CAMINHO_PADRAO))
