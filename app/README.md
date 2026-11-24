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
