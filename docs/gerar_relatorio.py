from pathlib import Path
from argparse import ArgumentParser
from html import escape
import textwrap

import pymupdf
from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Image


parser = ArgumentParser()
parser.add_argument('--nome', default='Não informado')
parser.add_argument('--matricula', default='Não informada')
parser.add_argument('--disciplina', default='Teste de Software (conforme README)')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
output = root / 'output/pdf'
output.mkdir(parents=True, exist_ok=True)
preview = root / 'tmp/pdfs'
preview.mkdir(parents=True, exist_ok=True)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Cover', fontSize=28, leading=34, textColor=colors.HexColor('#143b52'), alignment=TA_CENTER, spaceAfter=24))
styles['BodyText'].fontSize = 10
styles['BodyText'].leading = 15
styles['BodyText'].spaceAfter = 9
styles['Heading1'].textColor = colors.HexColor('#143b52')
styles['Code'].fontSize = 7.4
styles['Code'].leading = 10
story = []


def paragraph(text, style='BodyText'):
    story.append(Paragraph(text, styles[style]))


def code(text):
    story.append(Preformatted(text, styles['Code']))


def footer(canvas, document):
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#526674'))
    canvas.drawString(44, 28, 'Laboratório de Test Smells | UserService')
    canvas.drawRightString(550, 28, str(document.page))


story.append(Spacer(1, 100))
paragraph('Qualidade de testes<br/>Detecção e refatoração<br/>de Test Smells', 'Cover')
story.append(Spacer(1, 32))
paragraph(f'<b>Disciplina:</b> {escape(args.disciplina)}')
paragraph(f'<b>Nome completo:</b> {escape(args.nome)}')
paragraph(f'<b>Matrícula:</b> {escape(args.matricula)}')
paragraph('<b>Projeto:</b> UserService - laboratório de testes com Jest')
paragraph('<b>Repositório:</b> https://github.com/MateusRodrigu/test-smelly')
paragraph('<b>Data:</b> 18 de outubro de 2026')
story.append(PageBreak())
paragraph('1. Análise manual dos smells', 'Heading1')
paragraph('A suíte original está em <b>test/userService.smelly.test.js</b>. A execução inicial aprovou quatro testes e ignorou um. Esse resultado não garante a qualidade das verificações: há caminhos que podem passar sem avaliar o comportamento esperado.')
paragraph('Eager Test: responsabilidades misturadas', 'Heading2')
paragraph('O primeiro teste cria e busca um usuário, alternando ações e asserções. Uma falha na criação impede avaliar a busca e torna o diagnóstico menos preciso. A refatoração dedica um teste à criação e outro à consulta, usando a criação apenas como preparação neste último.')
paragraph('Conditional Test Logic: fluxo dentro do teste', 'Heading2')
paragraph('O teste de desativação usa for e if/else para tratar usuário comum e administrador. As verificações dependem do caminho executado, dificultando perceber cenários omitidos. Dois testes independentes tornam explícitos o sucesso da desativação e a proteção do administrador.')
paragraph('Teste frágil: acoplamento ao layout', 'Heading2')
paragraph('O teste de relatório exige uma linha com pontuação, ordem de campos, quebra de linha e cabeçalho exatos. Mudanças cosméticas podem provocar falhas sem regressão funcional. A nova suíte verifica nomes, IDs e estados relevantes sem exigir a apresentação completa. Essa escolha pressupõe que o layout exato não é um contrato público, coerente com o comentário do serviço.')
paragraph('Outras observações', 'Heading2')
paragraph('No teste de idade, o expect dentro de catch pode nunca executar: se a validação desaparecer, o teste passa. O novo toThrow exige o erro. O test.skip deixa o cenário vazio sem cobertura; a nova suíte verifica a mensagem do relatório vazio, pois não existe método público de listagem.')
paragraph('O banco é interno e em memória, sem evidência de Convidado Misterioso externo. Como ele é compartilhado pelo módulo, cada teste usa _clearDB() no setup. Esse acoplamento fica restrito ao mecanismo de isolamento fornecido pelo projeto.')
story.append(PageBreak())
paragraph('2. Processo de refatoração', 'Heading1')
paragraph('O cenário de desativação foi separado em dois contratos. Abaixo está o teste original completo e os dois testes que o substituem.')
original = (root / 'test/userService.smelly.test.js').read_text(encoding='utf-8')
before = original[original.index("  test('deve desativar"):original.index("  test('deve gerar")].strip()
before = '\n'.join(line for line in before.splitlines() if not line.lstrip().startswith('//'))
paragraph('Antes (comentários omitidos)', 'Heading2')
code(before)
clean = (root / 'tests/userService.clean.test.js').read_text(encoding='utf-8')
after = clean[clean.index("  test('desativa"):clean.index("  test('inclui")].strip()
paragraph('Depois', 'Heading2')
code(after)
paragraph('Cada bloco prepara um usuário, executa uma ação e verifica o resultado e o estado observável (AAA), separados por linhas em branco. Não há decisões nem repetição no fluxo do teste. A verificação do administrador também exige que ele permaneça ativo, cobrindo uma lacuna do original.')
story.append(PageBreak())
paragraph('3. Detecção automática e validação', 'Heading1')
paragraph('Foi usado ESLint 8.57.1 para executar diretamente o formato legado .eslintrc.json pedido no roteiro. A configuração habilita as regras recomendadas e as três regras explícitas. O lockfile registra as versões instaladas.')
log = (root / 'docs/eslint-inicial.txt').read_text(encoding='utf-8-sig').strip()
log = log.replace(str(root), '.').replace('\u2716', 'X')
font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18)
lines = ['$ npx eslint .'] + log.splitlines()
lines = [part for line in lines for part in (textwrap.wrap(line, 103, replace_whitespace=False, drop_whitespace=False) or [''])]
screen = PILImage.new('RGB', (1180, 38 + len(lines) * 25), '#17212b')
draw = ImageDraw.Draw(screen)
for index, line in enumerate(lines):
    draw.text((20, 15 + index * 25), line, font=font, fill='#e3eaf0')
