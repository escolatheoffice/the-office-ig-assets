"""Gera app/banco.json — banco de titulos (frase do reel), legendas e hashtags da The Office.

Combina blocos escritos a mao por tema (abertura x fechamento) para chegar a 1.000 titulos
e 1.000 legendas unicos, sem custo de IA. Regras de conteudo publico respeitadas:
sem cidade, sem quantidade de aulas/horas, sem preco.

Uso: python3 templates/gen_banco.py   (reescreve app/banco.json)
Para ampliar o banco, acrescente frases nas listas abaixo e rode de novo.
"""
import json, os, itertools

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "banco.json")
N = 1000

TEMAS = {
  "trafego": {
    "nome": "Tráfego pago",
    "chaves": ["trafego", "tráfego", "anuncio", "anúncio", "ads", "campanha", "meta", "impulsionar", "verba", "cpc", "lead", "criativo"],
    "abre": ["Antes de|aumentar a verba", "Se o anúncio|não vende", "Gastou com|impulsionar?", "Seu CPC|subiu do nada?",
             "Campanha|sem resultado?", "Antes de|culpar o algoritmo", "Muito clique,|pouca venda?", "Anúncio bom|não é sorte",
             "Quer escalar|a campanha?", "Seu público|ignorou o anúncio?", "Antes de apertar|o impulsionar", "Verba pequena|pede foco",
             "Mesmo criativo|há meses?", "Lead caro|demais?"],
    "fecha": ["olha o *criativo.*", "teste antes de *escalar.*", "revise a *oferta.*", "confira o *público.*",
              "meça o que *importa.*", "a resposta tá nos *dados.*", "estratégia vem *antes.*", "ajuste a *segmentação.*",
              "confira o *pixel.*", "troque o *gancho.*", "cuide da *página.*", "aprenda a *ler métricas.*"],
    "gancho": ["Impulsionar não é estratégia.", "Seu anúncio pode estar falando com a pessoa errada.", "Clique não paga boleto. Venda paga.",
               "Antes de colocar mais dinheiro, descubra onde ele está vazando.", "O algoritmo não é seu inimigo.", "Todo criativo cansa. A pergunta é quando.",
               "Anúncio que vende começa antes do botão de publicar.", "Verba pequena bem usada rende mais que verba grande no escuro.",
               "Seu custo por lead subiu? Calma.", "Tem gente gastando com anúncio sem saber o que medir.", "Escalar campanha sem teste é aposta.",
               "O público certo vale mais que o orçamento maior."],
    "corpo": ["Tráfego pago funciona quando oferta, público e criativo conversam entre si.",
              "Antes de mexer na verba, olhe para o criativo: é ele que segura ou perde a atenção.",
              "Testar dois ou três criativos pequenos mostra o caminho antes de investir pesado.",
              "Métrica boa é a que conversa com o seu objetivo. Curtida não é venda.",
              "Quando o anúncio cansa, o custo sobe. Trocar o gancho costuma resolver mais do que trocar o público.",
              "Uma página lenta ou confusa desperdiça o clique que você pagou para conseguir.",
              "Segmentação demais trava a entrega; de menos, desperdiça. O equilíbrio vem com teste.",
              "Pixel e eventos configurados são o que permitem a plataforma aprender com as suas vendas.",
              "Antes de culpar o algoritmo, confira se a oferta está clara nos primeiros segundos.",
              "Escalar é aumentar o que já deu certo, aos poucos, olhando os números todo dia.",
              "Quem entende de métrica para de chutar e começa a decidir.",
              "Na prática, cada real investido precisa ter um motivo e um número para acompanhar.",
              "O impulsionar é o atalho mais caro que existe quando não há estratégia por trás.",
              "Criativo, público e página: se um falha, os outros dois pagam a conta."],
  },
  "sites": {
    "nome": "Sites com IA",
    "chaves": ["site", "sites", "ia", "inteligencia", "inteligência", "landing", "página", "pagina", "layout", "conversão", "conversao"],
    "abre": ["Site pronto|em minutos", "Site bonito|não basta", "Fazer site|ficou fácil", "A IA monta|o layout",
             "Seu site|não converte?", "Ninguém acha|seu site?", "Site parado|há meses?", "Ainda sem site|em 2027?",
             "Visitas|sem contato?", "Site lento|perde cliente", "Template pronto|não vende", "Site ou|cartão de visita?",
             "A IA escreve|o texto", "Landing page|em minutos"],
    "fecha": ["falta *estratégia.*", "quem vende é a *mensagem.*", "o segredo é o *CTA.*", "você decide a *estrutura.*",
              "pense no *cliente.*", "mostre a *prova.*", "um botão claro *resolve.*", "teste a *headline.*",
              "a IA faz, você *direciona.*", "cuide do *celular.*", "foco em *conversão.*", "aprenda a *usar a IA.*"],
    "gancho": ["Fazer site ficou fácil. Vender com ele, nem tanto.", "A IA monta o layout em minutos. A estratégia ainda é sua.",
               "Site bonito sem estratégia é vitrine sem porta.", "Seu site recebe visitas e ninguém chama?", "Template pronto não conhece o seu cliente.",
               "A pergunta não é se você usa IA. É como.", "Seu site abre bem no celular?", "Ter site em 2027 não é luxo.",
               "Um bom site responde a dúvida antes de o cliente perguntar.", "O primeiro segundo decide se a pessoa fica.",
               "IA acelera. Quem sabe o que pedir, chega mais longe.", "Site parado é custo. Site com estratégia é vendedor."],
    "corpo": ["Com IA dá para criar um site em minutos, mas é a estratégia que transforma visita em contato.",
              "Título claro, prova de que funciona e um botão fácil de achar: o básico que muita página esquece.",
              "A IA escreve rápido; você precisa saber revisar para soar como o seu negócio.",
              "A maioria das pessoas vai abrir seu site pelo celular. Ele precisa funcionar bem ali primeiro.",
              "Estrutura de página não é gosto pessoal: é a ordem em que o cliente precisa das informações.",
              "Depoimento, foto real e resposta às dúvidas comuns valem mais que efeito bonito.",
              "Testar duas versões do título mostra o que o seu cliente realmente quer ler.",
              "Saber usar IA é dar o comando certo, conferir o resultado e ajustar até ficar bom.",
              "Um site lento faz o cliente desistir antes de ver o que você oferece.",
              "Landing page boa tem um objetivo só e guia a pessoa até ele.",
              "Ferramenta todo mundo tem. A diferença está em quem sabe usar com intenção.",
              "Quando o site e o anúncio contam a mesma história, a conversão aparece.",
              "Site não precisa ser complicado. Precisa ser claro.",
              "A IA tira o trabalho repetitivo e deixa você focar no que vende."],
  },
  "presencial": {
    "nome": "Diferencial do presencial",
    "chaves": ["presencial", "turma", "professor", "online", "sala", "aula", "acompanhamento", "dúvida", "duvida", "pequena"],
    "abre": ["Curso online|parado no meio?", "Turma pequena|esconde menos", "Dúvida na hora|vale mais", "Professor do lado|muda tudo",
             "Mais um curso|online?", "Aprender sozinho|cansa", "Travou no|meio do módulo?", "Comprou curso|e não terminou?",
             "Vídeo gravado|não responde", "Prática|com acompanhamento", "Presencial|é outro ritmo", "Olho no olho|com o professor",
             "Sem fórum,|sem espera", "Pergunta|sem esperar resposta"],
    "fecha": ["você *aprende fazendo.*", "a dúvida some *na hora.*", "o resultado *aparece.*", "é *atenção de verdade.*",
              "faz diferença no *resultado.*", "você sai *sabendo fazer.*", "aqui é *presencial.*", "ninguém fica *pra trás.*",
              "o professor *te vê.*", "é prática, não *teoria.*", "com *turma pequena.*", "você *termina o curso.*"],
    "gancho": ["Quantos cursos online você começou e não terminou?", "Em turma pequena, ninguém se esconde no fundo da sala.",
               "Dúvida respondida na hora vale mais que dez vídeos.", "Aprender sozinho é possível. Aprender acompanhado é mais rápido.",
               "Não é mais um curso online que não ensina de verdade.", "O professor vê onde você travou antes de você pedir ajuda.",
               "Presencial tem outro ritmo: você faz, erra e corrige ali mesmo.", "Vídeo gravado não percebe quando você se perdeu.",
               "Computador aberto, professor do lado.", "A diferença está na atenção.", "Na sala, a dúvida não fica para depois.",
               "Curso bom é o que você termina."],
    "corpo": ["Na The Office as turmas são pequenas e presenciais, para o professor acompanhar cada aluno de perto.",
              "Você aprende fazendo no seu próprio computador, com alguém do lado para destravar na hora.",
              "Sem fórum e sem esperar resposta por e-mail: a dúvida aparece e é resolvida ali.",
              "Turma pequena significa atenção individual e ritmo que respeita quem está começando.",
              "Presencial cria compromisso: você vai, pratica e sai com o trabalho feito.",
              "Aqui ninguém fica para trás, porque o professor vê o que cada um está fazendo.",
              "É prática guiada do começo ao fim, não uma sequência de vídeos para assistir sozinho.",
              "Estar na sala com outras pessoas aprendendo a mesma coisa acelera o aprendizado.",
              "O erro vira aula: o professor mostra o caminho no seu projeto, não num exemplo genérico.",
              "Quem já tentou curso online sabe: o difícil não é começar, é continuar.",
              "Você sai de cada encontro sabendo fazer, não só tendo assistido.",
              "Atenção de verdade é o professor conhecer o seu projeto pelo nome.",
              "Presencial é para quem quer aprender sem ficar travado sozinho.",
              "A turma é pequena de propósito: assim dá para acompanhar cada um."],
  },
  "prova": {
    "nome": "Prova social",
    "chaves": ["aluno", "alunos", "resultado", "evolução", "evolucao", "depoimento", "prova", "conquista", "primeiro"],
    "abre": ["Evolução vem|de acompanhamento", "Aluno que|pratica", "Primeiro anúncio|no ar", "Do zero|ao primeiro site",
             "Chegou sem|saber nada", "Resultado|não é mágica", "Primeira campanha|com dados reais", "Saiu da aula|com o site pronto",
             "Começou|com dúvida", "Primeiro contato|pelo anúncio", "Aprendeu|e aplicou", "Achava difícil|até tentar",
             "Medo de errar|ficou pra trás", "Na sala|mexeu no anúncio"],
    "fecha": ["hoje *aplica sozinho.*", "é *constância.*", "virou *rotina.*", "saiu com *confiança.*",
              "é *prática guiada.*", "começou na *sala.*", "é *acompanhamento.*", "teve *orientação.*",
              "colocou em *prática.*", "entende os *números.*", "fez *acontecer.*", "não parou no *vídeo.*"],
    "gancho": ["Evolução não vem de vídeo. Vem de acompanhamento.", "Ninguém chega sabendo. Todo mundo sai fazendo.",
               "O primeiro anúncio no ar tem um gosto diferente.", "Resultado não é mágica: é prática com orientação.",
               "Quem pratica com alguém do lado aprende mais rápido.", "Achava difícil até colocar a mão na massa.",
               "Do zero ao primeiro site publicado.", "O medo de errar some quando alguém mostra o caminho.",
               "Aprender é bom. Aplicar é melhor.", "Primeira campanha, primeiros números, primeiras decisões.",
               "A confiança vem de fazer, não de assistir.", "Cada turma tem uma história de primeira vez."],
    "corpo": ["Na The Office o aluno sai de cada encontro com algo funcionando: um anúncio, uma página, uma métrica entendida.",
              "Com turma pequena o professor acompanha a evolução de cada um e ajusta o passo quando precisa.",
              "O que faz diferença é praticar no projeto real, com orientação em cada etapa.",
              "Ver o próprio anúncio no ar e entender os números muda a forma de enxergar o marketing.",
              "Constância e acompanhamento: é assim que quem começou do zero passa a aplicar sozinho.",
              "Errar faz parte. Errar com alguém do lado para corrigir é o que acelera.",
              "A primeira vitória costuma ser pequena e é ela que dá confiança para a próxima.",
              "Teoria tem em todo lugar. Prática guiada é o que transforma dúvida em habilidade.",
              "Cada aluno chega com um objetivo diferente e sai sabendo o próximo passo.",
              "Quando o conhecimento vira rotina, o resultado deixa de ser sorte.",
              "Aprender junto com outras pessoas mostra que a dúvida de um é a dúvida de todos.",
              "O professor acompanha o projeto de cada um, não só a matéria do dia.",
              "Sair da aula com o trabalho feito é o melhor jeito de não esquecer o que aprendeu.",
              "O melhor depoimento é o aluno mostrando o que construiu."],
  },
  "matricula": {
    "nome": "Matrícula / CTA",
    "chaves": ["matrícula", "matricula", "vaga", "vagas", "inscrição", "inscricao", "turma", "janeiro", "2027", "começa", "comeca"],
    "abre": ["Vaga limitada,|turma pequena", "Turma de segunda|9h às 12h", "Turma de terça|14h às 17h", "Começa|em janeiro",
             "Quer aprender|tráfego e sites?", "2027 começa|com skill nova", "Imersão|presencial", "Matrículas|abertas",
             "Última chamada|para janeiro", "Sua vaga|ainda tá aqui", "Comece o ano|sabendo vender", "Aprenda|na prática",
             "Janeiro|tá chegando", "Agenda aberta|para 2027"],
    "fecha": ["garanta sua *vaga.*", "chama no *direct.*", "turma *presencial.*", "inscrição no *link.*",
              "vagas *limitadas.*", "fale com a *gente.*", "é hora de *começar.*", "reserve seu *lugar.*",
              "vem pra *The Office.*", "começa em *janeiro.*", "aprenda *de verdade.*", "com *turma pequena.*"],
    "gancho": ["Matrículas abertas para as turmas de janeiro.", "Turma pequena, vaga limitada.", "2027 pode começar com uma habilidade nova.",
               "Tráfego pago e sites com IA, no presencial.", "Ainda dá tempo de garantir a sua vaga.", "Segunda de manhã ou terça à tarde?",
               "Começa em janeiro. A vaga é agora.", "Quer aprender de verdade, com professor do lado?", "Sua próxima habilidade começa numa sala pequena.",
               "Última chamada para quem quer começar em janeiro.", "Imersão presencial em tráfego pago e sites com IA.",
               "Comece o ano sabendo anunciar e vender online."],
    "corpo": ["Turma TH1: segunda-feira, das 9h às 12h, início em 11/01/2027.",
              "Turma TH2: terça-feira, das 14h às 17h, início em 12/01/2027.",
              "As turmas são pequenas para o professor acompanhar cada aluno de perto.",
              "Você aprende tráfego pago e criação de sites com IA na prática, no seu computador.",
              "As vagas são limitadas porque a turma é pequena de propósito.",
              "É presencial, com atenção individual e sem ser mais um curso online que não ensina de verdade.",
              "Escolha o dia que encaixa na sua rotina: segunda de manhã ou terça à tarde.",
              "Ideal para quem quer vender mais no próprio negócio ou trabalhar com marketing digital.",
              "Não precisa saber nada antes: a turma começa do básico e vai até a prática completa.",
              "Você sai sabendo criar anúncio, montar página e ler os números da campanha.",
              "Quem chega primeiro escolhe a turma.",
              "Tire suas dúvidas com a gente antes de se inscrever.",
              "Um curso para terminar, com professor do lado do começo ao fim.",
              "Matrícula simples: é só chamar e a gente explica tudo."],
  },
  "mercado": {
    "nome": "Curiosidade de mercado",
    "chaves": ["mercado", "profissão", "profissao", "renda", "freela", "empresa", "negócio", "negocio", "oportunidade", "futuro", "carreira"],
    "abre": ["Empresa local|precisa de anúncio", "Todo negócio|precisa de site", "Gestor de tráfego|é profissão", "IA não substitui|quem entende",
             "Pequena empresa|também anuncia", "Saber anunciar|virou habilidade", "Freela de site|com IA", "Toda loja|quer vender online",
             "O mercado|pede resultado", "Quem domina IA|sai na frente", "Marketing digital|em 2027", "Anúncio sem estratégia|é dinheiro jogado",
             "Seu bairro|está no Instagram", "Cliente pesquisa|antes de comprar"],
    "fecha": ["e falta *gente boa.*", "é *oportunidade.*", "pode virar *renda extra.*", "precisa de *estratégia.*",
              "valoriza quem *sabe.*", "pede *atualização.*", "é skill de *futuro.*", "começa com *prática.*",
              "abre *portas.*", "é *demanda real.*", "pede *resultado.*", "quem aprende antes *ganha.*"],
    "gancho": ["Todo negócio do seu bairro quer aparecer no Instagram.", "Saber anunciar virou habilidade de mercado.",
               "A IA não substitui quem entende de estratégia. Ela acelera.", "Cliente pesquisa antes de comprar. Seu negócio aparece?",
               "Gestor de tráfego é profissão, não bico.", "Pequena empresa também precisa de anúncio bem feito.",
               "Criar site com IA pode virar serviço.", "O mercado não paga por clique. Paga por resultado.",
               "Quem domina as ferramentas novas sai na frente.", "Marketing digital muda rápido. Quem pratica acompanha.",
               "Anúncio sem estratégia é dinheiro jogado fora.", "Muita empresa quer vender online e não sabe por onde começar."],
    "corpo": ["Muitos negócios locais querem anunciar e não têm quem cuide disso com estratégia.",
              "Saber criar anúncios e sites é útil tanto para o próprio negócio quanto para atender clientes.",
              "Com IA, um site que levava semanas pode sair em dias. Quem sabe direcionar a ferramenta ganha tempo.",
              "O que o mercado valoriza é entregar resultado mensurável, não só postar bonito.",
              "Tráfego pago e criação de sites conversam: um traz a visita, o outro transforma em contato.",
              "Antes de comprar, o cliente procura, compara e lê. Estar bem apresentado online faz diferença.",
              "Ferramentas mudam o tempo todo. A base de estratégia é o que continua valendo.",
              "Para quem quer renda extra, atender pequenos negócios com anúncios e sites é um caminho prático.",
              "Quem entende de métrica conversa melhor com o cliente e mostra o valor do trabalho.",
              "A IA tira o trabalho repetitivo e deixa mais espaço para pensar a estratégia.",
              "Começar pela prática, com orientação, encurta o caminho até o primeiro trabalho.",
              "Pequenas empresas também anunciam. Elas só precisam de alguém que saiba fazer direito.",
              "Marketing digital deixou de ser opcional para quem quer vender.",
              "Oportunidade existe para quem sabe entregar o que o cliente precisa."],
  },
}

