# Reel Studio — The Office

App no navegador para criar vídeos curtos (9:16, 1080x1920) para TikTok e Reels
no padrão visual da escola, usando o gerador `templates/gen_reel.py`.

## Como usar

```bash
pip install playwright && python3 -m playwright install chromium   # uma vez
# ffmpeg também precisa estar instalado
python3 app/reel_studio.py
```

Abra http://127.0.0.1:8765 e:

1. Escreva a **frase** (`|` quebra linha, `*palavra*` fica em verde-limão e pulsa), a **tag** e o **CTA**.
2. Ajuste duração e tamanho da frase. A prévia animada atualiza na hora.
   Marque **Mostrar zona segura do TikTok** para ver o que a interface do app cobre.
3. Escreva a **legenda + hashtags** (salva em `legenda.txt`).
4. Clique em **Gerar vídeo MP4**. O vídeo fica em `reels/<pasta>/reel.mp4`,
   pronto para baixar e postar.

A lista "Vídeos gerados" mostra tudo o que já está em `reels/`.
O servidor escuta só em `127.0.0.1` por padrão; use `--host 0.0.0.0` para abrir
no celular pela mesma rede Wi-Fi.

## Versão online (sem instalar nada)

`app/reel_studio_online.html` é a mesma ferramenta rodando 100% no navegador:
a animação é desenhada num canvas e gravada em tempo real (MP4 no Chrome/Edge/Safari,
WebM no Firefox). Publicada como página privada no claude.ai:
https://claude.ai/artifact/XXb1Qa6yMe9aSXcbiLvWEc

## Banco de conteúdo (sem gastar créditos)

`app/banco.json` tem 1.000 títulos (frases no formato do reel), 1.000 legendas e 74 hashtags,
divididos em 6 temas (tráfego pago, sites com IA, diferencial do presencial, prova social,
matrícula, curiosidade de mercado). Gerado por `templates/gen_banco.py`, que combina blocos
escritos à mão. Para ampliar, acrescente frases nas listas do script e rode
`python3 templates/gen_banco.py`, depois republique a página com o novo `banco.json`.

Na página, "Buscar no banco" escolhe 3 títulos e 3 legendas do tema (detectado pela tag/descrição
ou escolhido na lista), com hashtags menos usadas. O que é confirmado fica registrado no banco de
dados da página (coleção `usos`) e deixa de aparecer no topo das buscas.

## 100 modelos de vídeo

Os vídeos mudam de roteiro, não só de estilo. São 5 estruturas:

1. **Frase com Offi**: o modelo original (frase animada, Offi, logo + CTA).
2. **Palavra gigante**: uma palavra por vez, enorme; a palavra-chave pode inverter a tela.
3. **Pergunta e resposta**: tela verde com a pergunta (todas as linhas menos a última), depois a resposta (última linha) em destaque.
4. **Dois tempos**: primeira metade em cima, uma linha verde corta a tela, a virada embaixo.
5. **Lista**: cada linha da frase vira um cartão numerado que entra um por vez.

Cada estrutura combina estilos de entrada do texto, fundo, destaque, movimento do Offi e
encerramento (a "Frase com Offi" também varia o layout). São 30 + 18 + 18 + 17 + 17 modelos;
dois modelos da mesma estrutura diferem em pelo menos 3 estilos. O Modelo 001 é o original.

Os 100 modelos ficam no banco de dados da página (coleção `modelos`, documentos `m001`…`m100`,
cópia em `app/modelos.json`). Na página, "Incluir este modelo no sorteio" tira ou devolve um
modelo do rodízio. Depois de cada vídeo o app sorteia outro modelo, de estrutura diferente,
priorizando os nunca usados (histórico na coleção `usos`). O número vai no nome do arquivo
(`...-m037.mp4`). Amostra das 5 estruturas: `app/estruturas-amostra.jpg`.