capture = root / 'docs/eslint-inicial.png'
screen.save(capture)
story.append(Image(str(capture), width=505, height=screen.height * 505 / screen.width))
paragraph('Figura 1. Reprodução visual da saída real da primeira execução; o registro textual acompanha o projeto. Caminho absoluto abreviado e símbolo de erro normalizado para legibilidade.')
paragraph('As quatro asserções condicionais são erros; o teste ignorado e a ausência de asserções nele geram avisos. A regra de títulos idênticos não encontra duplicatas. A ferramenta detecta padrões sintáticos, mas não identifica automaticamente o Eager Test nem decide se uma comparação de relatório é frágil.')
paragraph('<b>Validação final:</b> 13 testes aprovados e 1 ignorado, em 2 suítes aprovadas. A suíte limpa passa no ESLint com --max-warnings 0. O lint global mantém os 4 erros e 2 avisos do original preservado. O registro completo está em docs/testes-finais.txt. O npm também reportou 33 vulnerabilidades nas dependências; sua atualização exige avaliação separada de compatibilidade.')
paragraph('4. Conclusão', 'Heading1')
paragraph('Testes pequenos e diretos facilitam localizar regressões. Asserções incondicionais evitam sucesso sem verificação, enquanto o isolamento reduz dependências entre casos. Análise estática fornece feedback repetível e complementa a revisão humana de intenção, cobertura e acoplamento. Passar no linter não basta para provar a qualidade de uma suíte.')
paragraph('<b>Referências:</b><br/>github.com/jest-community/eslint-plugin-jest<br/>eslint.org/docs/latest/use/configure/migration-guide')
target = output / 'relatorio-test-smells.pdf'
SimpleDocTemplate(str(target), pagesize=(595.28, 841.89), rightMargin=44, leftMargin=44, topMargin=38, bottomMargin=44).build(story, onFirstPage=footer, onLaterPages=footer)
document = pymupdf.open(target)
print(f'{target}: {len(document)} páginas')
for index, page in enumerate(document):
    page.get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(preview / f'pagina-{index + 1}.png')