CTAS = ["Chama no direct para saber mais.", "Comenta \"EU QUERO\" que a gente te chama.", "Salva este vídeo para não esquecer.",
        "Manda para alguém que precisa ouvir isso.", "Quer aprender na prática? Fala com a gente.", "Turma presencial com vagas limitadas: chama no direct.",
        "Segue a The Office para mais dicas assim.", "Link na bio para garantir sua vaga.", "Conta nos comentários: você já passou por isso?",
        "Garanta sua vaga na turma de janeiro."]

HASHTAGS = {
  "geral": ["#theoffice", "#marketingdigital", "#cursopresencial", "#aprendanapratica", "#empreendedorismo", "#negociolocal",
            "#marketing", "#vendasonline", "#pequenosnegocios", "#dicasdemarketing", "#carreiradigital", "#educacao"],
  "trafego": ["#trafegopago", "#gestordetrafego", "#metaads", "#facebookads", "#instagramads", "#anunciosonline", "#criativos",
              "#performance", "#leads", "#roi", "#googleads", "#campanhas"],
  "sites": ["#sitescomia", "#inteligenciaartificial", "#ia", "#criacaodesites", "#landingpage", "#webdesign", "#sitequevende",
            "#conversao", "#nocode", "#ferramentasdeia", "#chatgpt", "#copywriting"],
  "presencial": ["#cursopresencial", "#turmapequena", "#aulapresencial", "#aprendizado", "#professor", "#estudo",
                 "#educacaopresencial", "#aprenderfazendo", "#qualificacao", "#capacitacao"],
  "prova": ["#resultados", "#alunos", "#evolucao", "#depoimento", "#aprendizado", "#conquista", "#praticaguiada",
            "#primeiroanuncio", "#primeirosite", "#constancia"],
  "matricula": ["#matriculasabertas", "#vagaslimitadas", "#turma2027", "#cursodemarketing", "#inscricoesabertas",
                "#novaturma", "#janeiro2027", "#cursodetrafego", "#cursodesites", "#imersao"],
  "mercado": ["#mercadodigital", "#rendaextra", "#freelancer", "#profissaodofuturo", "#oportunidade", "#transformacaodigital",
              "#negociosdigitais", "#tendencias", "#carreira", "#empreender"],
}


