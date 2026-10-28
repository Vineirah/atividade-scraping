# Crawler com Parser — arXiv (Inteligência Artificial)

**Página-alvo:** https://arxiv.org/list/cs.AI/recent, listagem pública de artigos científicos de Inteligência Artificial. **Paginação:** parâmetros GET `skip` (deslocamento: 0, 20, 40...) e `show=20` (quantidade por página), avançando até obter 30 registros únicos. **Parser:** `BeautifulSoup(..., 'html.parser')`, com `select('dl')`, busca de pares diretos `dt`/`dd` e seletores `a[href^="/abs/"]`, `.list-title`, `.list-authors` e `.list-subjects`. O tratamento de elementos ausentes (`select_one()` e função `texto()`), a normalização de espaços e a deduplicação por ID ajudam a contornar HTML irregular, campos opcionais e variações de apresentação, sem depender de classes dinâmicas para a identificação do artigo.

## Objetivo

Demonstrar coleta automatizada (crawler), extração de informações (parser) e exportação estruturada de, no mínimo, 30 registros de uma fonte pública. A alternativa arXiv foi escolhida no lugar de editais públicos, conforme permitido no enunciado. Por compatibilidade com a atividade, o arquivo de saída se chama `editais_extraidos.csv`, mas seus dados são **artigos científicos**, não licitações.

## Arquivos

- `crawler_arxiv.py` — crawler completo com paginação, parser, limites de requisição, deduplicação e exportação.
- `editais_extraidos.csv` — amostra de 30 registros reais identificados na página pública do arXiv em 28/10/2026. A amostra foi montada a partir da listagem consultada; não representa uma execução do script no ambiente de criação, que não teve acesso HTTP direto ao arXiv. Executar o script atualiza o CSV com dados coletados automaticamente.
- `requirements.txt` — bibliotecas necessárias.

## Como executar

Ter Python 3.9+ instalado. No terminal, dentro da pasta do projeto:

```bash
pip install -r requirements.txt
python crawler_arxiv.py
```

O script grava um CSV separado por ponto e vírgula, em UTF-8 com BOM, legível no Excel brasileiro. Os campos são `id`, `titulo`, `autores`, `data_listagem`, `categorias` e `url`. Se houver erro de rede antes de qualquer registro, o CSV existente não é apagado. Os resultados e a data podem mudar em execuções futuras.

## Boas práticas

Somente metadados acadêmicos públicos são coletados, sem fazer download dos PDFs. A coleta é sequencial, com intervalo de 3 segundos entre páginas, limite máximo de páginas, timeout e tratamento de erros. Respeite as políticas de uso do portal e evite execuções excessivas.

**Fonte:** [arXiv — Artificial Intelligence, recent submissions](https://arxiv.org/list/cs.AI/recent).