def interleave(per_tema):
    """Intercala os temas (1 de cada por vez) para o corte em N ficar equilibrado."""
    out = []
    for group in itertools.zip_longest(*per_tema):
        out.extend(x for x in group if x)
    return out


def main():
    tit_by, leg_by = [], []
    for tid, t in TEMAS.items():
        tits, legs = [], []
        for i, a in enumerate(t["abre"]):
            for j, b in enumerate(t["fecha"]):
                # desloca o fechamento para variar a ordem (evita blocos repetidos lado a lado)
                tits.append((tid, f"{a}|{t['fecha'][(j + i) % len(t['fecha'])]}"))
        for i, g in enumerate(t["gancho"]):
            for j in range(len(t["corpo"])):
                c = t["corpo"][(j + i) % len(t["corpo"])]
                cta = CTAS[(i * 3 + j) % len(CTAS)]
                legs.append((tid, f"{g}\n\n{c}\n\n{cta}"))
        assert len(set(tits)) == len(tits) and len(set(legs)) == len(legs)
        tit_by.append(tits); leg_by.append(legs)

    tits = interleave(tit_by)[:N]
    legs = interleave(leg_by)[:N]
    assert len(tits) == N and len(legs) == N, (len(tits), len(legs))

    banco = {
        "versao": 1,
        "temas": {k: {"nome": v["nome"], "chaves": v["chaves"]} for k, v in TEMAS.items()},
        "hashtags": HASHTAGS,
        "titulos": [{"id": f"t{i+1:04d}", "tema": tid, "texto": s} for i, (tid, s) in enumerate(tits)],
        "legendas": [{"id": f"l{i+1:04d}", "tema": tid, "texto": s} for i, (tid, s) in enumerate(legs)],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, separators=(",", ":"))
    from collections import Counter
    print("ok:", OUT, os.path.getsize(OUT), "bytes")
    print("titulos por tema:", dict(Counter(x[0] for x in tits)))
    print("legendas por tema:", dict(Counter(x[0] for x in legs)))
    print("hashtags unicas:", len({h for v in HASHTAGS.values() for h in v}))


if __name__ == "__main__":
    main()
